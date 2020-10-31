import pandas as pd
from kakao_map_api import getGeo

df = pd.read_csv("../source/station_lang.csv") # 서울교통공사 역명 다국어 표기 정보

# 열 (연번) 제거
df = df.drop(['연번'], axis=1)
# 9호선 제거
df_line9 = df[df['호선'] == '9호선'].index
df = df.drop(df_line9)
# 칼럼 변경
df.columns = ["line_num", "station_nm", "stn_nm_chc", "stn_nm_eng", "stn_nm_chn", "stn_nm_jpn"]
# 위도, 경도 추가
lati, longi = [], []
for index, row in df.iterrows():
    station = row["station_nm"]
    lati, longi = getGeo(station)
    
df['geo_x'] = lati
df['geo_y'] = longi

df.to_csv('../source/stations_meta.csv', mode='w')