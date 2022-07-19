import pandas as pd
import DB
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

db = DB.MYDB()


def get_team_avg_record(gmkey: str, tcode: int):
    pass


def split_gmkey(gmkey: str):
    season_code = int(gmkey[gmkey.index('S') + 1:gmkey.index('G')])
    game_code = int(gmkey[gmkey.index('G') + 1:gmkey.index('N')])
    game_num = int(gmkey[gmkey.index('N') + 1:])

    return season_code, game_code, game_num


def get_gmkey_list():
    db.cursor.execute("Select gmkey, gameDate, tcodeA, tcodeH FROM game_meta;")

    gmkey_list = list()
    gmkey_tcode_dict = dict()

    for item in db.cursor.fetchall():
        gmkey_list.append(item["gmkey"])
        gmkey_tcode_dict[item["gmkey"]] = [item['gameDate'], item["tcodeA"], item["tcodeH"]]

    return gmkey_list, gmkey_tcode_dict


if __name__ == "__main__":
    gmkey_list, gmkey_tcode = get_gmkey_list()

    result = pd.DataFrame()

    for gmkey in gmkey_list:
        print("현재 조회 gmkey : " + gmkey)
        gameDate = gmkey_tcode[gmkey][0]

        for i in range(1, 3):
            tcode = gmkey_tcode[gmkey][i]

            db.cursor.execute('''SELECT gmkey FROM game_meta WHERE gamedate <= {} and (tcodeA = {} or tcodeH = {})
                                       ORDER BY gameDate DESC LIMIT 1, 5;'''.format(gameDate, tcode, tcode))

            recent_gmkey_away = [item['gmkey'] for item in db.cursor.fetchall()]
            if recent_gmkey_away:
                recent_gmkey_away.reverse()
                if len(recent_gmkey_away) == 1:
                    db.cursor.execute('''SELECT * FROM team_record WHERE tcode = {} and gmkey = '{}';'''.format(tcode, recent_gmkey_away[0]))
                else:
                    db.cursor.execute('''SELECT * FROM team_record WHERE tcode = {} and gmkey IN {};'''.format(tcode, tuple(recent_gmkey_away)))

                recent_team_record_away = pd.DataFrame(db.cursor.fetchall())

                try:
                    mean = pd.DataFrame(recent_team_record_away.mean())
                    mean = mean.transpose()
                    mean.drop(columns=['team_record_idx'], inplace=True)
                    mean.drop(columns=['tcode'], inplace=True)
                    mean.insert(loc=0, column='tcode', value=tcode)
                    mean.insert(loc=0, column='gmkey', value=gmkey)
                    if result.empty:
                        result = mean
                    else:
                        result = pd.concat([result, mean], ignore_index=True)
                except Exception as e:
                    print("Error = " + e, gmkey, tcode)

        result.to_csv("recent_avg_record.csv", mode="w")
