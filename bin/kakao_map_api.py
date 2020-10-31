import requests

def getGeo(station):
    if not station == "서울역":
        if len(station.split('(')) > 1:
            station = station.split('(')[0]
        station += "역"
    url = 'https://dapi.kakao.com/v2/local/search/keyword.json?query={}'.format(station)
    headers = {
        "Authorization": "KakaoAK 52d7652ca9ee3128f0a11956e7cd1ae8"
    }
    places = requests.get(url, headers = headers).json()['documents']

    lati, longi = places[0]['y'], places[0]['x']
    return lati, longi