import pandas as pd
import pymysql
import json
import warnings
import DB
warnings.filterwarnings(action='ignore')

#### 키플레이어 최근 경기 ####
def get_keyplayer_data_v1(start=0, verborse=False):
    db = DB.MYDB()
    db.cursor.execute("select * from game_meta where gameDate >= '20101015'")
    meta_data = db.cursor.fetchall()

    df = pd.DataFrame()
    for idx, meta in enumerate(meta_data[start:]):
        print(idx, meta['gmkey'])
        gmkey = meta['gmkey']
        db.cursor.execute("select pcode, home_away from player_record where gmkey = '{}'".format(gmkey))
        player = pd.DataFrame(db.cursor.fetchall())
        if verborse:
            print(player)
        
        h_player = tuple(player[player['home_away'] == '1']['pcode'])
        a_player = tuple(player[player['home_away'] == '2']['pcode'])
        gameDate = meta['gameDate']

        key_player =  tuple(get_recent_keyplayer_v1(h_player, gameDate, db) | get_recent_keyplayer_v1(a_player, gameDate, db))

        db.cursor.execute("""
                    select avg(ast) as ast, avg(bs) as bs, avg(defr) as defr, avg(dk) as dk, avg(dkA) as dkA, avg(ef) as ef, 
                            avg(fb) as fb, avg(fg) as fg, avg(fgA) as fgA, avg(fgtA) as fgtA, avg(fo) as fo, avg(foul) as foul, 
                            avg(ft) as ft, avg(ftA) as ftA, avg(gd) as gd, avg(offr) as offr, avg(pp) as pp, avg(ppA) as ppA, avg(pscore) as pscore, 
                            avg(stl) as stl, avg(tf) as tf, avg(threep) as threep, avg(threepA) as threepA, avg(r.to) as turonover, avg(wft) as wft, 
                            avg(woft) as woft, avg(rb) as rb, avg(score) as score, avg(trueShooting) as trueShooting, avg(astRatio) as astRatio, avg(rebRatio) as rebRatio,
                            home_away
                            from player_record r
                            where gmKey = '{}' and pcode in {}
                            group by home_away
        """.format(gmkey, key_player))
        data = db.cursor.fetchall()
        if verborse:
            print(data)
        for d in data:
            d['gmkey'] = gmkey
            if d['home_away'] == '1':
                d['tcode'] = meta['tcodeH']
            else:
                d['tcode'] = meta['tcodeA']

        data = pd.DataFrame(data)
        df = pd.concat([df, data], ignore_index=True)
    df.to_csv('key_player_recent5.csv')
    db.db.close()

def get_recent_keyplayer_v1(player, gameDate, db):
    db.cursor.execute("""
                    select *
                    from (
                        SELECT r.pcode, r.trueShooting, r.astRatio, r.rebRatio,r.home_away, m.gameDate, rank() over(partition by r.pcode order by gameDate desc) as a
                        FROM player_record r join game_meta m on r.gmkey = m.gmkey
                        WHERE m.gameDate < '{}'
                            and r.pcode in {}
                        ) as rankrow
                    where rankrow.a <=5;
                        """.format(gameDate, player))
    data = pd.DataFrame(db.cursor.fetchall()).groupby('pcode').mean()
    top_shoot = data.sort_values('trueShooting', ascending=False)[:1].index
    top_ast = data.sort_values('astRatio', ascending=False)[:1].index
    top_reb = data.sort_values('rebRatio', ascending=False)[:1].index

    top_player = set(top_shoot) | set(top_ast) | set(top_reb)

    return top_player


def get_keyplayer_data_v2(start=0, verborse=False):
    db = DB.MYDB()
    db.cursor.execute("select * from game_meta where gameDate >= '20101015'")
    meta_data = db.cursor.fetchall()

    season = 0

    df = pd.DataFrame()
    for idx, meta in enumerate(meta_data[start:]):
        print(idx, meta['gmkey'])
        gmkey = meta['gmkey']
        gameDate = meta['gameDate']
        season_key = gmkey[1:3]

        if season != season_key:
            season = season_key
            db.cursor.execute("select pcode, gmkey, home_away from player_record where gmkey like 'S{}%'".format(season))
            player = pd.DataFrame(db.cursor.fetchall())
            if verborse:
                print(player)
        
        game_player = player[player['gmkey'] == gmkey]
        h_player = tuple(game_player[game_player['home_away'] == '1']['pcode'])
        a_player = tuple(game_player[game_player['home_away'] == '2']['pcode'])
        if verborse:
            print("total :", game_player)
            print("home :", h_player)
            print("away :", a_player)
        key_player, game_record =  get_recent_keyplayer_v2(h_player, a_player, gameDate, db)

        data = game_record[game_record['pcode'].isin(key_player)]
        data.rename(columns={'home_away':'tcode'}, inplace=True)
        data.replace({"tcode" : '1'}, meta['tcodeH'], inplace=True)
        data.replace({"tcode" : '2'}, meta['tcodeA'], inplace=True)
        data.drop(columns=['a'], inplace=True)
        data = data.groupby('tcode',as_index=False).mean()
        data['gmkey'] = gmkey
        df = pd.concat([df, data], ignore_index=True)
        
    df.to_csv('key_player_recent5.csv')
    db.db.close()

def get_recent_keyplayer_v2(h_player, a_player, gameDate, db):
    players = h_player + a_player
    db.cursor.execute("""
                    select *
                    from (
                        SELECT r.*, m.gameDate, rank() over(partition by r.pcode order by gameDate desc) as a
                        FROM player_record r join game_meta m on r.gmkey = m.gmkey
                        WHERE m.gameDate <= '{}'
                            and r.pcode in {}
                        ) as rankrow
                    where rankrow.a <=6;
                        """.format(gameDate, players))
    all_data = pd.DataFrame(db.cursor.fetchall())
    top_player = set()
    iter = [h_player, a_player]
    data = all_data[all_data['a'] != 1]
    return_data = all_data[all_data['a'] == 1]
    for i in range(2):
        team_data = data[data['pcode'].isin(iter[i])].groupby('pcode').mean()

        top_shoot = team_data.sort_values('trueShooting', ascending=False)[:1]
        top_shoot = top_shoot.index if top_shoot['trueShooting'].values != 0 else []

        top_ast = team_data.sort_values('astRatio', ascending=False)[:1]
        top_ast = top_ast.index if top_ast['astRatio'].values != 0 else []

        top_reb = team_data.sort_values('rebRatio', ascending=False)[:1]
        top_reb = top_reb.index if top_reb['rebRatio'].values != 0 else []
        
        top_player |= set(top_shoot) | set(top_ast) | set(top_reb)
    return top_player, return_data

#### 팀 최근 경기 #####
def make_team_recent_data():
    h_data = []
    a_data = []
    db = DB.MYDB()
    db.cursor.execute("SELECT gmkey, tcodeA, tcodeH, gameDate FROM hygp.game_meta where gmkey >= 'S17G01N1' order by gmkey;")
    records = db.cursor.fetchall()
    db.cursor.execute("SELECT gmkey, score, loss FROM hygp.team_record where home_away = 'H' and gmkey >= 'S17' order by gmkey;")
    scores = db.cursor.fetchall()
    db.cursor.execute("select tcode from team_code")
    tcodes = db.cursor.fetchall()   
    tcodes = [tcode['tcode'] for tcode in tcodes]
    for idx, (record, score) in enumerate(zip(records, scores)):
        gmkey = record['gmkey']
        gameDate = record['gameDate']
        h_score = score['score']
        a_score = score['loss']
        if gmkey != score['gmkey']:
            print('index error', gmkey, score['gmkey'])
        if record['tcodeH'] == '75' or record['tcodeA'] == '75': #예외처리
            continue
        try:
            temp1 = dict(get_recent_team(record['tcodeH'], gameDate, db).mean(numeric_only=True))
            temp1['score'] = h_score
            temp1['gmkey'] = gmkey
            temp2 = dict(get_recent_team(record['tcodeA'], gameDate, db).mean(numeric_only=True))
            temp2['score'] = a_score
            temp2['gmkey'] = gmkey

            h_data.append(temp1)
            a_data.append(temp2)
        except Exception as e:
            print("error ", gmkey)
            e.with_traceback()
        if idx % 100 == 0:
            print(gmkey)
        

    h_df = pd.DataFrame(h_data).to_csv("team_h_data_recent5.csv")
    a_df = pd.DataFrame(h_data).to_csv("team_a_data_recent5.csv")
    # model = pd.concat([make_data(h_data, a_data), make_data(a_data, h_data)])
    # return model
    db.db.close()

#팀의 최근 기록을 가져오는 함수
def get_recent_team(team, gameDate, db):
    db.cursor.execute("""select b.*, a.gameDate 
                        from game_meta a, team_record b
                        where a.gmkey = b.gmkey and a.gameDate <'{}'
                            and b.tcode = '{}'
                        order by a.gameDate desc
                        limit 5""".format(gameDate, team))
    # db.db.close()
    return pd.DataFrame(db.cursor.fetchall())

# 시즌별 팀원 전체를 구하는 함수
def get_team_player(tcodes, db):
    
    db.cursor.execute("select pcode, tcode, seasonCode from player;")
    total_players = pd.DataFrame(db.cursor.fetchall())
    players = dict()
    
    for season in range(17, 41):
        season_player = total_players[total_players['seasonCode'] == str(season)]
        players[str(season)] = dict()
        for tcode in tcodes: 
            players[str(season)][tcode] = tuple(season_player[season_player['tcode'] == tcode]['pcode'])
    return players
