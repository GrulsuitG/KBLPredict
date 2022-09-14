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
    db.cursor.execute("Select gmkey, gameDate, tcodeA, tcodeH FROM game_meta WHERE gameDate >= 20101015;")

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

            db.cursor.execute('''SELECT score, loss FROM team_record WHERE gmkey='{}' and tcode={}'''.format(gmkey, tcode))
            score_loss = db.cursor.fetchall()[0]
            score, loss = score_loss['score'], score_loss['loss']

            db.cursor.execute('''SELECT gmkey FROM game_meta WHERE gamedate <= {} and (tcodeA = {} or tcodeH = {})
                                       ORDER BY gameDate DESC LIMIT 1, 5;'''.format(gameDate, tcode, tcode))

            recent_gmkey = [item['gmkey'] for item in db.cursor.fetchall()]
            if recent_gmkey:
                recent_gmkey.reverse()
                if len(recent_gmkey) == 1:
                    db.cursor.execute('''SELECT * FROM team_record WHERE tcode = {} and gmkey = '{}';'''.format(tcode, recent_gmkey[0]))
                else:
                    db.cursor.execute('''SELECT * FROM team_record WHERE tcode = {} and gmkey IN {};'''.format(tcode, tuple(recent_gmkey)))

                recent_team_record = pd.DataFrame(db.cursor.fetchall())

                recent_team_record.drop(columns=['team_record_idx', 'gmkey', 'tcode', 'home_away', 'score', 'loss'], inplace=True)
                length = len(recent_team_record)
                total = length * (length + 1) / 2

                for i in range(length):
                    value = recent_team_record.iloc[i, :].values
                    # alpha : 가중치
                    alpha = (i + 1) / total
                    value = value * alpha

                    if i == 0:
                        row_data = value
                    else:
                        row_data += value

                temp_df = pd.DataFrame([row_data], columns=recent_team_record.columns)
                temp_df.insert(loc=0, column='gm_loss', value=loss)
                temp_df.insert(loc=0, column='gm_score', value=score)
                temp_df.insert(loc=0, column='tcode', value=tcode)
                temp_df.insert(loc=0, column='gmkey', value=gmkey)

                if result.empty:
                    result = temp_df
                else:
                    result = pd.concat([result, temp_df], ignore_index=True)

        result.to_csv("recent_avg_record_ver5.csv", mode="w")


                # try:
                #     mean = pd.DataFrame(recent_team_record.mean())
                #     mean = mean.transpose()
                #     mean.drop(columns=['team_record_idx', 'tcode', 'score', 'loss'], inplace=True)
                #     mean.insert(loc=0, column='gm_loss', value=loss)
                #     mean.insert(loc=0, column='gm_score', value=score)
                #     mean.insert(loc=0, column='tcode', value=tcode)
                #     mean.insert(loc=0, column='gmkey', value=gmkey)
                #     if result.empty:
                #         result = mean
                #     else:
                #         result = pd.concat([result, mean], ignore_index=True)
                # except Exception as e:
                #     print("Error = " + e, gmkey, tcode)

        # result.to_csv("recent_avg_record_ver5.csv", mode="w")
