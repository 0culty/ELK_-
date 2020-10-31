import json
import pandas as pd
from datetime import datetime
from collections import defaultdict
csv_log = pd.read_csv("../source/metro_log_2019.csv") # 서울교통공사 2019년 일별 역별 시간대별 승하차인원(1_8호선)
csv_meta = pd.read_csv("../source/stations_meta.csv") # 서울교통공사 역명 다국어 표기 정보
f = open("../data/seoul-metro-2019.logs", "w") # log 파일
s_meta = defaultdict(list)

for idx, row in csv_meta.iterrows():
    stn_nm_kor = row["station_nm"].replace(' ','').replace('•','.').replace(',','.') # 공백, (,), (•) 제거 및 변환
    station_name = stn_nm_kor.split('(')[0]
    stn_nm_eng = row["stn_nm_eng"]
    stn_nm_chc = row["stn_nm_chc"]
    stn_nm_chn = row["stn_nm_chn"]
    stn_nm_jpn = row["stn_nm_jpn"]
    geo_x = row['geo_x']
    geo_y = row['geo_y']
    if not s_meta[station_name]:
        s_meta[station_name].extend([stn_nm_kor, stn_nm_eng, stn_nm_chc, stn_nm_chn, stn_nm_jpn, geo_x, geo_y])

line_num_lang = {
    "1호선" : "Line 1", "2호선" : "Line 2", "3호선" : "Line 3", "4호선" : "Line 4", 
    "5호선" : "Line 5", "6호선" : "Line 6", "7호선" : "Line 7", "8호선" : "Line 8"
    }

for i in range(0, len(csv_log), 2):
    dataIn = csv_log.loc[[i],:].values.tolist()[0]
    dataOut = csv_log.loc[[i+1],:].values.tolist()[0]
    ldateTemp = dataIn[0].split('-')
    for h in range(20):
        hour = (h+5)%24
        ldate = datetime(int(ldateTemp[0]), int(ldateTemp[1]), int(ldateTemp[2]), hour)
        station_name = dataIn[3].split('(')[0]
        # print(station_name)
        people_in = int(dataIn[5+h])
        people_out = int(dataOut[5+h])
        s_logs = {
            "@timestamp" : ldate.isoformat(),
            "code": str(dataIn[2]),
            "line_num" : dataIn[1],
            "line_num_en" : line_num_lang[dataIn[1]],
            "station": {
                "name" : s_meta[station_name][0], #full name
                "kr" : station_name,
                "en" : s_meta[station_name][1],
                "chc" : s_meta[station_name][2],
                "ch" : s_meta[station_name][3],
                "jp" : s_meta[station_name][4]
            },
            "location" : {
                "lat" : s_meta[station_name][5],
                "lon" : s_meta[station_name][6]
            },
            "people":{
                "in" : people_in,
                "out" : people_out,
                "total" : people_in+people_out
            }
        }
        jsonString = json.dumps(s_logs, ensure_ascii=False)
        f.write(jsonString+ "\n")
f.close()