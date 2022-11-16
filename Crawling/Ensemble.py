import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import VotingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score

def make_home_model(item):
    result = pd.DataFrame()

    #게임스코어
    #득점 + 0.4*야투성공개수 - 0.7*야투시도갯수 - 0.4*(자유투시도갯수 - 자유투성공갯수) + 
    #0.7 * 오펜스리바운드 + 0.3 * 디펜스리바운드 + 스틸 + 0.7 * 어시스트 + 0.7 * 블럭 - 0.4 * 개인파울 - 턴오버
    result['gameScore_h'] = item['avg_score'] + 0.4 * item['fgt'] - 0.7 * item['fgtA'] - 0.4*(item['ftA'] - item['ft']) + \
    0.7 * item['offr'] + 0.3 * item['defr'] + item['stl'] + 0.7 * item['ast'] + 0.7 * item['bs'] - 0.4 * item['foul'] - item['to']

    #승률
    result['winRate_h'] = -3.590 + 4.112 * item['defr'] + 1.839 * item['fg'] / item['fgA'] + 4.474 * item['stl'] + \
        1.674 * item['threep'] / item['threepA'] - 2.2 * item['to'] + 1.109 * item['ftA'] + 2.320 * item['bs'] + \
        1.812 * item['offr'] + 0.650 * item['ft'] / item['ftA'] + 0.590 * item['ast']

    #팀포제션
    result['teamPossesion_h'] = item['fgtA'] + 0.44 * item['ftA'] - item['offr'] + item['to']

    #PMG
    result['PMG_h'] = result['teamPossesion_h'] - item['fg'] - 0.77*(item['fgA'] - item['fg']) - 0.44 * item['ft'] - \
        0.339 * (item['ftA'] - item['ft']) - item['to'] + 0.77 * item['offr'] + 0.55 * item['ast'] + \
        item['stl'] + 0.23 * item['defr'] + 0.2 * item['foul'] + 0.7 * item['bs']

    #TOR 턴오버 레이팅
    result['TRB_h'] = (item['to'] * 100) / (item['fgtA'] + item['fgtA'] * 0.44 + item['ast'] + item['to'])

    #KBL Efficiency
    result['Efficiency_h'] = (item['avg_score'] + item['stl'] + item['bs'] + \
        item['defr']) + (item['offr'] + item['ast'] + item['gd']) * 1.5 - \
            (item['to'] * 1.5 + item['fgA'] - item['fg'] + (item['threepA'] - item['threep']) * 0.9 + \
            (item['ftA'] - item['ft']) * 0.8)

    result['currentWinRate_h'] = item['seasonWin'] / (item['seasonWin'] + item['seasonLose'])

    return result, item['gm_score'] > item['gm_loss']


def make_away_model(item):
    result = pd.DataFrame()

    #게임스코어
    #득점 + 0.4*야투성공개수 - 0.7*야투시도갯수 - 0.4*(자유투시도갯수 - 자유투성공갯수) + 
    #0.7 * 오펜스리바운드 + 0.3 * 디펜스리바운드 + 스틸 + 0.7 * 어시스트 + 0.7 * 블럭 - 0.4 * 개인파울 - 턴오버
    result['gameScore_a'] = item['avg_score'] + 0.4 * item['fgt'] - 0.7 * item['fgtA'] - 0.4*(item['ftA'] - item['ft']) + \
    0.7 * item['offr'] + 0.3 * item['defr'] + item['stl'] + 0.7 * item['ast'] + 0.7 * item['bs'] - 0.4 * item['foul'] - item['to']

    #승률
    result['winRate_a'] = -3.590 + 4.112 * item['defr'] + 1.839 * item['fg'] / item['fgA'] + 4.474 * item['stl'] + \
        1.674 * item['threep'] / item['threepA'] - 2.2 * item['to'] + 1.109 * item['ftA'] + 2.320 * item['bs'] + \
        1.812 * item['offr'] + 0.650 * item['ft'] / item['ftA'] + 0.590 * item['ast']

    #팀포제션
    result['teamPossesion_a'] = item['fgtA'] + 0.44 * item['ftA'] - item['offr'] + item['to']

    #PMG
    result['PMG_a'] = result['teamPossesion_a'] - item['fg'] - 0.77*(item['fgA'] - item['fg']) - 0.44 * item['ft'] - \
        0.339 * (item['ftA'] - item['ft']) - item['to'] + 0.77 * item['offr'] + 0.55 * item['ast'] + \
        item['stl'] + 0.23 * item['defr'] + 0.2 * item['foul'] + 0.7 * item['bs']

    #TOR 턴오버 레이팅
    result['TRB_a'] = (item['to'] * 100) / (item['fgtA'] + item['fgtA'] * 0.44 + item['ast'] + item['to'])

    #KBL Efficiency
    result['Efficiency_a'] = (item['avg_score'] + item['stl'] + item['bs'] + \
        item['defr']) + (item['offr'] + item['ast'] + item['gd']) * 1.5 - \
            (item['to'] * 1.5 + item['fgA'] - item['fg'] + (item['threepA'] - item['threep']) * 0.9 + \
            (item['ftA'] - item['ft']) * 0.8)

    result['currentWinRate_a'] = item['seasonWin'] / (item['seasonWin'] + item['seasonLose'])

    return result, item['gm_score'] > item['gm_loss']

def make_model_with_baseline(baseline, target):
    #신생 팀 첫번째 기록 제거
    target = target[target['gmkey'] != 'S39G01N3'].reset_index()
    baseline = baseline[baseline['gmkey'] != 'S39G01N3'].reset_index()

    df = pd.concat([target, baseline],axis=1)

    a_team_data = df[df.index % 2 == 0].reset_index()
    h_team_data = df[df.index % 2 != 0].reset_index()
    home_data, win = make_home_model(h_team_data)
    away_data, _ = make_away_model(a_team_data)

    data = pd.concat([home_data, away_data], axis=1)
    data['rank'] = h_team_data['rank'] - a_team_data['rank']
    data['win'] = win
    data = data.fillna(0)

    X, y = data.iloc[:, :-1], data.iloc[:, -1]
    return X, y



baseline = pd.read_csv("baseline.csv")
target = pd.read_csv("recent_avg_record_ver7_9game.csv", index_col= 0)
X, y = make_model_with_baseline(baseline, target)

X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.7)


scaler = StandardScaler()
scaler.fit(X_train)
X_train_scaled = scaler.transform(X_train)
X_train_scaled = pd.DataFrame(data=X_train_scaled, columns=X_train.columns)

scaler.fit(X_test)
X_test_scaled = scaler.transform(X_test)
X_test_scaled = pd.DataFrame(data=X_test_scaled, columns=X_test.columns)

rf = RandomForestClassifier(max_depth=8, min_samples_leaf=7, min_samples_split= 2, n_estimators= 150, random_state=2022, n_jobs=-1)
gb = GradientBoostingClassifier(learning_rate=0.03, max_depth=1, min_samples_leaf=5, n_estimators=100, random_state=2022)
xgb = XGBClassifier(n_estimators=31, learning_rate=0.1, max_depth=3, gamma=0.1, random_state=2022)
lgbm = LGBMClassifier(n_estimators=100, max_depth=7, learning_rate=0.01, colsample_bytree=0.8, subsample=0.8, random_state=2022)

voting_model = VotingClassifier(estimators=[('RandomForest', rf),
                                            ('GradientBoost', gb),
                                            ('XGBoost', xgb),
                                            ('LightGBM', lgbm)],       
                                voting='hard')

classifiers = [rf, gb, xgb, lgbm]

for classifier in classifiers:
    classifier.fit(X_train_scaled, y_train)
    pred = classifier.predict(X_test_scaled)
    class_name = classifier.__class__.__name__
    print('{0} 정확도: {1:.4f}'.format(class_name, accuracy_score(y_test, pred)))

voting_model.fit(X_train_scaled, y_train)
pred = voting_model.predict(X_test_scaled)
print('보팅 분류기의 정확도: {0: .4f}'.format(accuracy_score(y_test, pred)))