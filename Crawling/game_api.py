import requests
from bs4 import BeautifulSoup
from pprint import pprint
import pandas as pd

import DB

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
def match_meta(MATCH_NUM):
    response = requests.get(BASE_URL + '/' + MATCH_NUM, headers=headers)
    # soup = BeautifulSoup(response.content, "html.parser")

    game_meta_data = eval(response.content)
    # pprint(game_meta_data)

    return game_meta_data


# 경기 기록 데이터
# url example : https://api.kbl.or.kr/matches/S39G03N11/team-records?
def match_record(MATCH_NUM):
    response = requests.get(BASE_URL + '/' + MATCH_NUM + '/' + 'team-records', headers=headers)
    if response.status_code != 200:
        return None

    # soup = BeautifulSoup(response.content, "html.parser")
    game_record_data = eval(response.content)
    # pprint(game_record_data)
    return game_record_data


# 득점 우위 데이터
# url example : https://api.kbl.or.kr/matches/S39G03N11/leadtracks?
def match_leadtrack(MATCH_NUM):
    response = requests.get(BASE_URL + '/' + MATCH_NUM + '/' + 'leadtracks', headers=headers)
    if response.status_code != 200:
        return None

    # soup = BeautifulSoup(response.content, "html.parser")
    leadtrack_data = eval(response.content)
    pprint(leadtrack_data)

    return leadtrack_data


# 베스트 플레이어 데이터
# url example : https://api.kbl.or.kr/matches/S39G03N11/top-partplayers?
def match_topplayer(MATCH_NUM):
    response = requests.get(BASE_URL + '/' + MATCH_NUM + '/' + 'top-partplayers', headers=headers)
    if response.status_code != 200:
        return None

    # soup = BeautifulSoup(response.content, "html.parser")
    top_player_data = eval(response.content)
    pprint(top_player_data)

    return top_player_data


# 주요 선수 데이터
# url example : https://api.kbl.or.kr/matches/S39G03N11/keyplayers?
def match_keyplayer(MATCH_NUM):
    response = requests.get(BASE_URL + '/' + MATCH_NUM + '/' + 'keyplayers', headers=headers)
    if response.status_code != 200:
        return None

    # soup = BeautifulSoup(response.content, "html.parser")
    key_player_data = eval(response.content)
    pprint(key_player_data)

    return key_player_data


# 선수 스탯 데이터
# url example : https://api.kbl.or.kr/matches/S39G03N11/players-stats?
def match_playerstat(MATCH_NUM):
    response = requests.get(BASE_URL + '/' + MATCH_NUM + '/' + 'players-stats', headers=headers)
    if response.status_code != 200:
        return None

    # soup = BeautifulSoup(response.content, "html.parser")
    player_stats_data = eval(response.content)
    # pprint(player_stats_data)

    return player_stats_data


# 선수 정보 데이터
# url example : https://api.kbl.or.kr/leagues/S39G01/stats/players?tcodeList=all
def player_meta(MATCH_NUM):
    response = requests.get('https://api.kbl.or.kr/leagues/' + MATCH_NUM + '/stats/players?tcodeList=all',
                            headers=headers)
    if response.status_code != 200:
        return None

    player_meta_data = eval(response.content)
    # pprint(player_meta_data)

    return player_meta_data


# 선수 평균 기록
# url example : https://api.kbl.or.kr/leagues/S17G01/stats/players?
def player_average(MATCH_NUM):
    response = requests.get('https://api.kbl.or.kr/leagues/' + MATCH_NUM + '/stats/players?', headers=headers)

    if response.status_code != 200:
        return None

    player_average_data = eval(response.content)
    # pprint(player_average_data)

    return player_average_data


BASE_URL = 'https://api.kbl.or.kr/matches'
MATCH_NUM_FORMAT = 'S{}G{}N{}'


def game_record_toDB():
    sample = match_record(MATCH_NUM_FORMAT.format(39, '01', 1))[0]['records']
    sample['tcode'] = ''
    sample['gmkey'] = ''
    sample['home_away'] = ''
    sample['loss'] = 0
    sample = sample.keys()
    # 01 : 정규시즌 03 : 플레이오프 04: 챔피온 결정전
    # 08 : D리그 2차 13: 컵대회
    game_code = ['01', '03', '04', '08', '13']
    # game_code = ['04']
    myDB = DB.HYGPDB()
    for s in range(15, 41):
        # 홀수 정규시즌
        # 짝수 D 리그 - 2군 리그 사용할지 안할지 결정
        for g in game_code:
            df = pd.DataFrame(columns=sample)
            idx = 0
            for n in range(1, 275):
                MATCH_NUM = MATCH_NUM_FORMAT.format(s, g, n)
                meta = match_meta(MATCH_NUM)
                record = match_record(MATCH_NUM)
                # stat = match_playerstat(MATCH_NUM)
                if not record:
                    break
                home_code = meta['teams']['home']['tcode']
                away_code = meta['teams']['away']['tcode']
                home_record = record[0]['records']
                away_record = record[1]['records']

                if record[1]['tcode'] == home_code:
                    home_record, away_record = away_record, home_record
                home_record['tcode'] = home_code
                home_record['gmkey'] = MATCH_NUM
                home_record['home_away'] = 'H'
                home_record['loss'] = away_record['score']

                away_record['tcode'] = away_code
                away_record['gmkey'] = MATCH_NUM
                away_record['home_away'] = 'A'
                away_record['loss'] = home_record['score']


                # temp = dict()
                # temp['gmkey'] = MATCH_NUM
                # for key, value in home_record.items():
                #     if key == 'gmkey':
                #         continue
                #     temp['h_'+key] = value
                # for key, value in away_record.items():
                #     if key == 'gmkey':
                #         continue
                #     temp['a_'+key] = value
                # df = df.append(temp, ignore_index=True)
                df.loc[idx] = home_record
                df.loc[idx + 1] = away_record
                idx += 2
            df.to_sql(name='team_record', con=myDB.engine, if_exists='append', index=False, chunksize=1000)
        print('season ', s)
    myDB.conn.close()


def game_meta_toDB():
    columns = {'gmkey', 'gameDate', 'tcodeA', 'tcodeH', 'weekDay',
               'gameStart', 'gameEnd', 'gameCode',
               'seasonCode', 'seasonGrade', 'seasonCategoryName',
               'seasonName', 'stadiumname'}
    # 01 : 정규시즌 03 : 플레이오프 04: 챔피온 결정전
    # 08 : D리그 2차 13: 컵대회
    game_code = ['01', '03', '04', '08', '13']
    game_code = ['04']
    myDB = DB.HYGPDB()
    for s in range(39, 40):
        # 홀수 정규시즌
        # 짝수 D 리그 - 2군 리그 사용할지 안할지 결정
        for g in game_code:
            df = pd.DataFrame(columns=columns)
            idx = 0
            for n in range(1, 271):
                MATCH_NUM = MATCH_NUM_FORMAT.format(s, g, n)
                meta = match_meta(MATCH_NUM)
                # pprint(meta)

                if meta.get('code'):
                    break
                data = meta['game']
                df.loc[idx] = data
                idx += 1
            if not df.empty:
                # print(df)
                df.to_sql(name='game_meta', con=myDB.engine, if_exists='append', index=False, chunksize=1000)
        print('season ', s)
    myDB.conn.close()

def player_meta_toDB():
    myDB = DB.HYGPDB()
    myDB.set_page_DB()
    MATCH_NUM_FORMAT = 'S{}G{}'
    game_code = ['01', '08']
    columns = ['backNum', 'img', 'pcode', 'playerFlag', 'pname', 'pos', 'tcode', 'tname', 'seasonCode']

    for s in range(17, 41):
        for g in game_code:
            df = pd.DataFrame(columns=columns)
            MATCH_NUM = MATCH_NUM_FORMAT.format(s, g)
            player_meta_data = player_meta(MATCH_NUM)

            for i in range(len(player_meta_data)):
                df.loc[i] = player_meta_data[i]['player']
            df['seasonCode'] = s
            df = df.drop('tname', axis=1)
            if not df.empty:
                df.to_sql(name='player', con=myDB.engine, if_exists='append', index=False, chunksize=1000)
        print('season', s)

def player_average_record_toDB():
    myDB = DB.HYGPDB()
    MATCH_NUM_FORMAT = 'S{}G{}'
    sample = player_average(MATCH_NUM_FORMAT.format(39, '01'))[0]['records']
    sample['pcode'] = 0
    sample['tcode'] = 0
    sample['gameCnt'] = 0
    sample['startCnt'] = 0
    game_code = ['01', '03', '08', '13']

    for s in range(15, 41):
        for g in game_code:
            df = pd.DataFrame(columns=sample)
            idx = 0
            MATCH_NUM = MATCH_NUM_FORMAT.format(s, g)
            stats = player_average(MATCH_NUM)

            for stat in stats:
                data = stat['records']
                data['pcode'] = stat['player']['pcode']
                data['tcode'] = stat['player']['tcode']
                data['gameCnt'] = stat['gameCount']
                data['startCnt'] = stat['startCount']

                df.loc[idx] = data
                idx += 1

            df['seasonCode'] = MATCH_NUM
            if not df.empty:
                df.to_sql(name='player_avg_record', con=myDB.engine, if_exists='append', index=False, chunksize=1000)
        print(s)
    myDB.conn.close()

def player_total_average_record_toDB():
    myDB = DB.HYGPDB()
    MATCH_NUM_FORMAT = 'S{}G{}'
    sample = player_average(MATCH_NUM_FORMAT.format(39, '01'))[0]['records']
    sample['pcode'] = 0
    sample['tcode'] = 0
    sample['gameCnt'] = 0
    sample['startCnt'] = 0
    game_code = ['01', '03', '08', '13']

    for s in range(15, 41):
        df = pd.DataFrame(columns=sample)
        idx = 0
        players = dict()
        for g in game_code:
            MATCH_NUM = MATCH_NUM_FORMAT.format(s, g)
            stats = player_average(MATCH_NUM)

            for stat in stats:
                # print(stat)

                data = stat['records']
                data['pcode'] = stat['player']['pcode']
                players[stat['player']['pcode']] = stat['player']['tcode']
                data['gameCnt'] = stat['gameCount']
                data['startCnt'] = stat['startCount']

                df.loc[idx] = data
                idx += 1

        if not df.empty:
            df = df.groupby(['pcode'], ).sum()
            df['seasonCode'] = s
            df['pcode'] = df.index
            df['tcode'] = ''
            for pcode in df.index:
                df.loc[df.pcode == pcode, ('tcode')] = players[pcode]
            df.to_sql(name='player_total_avg_record', con=myDB.engine, if_exists='append', index=False, chunksize=1000)

            print(s)
    myDB.conn.close()

def player_record_toDB():
    myDB = DB.HYGPDB()
    sample = match_playerstat(MATCH_NUM_FORMAT.format(39, '01', 1))[0]['records']
    sample['pcode'] = 0
    sample['startFlag'] = 0
    sample['home_away'] = 0
    game_code = ['01', '03', '04', '08', '13']
    # game_code = ['13']

    for s in range(15, 17):
        for g in game_code:
            for n in range(1, 271):
                idx = 0
                df = pd.DataFrame(columns=sample)
                MATCH_NUM = MATCH_NUM_FORMAT.format(s, g, n)
                stats = match_playerstat(MATCH_NUM)

                for stat in stats:
                    data = stat['records']
                    data['pcode'] = stat['player']['pcode']
                    data['home_away'] = stat['homeAway']
                    data['startFlag'] = stat['startFlag']

                    df.loc[idx] = data
                    idx += 1
                

                df['gmkey'] = MATCH_NUM
                if not df.empty:
                    df.to_sql(name='player_record', con=myDB.engine, if_exists='append', index=False, chunksize=1000)
                    print(MATCH_NUM)
                else:
                    break
    myDB.conn.close()


# game_record_toDB()
# game_meta_toDB()
# player_record_toDB()
# player_average_record_toDB()
player_total_average_record_toDB()