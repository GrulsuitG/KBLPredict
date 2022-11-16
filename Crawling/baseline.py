import DB
import pandas as pd
from collections import defaultdict
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn import svm
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix

def test_and_score(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.7)
    scaler = StandardScaler()
    scaler.fit(X_train)
    X_train_scaled = scaler.transform(X_train)
    X_train_scaled = pd.DataFrame(data=X_train_scaled, columns=X_train.columns)

    scaler.fit(X_test)
    X_test_scaled = scaler.transform(X_test)
    X_test_scaled = pd.DataFrame(data=X_test_scaled, columns=X_test.columns)

    clf = svm.SVC(kernel='linear')
    clf.fit(X_train_scaled, y_train)

    y_pred = clf.predict(X_test_scaled)
    return accuracy_score(y_test, y_pred)


db = DB.MYDB()
db.cursor.execute("""
SELECT r.score, r.loss, r.rank, wl.*
FROM team_record_new2 r join win_lose_record wl on r.gmkey = wl.gmkey and r.tcode = wl.tcode
""")
df = pd.DataFrame(db.cursor.fetchall())

db.cursor.execute("select * from team_rank")
df2 = db.cursor.fetchall()
rank = defaultdict(dict)
for data in df2:
    gmkey = data['gmkey']
    for tcode in data.keys():
        if not tcode.isdigit():
            continue
        rank[gmkey][tcode] = data[tcode]

df['rank'] = -1
for i in range(df.index.stop):
    data = df.iloc[i].copy()
    data['rank'] = rank[data['gmkey']][data['tcode']]
    
    df.iloc[i] = data

data = pd.DataFrame()
data['currentWinRate'] = df['seasonWin'] / (df['seasonWin'] + df['seasonLose'])
data['relativeWinRate'] = df['totalRelativeWin'] / (df['totalRelativeWin'] + df['totalRelativeLose'])
data['seasonRelativeWinRate'] = df['seasonRelativeWin'] / (df['seasonRelativeWin'] + df['seasonRelativeLose'])
data['allWinRate'] = df['totalWin'] / (df['totalWin'] + df['totalLose'])



home = df[df.index % 2 == 0].copy().reset_index()
away = df[df.index % 2 != 0].copy().reset_index()

home['totalHomeAwayWinRate'] = home['homeWin'] / (home['homeWin'] + home['homeLose'])
away['totalHomeAwayWinRate'] = away['awayWin'] / (away['awayWin'] + away['awayLose'])

data['totalHomeWinRate'] = home['totalHomeAwayWinRate']
data['totalAwayWinRate'] = away['totalHomeAwayWinRate']
data['rank'] = home['rank'] - away['rank']
data['seasonHomeAwayWinRate'] = df['seasonHomeWin'] / (df['seasonHomeWin'] + df['seasonHomeLose']) if data.index % 2 == 0 else df['seasonAwayWin'] / (df['seasonAwayWin'] + df['seasonAwayLose']) 
data['target'] = df['score'] > df['loss']
data.fillna(0, inplace=True)

X = data.iloc[:, :-1]
y = data.iloc[:, -1]
total = 0
for i in range(100):
    a = test_and_score(X, y)
    if i % 10 == 0:
        print(i, a)
    total += a

print('100 avg :', total / 100)
