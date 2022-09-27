import numpy as np
import pandas as pd
import requests
import copy

from Crawling import DB

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

TCODE_LIST = ["06", "10", "16", "30", "35", "50", "55", "60", "64", "65", "70"]


# 라운드별 순위 데이터
def get_round_rank_data(seasonCode):
    response = requests.get("https://api.kbl.or.kr/leagues/S" + seasonCode + "G01/rank/team-tracks?", headers=headers)

    data = eval(response.content)

    return data


def insert_rank_data_to_db(seasonCode, tcode_list, tracks_arr):
    db = DB.MYDB()
    not_exist_team = set(TCODE_LIST).difference(set(tcode_list)).pop()
    idx = TCODE_LIST.index(not_exist_team)

    j = -1
    for i in range(1, 271):
        if i % 5 == 1:
            j += 1
            temp = tracks_arr[j].tolist()
            temp.insert(idx, 0)

        gmkey = "S" + seasonCode + "G01N" + str(i)
        sql = """INSERT INTO team_rank VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        value = [None, gmkey]
        value += temp
        value = tuple(value)

        db.cursor.execute(sql, value)
        print(gmkey + " is inserted!")

    db.db.commit()
    db.db.close()


def get_team_record(seasonCode):
    db = DB.MYDB()
    db.cursor.execute("""SELECT gmkey, tcode, score, loss, IF(score > loss, 1, 0) AS win FROM team_record_new WHERE gmkey LIKE 'S{}%'""".format(seasonCode))
    team_record = pd.DataFrame(db.cursor.fetchall())

    db.db.close()

    return team_record


def make_team_rank(season_win):
    temp = copy.deepcopy(season_win)
    sorted_dict = sorted(temp.items(), key=lambda item: item[1], reverse=True)

    totalRank, currentRank = 0, 0
    rank = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for i in range(0, len(sorted_dict)):
        totalRank += 1
        if sorted_dict[i][1] == sorted_dict[i - 1][1]:
            pass
        else:
            currentRank = totalRank

        idx = TCODE_LIST.index(sorted_dict[i][0])
        rank[idx] = currentRank

    return rank


if __name__ == "__main__":
    db = DB.MYDB()

    seasonCode = "39"
    game_num = 1
    season_win = {"06": 0, "10": 0, "16": 0, "30": 0, "35": 0, "50": 0, "55": 0, "60": 0, "64": 0, "65": 0, "70": 0}

    team_record = get_team_record(seasonCode)

    for idx, game in team_record.iterrows():
        game = game.to_dict()

        if game['win']:
            season_win[game['tcode']] += 1

        if idx % 2 == 1:
            game_num += 1
            gmkey = "S" + seasonCode + "G01N" + str(game_num)
            rank = make_team_rank(season_win)
            sql = """INSERT INTO team_rank VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            value = (None, gmkey) + tuple(rank)
            db.cursor.execute(sql, value)
            print(gmkey + " INSERTED!")

    db.db.commit()
    db.db.close()

    # data = get_round_rank_data(seasonCode)
    #
    # tcode_list = []
    # tracks_list = []
    #
    # for team in data:
    #     tcode = team['tcode']
    #     tracks = team['tracks']
    #
    #     tcode_list.append(tcode)
    #     tracks_list.append(tracks)
    #
    # tracks_arr = np.array(tracks_list)
    # tracks_arr = tracks_arr.T
    #
    # insert_rank_data_to_db(seasonCode, tcode_list, tracks_arr)
