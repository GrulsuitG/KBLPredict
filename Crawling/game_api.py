import requests
from bs4 import BeautifulSoup
from pprint import pprint

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'ko-KR,ko;q=0.9',
    'Access-Control-Allow-Credentials': 'true',
    'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS',
    'Access-Control-Allow-Origin': '*',
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJ3a2RjamRmeWRAbmF2ZXIuY29tIiwiaXNzIjoia2JsLWFwaS1zZXJ2ZXIiLCJjaGFubmVsIjoiV0VCIiwidG9rZW5UeXBlIjoiQUNDRVNTX1RPS0VOIiwiZXhwIjoxNjUwNTA1Njc2LCJpYXQiOjE2NTA1MDIwNzZ9.d_b4rCeP9CBf_Nm8Yo96-zxXeP1VFBq7UXZpJK7J0Vw',
    'Cache-Control': 'no-cache',
    'Channel': 'WEB',
    'Connection': 'keep-alive',
    'Origin': 'https://www.kbl.or.kr',
    'Pragma': 'no-cache',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'TeamCode': 'XX',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

# 경기 메타 데이터
# url example : https://api.kbl.or.kr/matches/S39G03N11?
BASE_URL = 'https://api.kbl.or.kr/matches'
MATCH_NUM = 'S39G03N11'

response = requests.get(BASE_URL + '/' + MATCH_NUM, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

game_meta_data = eval(response.content)
pprint(game_meta_data)

# 경기 기록 데이터
# url example : https://api.kbl.or.kr/matches/S39G03N11/team-records?

response = requests.get(BASE_URL + '/' + MATCH_NUM + '/' + 'team-records', headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

game_record_data = eval(response.content)
pprint(game_record_data)

# 득점 우위 데이터
# url example : https://api.kbl.or.kr/matches/S39G03N11/leadtracks?

response = requests.get(BASE_URL + '/' + MATCH_NUM + '/' + 'leadtracks', headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

leadtrack_data = eval(response.content)
pprint(leadtrack_data)

# 베스트 플레이어 데이터
# url example : https://api.kbl.or.kr/matches/S39G03N11/top-partplayers?

response = requests.get(BASE_URL + '/' + MATCH_NUM + '/' + 'top-partplayers', headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

top_player_data = eval(response.content)
pprint(top_player_data)

# 주요 선수 데이터
# url example : https://api.kbl.or.kr/matches/S39G03N11/keyplayers?

response = requests.get(BASE_URL + '/' + MATCH_NUM + '/' + 'keyplayers', headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

key_player_data = eval(response.content)
pprint(key_player_data)

# 선수 스탯 데이터
# url example : https://api.kbl.or.kr/matches/S39G03N11/players-stats?

response = requests.get(BASE_URL + '/' + MATCH_NUM + '/' + 'players-stats', headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

player_stats_data = eval(response.content)
pprint(player_stats_data)
