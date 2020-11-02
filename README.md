# ELK_Subway_Dashboard
------------

## 프로젝트 계획이유
> 김종민님의 'Elastic Stack을 이용한 서울시 지하철 대시보드 다시 만들기'를 따라 구현하여 ELK 실습하였습니다.  
> 출처: https://github.com/eskrug/elastic-demos/tree/master/seoul-metro-logs

## 기존의 대시보드와 다른 점
>1. 데이터는 2018년이 아닌 2019년 데이터로 진행하였습니다.
>2. javascript가 아닌 python으로 진행하였습니다.
>3. 공공데이터 '서울시 역코드로 지하철역 위치 조회'가 더이상 서울 열린데이터광장에서 제공하지 않아 지하철역 키워드를 Kakao Map Api를 통해 구현하였습니다.
>4. Logstash의 @timestamp를 사용할 때는 한국 시간의 -9시간을 하기 때문에 @timestamp 값을 통해 시간을 구할 때 +9를 하였습니다.
>5. kibana의 region map 이 더이상 지원이 되지 않아 Maps -> Clusters and girds -> cluster(show as) 를 통해 구현하였다.

## 파일 설명
> ### stations_meta.py
> '서울교통공사 지하철 역명 다국어 표기 정보'의 역명을 Kakao Map Api의 키워드을 통해 위도와 경도를 추가하여 stations_meta.csv 파일에 저장하였습니다.
> ### run.py
> '서울교통공사 2019년 일별 역별 시간대별 승하차인원(1_8호선)'와 stations_meta.csv를 합쳐 seoul-metro-2019.logs 파일에 log 데이터 생성하였습니다.
> ### seoul-metro-logs-conf
> logstash를 통해 log 데이터 저장
> ### index-settings-mappnigs.conf
> mapping
>>1. code, line_num, line_num_en 값은 keyword 로 설정
>>2. location 필드 geo_point 로 설정
>>3. people.in, people.out, people.total 값은 integer 로 설정
>>4. station.kr, station.name 에 멀티필드로 nori 애널라이저를 적용한 station.kr.nori 추가

> # 추가 mapping 사항
>>1. 시간(hour_and_week), 요일(day_of_week) 추가
```
# 1. pipeline을 통해 추가 변수 생성
PUT _ingest/pipeline/hour_and_week
{
  "description": "Add hour_of_day and day_of_week field from @timestamp"
  , "processors": [
    {
      "script": {
        "lang": "painless",
        "source": """
def ts=ctx['@timestamp'];
def sdf=new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS");
def date=sdf.parse(ts);
def cal=Calendar.getInstance();
cal.setTime(date);

ctx.hour_of_day=(cal.get(Calendar.HOUR_OF_DAY)+9)%24;
if (ctx.hour_of_day==0) {ctx.hour_of_day=24;}

def dowNum=cal.get(Calendar.DAY_OF_WEEK)-1;
def dowEn=["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][dowNum];
def dowKr=["일", "월", "화", "수", "목", "금", "토"][dowNum];

ctx.day_of_week=["num":dowNum, "en":dowEn, "kr":dowKr];
"""
      }
    }
  ]
}

# 2. pipeline을 통해 추가 변수 생성
# 자기자신을 reindex할때는 _update_by_query 이용
POST subway-logs-2019/_update_by_query?pipeline=hour_and_week&wait_for_completion=false

# *주의사항이 있는데 document양이 10만 이상이 넘어가게 되면 작업이 오래걸리기에 kibana에서 504 gateway timeout이 발생하고 작업이 중단된다. 
# 그래서 해당 작업을 비동기로 실행시키는 옵션인 wait_for_completion=false를 함께 설정해주고 진행해야한다.
# 출처: https://wedul.site/618
```


<img width="1789" alt="스크린샷 2020-11-02 오후 5 47 37" src="https://user-images.githubusercontent.com/37995679/97847883-a1cc7200-1d33-11eb-8fdb-2f03ebd678f6.png">

