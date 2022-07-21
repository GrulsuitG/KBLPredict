import pandas as pd
import pymysql
import json
import warnings
import DB
warnings.filterwarnings(action='ignore')

def make_model(data):
    h_data = pd.DataFrame()
    a_data = pd.DataFrame()
    # 어시스트 -> 어시스트 / 필드골 성공
    h_data['ast'] = data['h_ast'] / data['h_fgt']
    a_data['ast'] = data['a_ast'] / data['a_fgt']
    # 2점
    h_data['twop'] = data['h_fg'] / data['h_fgA']
    a_data['twop'] = data['a_fg'] / data['a_fgA']

    # 3점
    h_data['threep'] = data['h_threep'] / data['h_threepA']
    a_data['threep'] = data['a_threep'] / data['a_threepA']

    # 자유투
    h_data['freep'] = data['h_ft'] / data['h_ftA']
    a_data['freep'] = data['a_ft'] / data['a_ftA']

    # 공격 리바
    h_data['offr'] = data['h_offr'] / (data['h_offr'] + data['a_defr'])
    a_data['offr'] = data['a_offr'] / (data['a_offr'] + data['h_defr'])
    # 속공
    h_data['tfb'] = data['h_tfb'] / data['h_fgt']
    a_data['tfb'] = data['a_tfb'] / data['a_fgt']

    # 벤치득점
    h_data['bench'] = data['h_benchScoreCn'] / data['h_score']
    a_data['bench'] = data['a_benchScoreCn'] / data['a_score']


    # 속공득점
    h_data['tfbp'] = data['h_fbScoreCn'] / data['h_score']
    a_data['tfbp'] = data['a_fbScoreCn'] / data['a_score']

    # 페인트존 득점
    h_data['ppp'] = data['h_pp'] / data['h_ppA']
    a_data['ppp'] = data['a_pp'] / data['a_ppA']

    # 덩크
    h_data['dk'] = data['h_dk'] / data['h_dkA']
    a_data['dk'] = data['a_dk'] / data['a_dkA']

    # 최다 연속 득점 비율
    h_data['maxContiScore'] = data['h_maxContiScoreCn'] / data['h_score']
    a_data['maxContiScore'] = data['a_maxContiScoreCn'] / data['a_score']

    # 최다 리드 점수차
    # h_data['maxLeadScore'] = (data['h_score'] - data['a_score']) / data['h_maxLeadScoreCn']
    # a_data['maxLeadScore'] = (data['a_score'] - data['h_score']) / data['a_maxLeadScoreCn']
    # h_data[h_data['maxLeadScore'] < -1]

    # 득점 우위 시간
    h_data['scoreHighTime'] = data['h_scoreHighTimeCn'] / 2400
    a_data['scoreHighTime'] = data['a_scoreHighTimeCn'] / 2400

    # 세컨찬스 득점
    h_data['secChanceScore'] = data['h_secChanceScoreCn'] / data['h_score']
    a_data['secChanceScore'] = data['a_secChanceScoreCn'] / data['a_score']

    # 턴오버
    h_data['to'] = (data['h_to'] + data['h_tto']) / (data['h_to'] + data['h_tto'] + data['a_to'] + data['a_tto'])
    a_data['to'] = (data['a_to'] + data['a_tto']) / (data['h_to'] + data['h_tto'] + data['a_to'] + data['a_tto'])

    h_data['defr'] = data['h_defr'] / (data['a_offr'] + data['h_defr'])
    a_data['defr'] = data['a_defr'] / (data['h_offr'] + data['a_defr'])
    h_data['stl'] = data['h_stl'] / (data['h_stl'] + data['a_stl'])
    a_data['stl'] = data['a_stl'] / (data['h_stl'] + data['a_stl'])
    h_data['bs'] = data['h_bs'] / data['a_fgtA']
    a_data['bs'] = data['a_bs'] / data['h_fgtA']
    h_data['foul'] = data['h_foul'] / (data['h_foul'] + data['a_foul'])
    a_data['foul'] = data['a_foul'] / (data['h_foul'] + data['a_foul'])
    h_data['tf'] = data['h_tf'] / (data['h_tf'] + data['a_tf'])
    a_data['tf'] = data['a_tf'] / (data['h_tf'] + data['a_tf'])
    h_data['gd'] = data['h_gd'] / (data['h_gd'] + data['a_gd'])
    a_data['gd'] = data['a_gd'] / (data['h_gd'] + data['a_gd'])
    h_data['teamR'] = data['h_teamR'] / (data['h_teamR'] + data['a_teamR'])
    a_data['teamR'] = data['a_teamR'] / (data['h_teamR'] + data['a_teamR'])

    # h_data = h_data.fillna(0)
    # h_data = h_data.replace([np.inf, -np.inf], 0)
    h_data['score'] = data['h_score']
    # h_data['gmkey'] = data['gmkey']

    # a_data = a_data.fillna(0)
    # a_data = a_data.replace([np.inf, -np.inf], 0)
    a_data['score'] = data['a_score']
    # a_data['gmkey'] = data['gmkey']
    return pd.concat([h_data, a_data], ignore_index=True)

#시즌 키와 팀코드를 가지고 전시즌 평균기록으로 가장 잘하는 선수를 찾아 이번 시즌 키플레이어를 구하는 함수.
def get_season_keyplayer(season):
    db = DB.MYDB()
    result = dict()
    seasonCode = 'S' + str(season) + 'G01'
    db.cursor.execute("select tcode from team_code")
    tcodes = db.cursor.fetchall()   
    tcodes = [tcode['tcode'] for tcode in tcodes]
    for tcode in tcodes:
        tcode = str(tcode['tcode'])
        
        db.cursor.execute('''SELECT *
                        FROM (
                            SELECT p.*, rank() over(partition by p.pcode order by p.seasonCode desc) as a
                            FROM player_avg_record as p
                            WHERE seasonCode < 'S{}' and
                                pcode IN (SELECT pcode
                                            FROM player
                                            WHERE tcode = '{}' and seasonCode = '{}')
                            ) as rankrow
                        where rankrow.a <=1;
        '''.format(seasonCode, tcode, season))
        data = pd.DataFrame(db.cursor.fetchall())
        if data.size != 0:
            score_top_player = data.sort_values('score',ascending=False)['pcode'][:1]
            ast_top_player = data.sort_values('ast', ascending=False)['pcode'][:1]
            rb_top_player = data.sort_values('rb', ascending=False)['pcode'][:1]
            result[tcode] = set(score_top_player) | set(ast_top_player) | set(rb_top_player)

    db.db.close()
    return result

#전 시즌 점수를 이용해 키플레이어 선정 -> 
# 그 키플레이어를 이용해 최근 5경기 기록 조회
def get_keyplayer_game_record():
    db = DB.MYDB()
    season_keyplayers = make_keyplayers()
    df = pd.DataFrame()
    for season in season_keyplayers:
        for tcode in season_keyplayers[season]:
            pcode = season_keyplayers[season][tcode]
            if len(pcode) == 1:
                pcode.add('0')
            try:
            
                db.cursor.execute("""
                                SELECT * FROM hygp.player_record a join game_meta b on a.gmkey = b.gmkey
                                where (b.tcodeH = '{}' or b.tcodeA = '{}') and a.gmkey >= 'S17'
                                and a.pcode in {};
                                """.format(tcode, tcode, tuple(pcode)))
                data = pd.DataFrame(db.cursor.fetchall())
                df = pd.concat([df, data.groupby('gmkey').mean()], ignore_index=True)
            except Exception as e:
                print(season, tcode)
                print(pcode)
                print(data)
                input()
            # print(df)
        
    db.db.close()

    return df

def make_keyplayers():
    season_keyplayers = dict()
    for season in range(17, 41):
        season_keyplayers[str(season)] = get_season_keyplayer(season)
    return season_keyplayers

#플레이어들의 최근 5경기 기록 조회
def get_players_recent_records(players, gameDate, db):
    if len(players) == 1:
        players.add('0')
    db.cursor.execute("""
                        select *
                        from (
                            SELECT b.*, a.gameDate, rank() over(partition by b.pcode order by gameDate desc) as a
                            FROM game_meta a, player_record b
                            WHERE a.gmkey = b.gmkey and a.gameDate < '{}'
                                and b.pcode in {}
                            ) as rankrow
                        where rankrow.a <=5;""".format(gameDate, tuple(players)))
    # db.db.close()
    return pd.DataFrame(db.cursor.fetchall())

def make_player_recent_data():
    h_data = []
    a_data = []
    db = DB.MYDB()
    db.cursor.execute("SELECT gmkey, tcodeA, tcodeH, gameDate FROM hygp.game_meta where gmkey >= 'S17G01N1' order by gmkey;")
    records = db.cursor.fetchall()
    db.cursor.execute("SELECT gmkey, score, loss FROM hygp.team_record where home_away = 'H' and gmkey >= 'S17' order by gmkey;")
    scores = db.cursor.fetchall()
    season_keyplayers = make_keyplayers()
    for idx, (record, score) in enumerate(zip(records, scores)):
        gmkey = record['gmkey']
        gameDate = record['gameDate']
        season = gmkey[1:3]
        h_score = score['score']
        a_score = score['loss']
        tcodeH = record['tcodeH']
        tcodeA = record['tcodeA']
        if gmkey != score['gmkey']:
            print('index error', gmkey, score['gmkey'])
        if tcodeH == '75' or tcodeA == '75': #예외처리
            continue
        try:
            temp1 = dict(get_players_recent_records(season_keyplayers[season][tcodeH], gameDate, db).mean(numeric_only=True))
            temp1['score'] = h_score
            temp1['gmkey'] = gmkey
            temp2 = dict(get_players_recent_records(season_keyplayers[season][tcodeA], gameDate, db).mean(numeric_only=True))
            temp2['score'] = a_score
            temp2['gmkey'] = gmkey

            h_data.append(temp1)
            a_data.append(temp2)
        except Exception as e:
            print("error ", gmkey)
        if idx % 100 == 0:
            print(gmkey)
        

    h_df = pd.DataFrame(h_data).to_csv("h_data.csv")
    a_df = pd.DataFrame(h_data).to_csv("a_data.csv")
    # model = pd.concat([make_data(h_data, a_data), make_data(a_data, h_data)])
    # return model
    db.db.close()

