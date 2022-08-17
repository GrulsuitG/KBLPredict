from cgitb import reset
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn import svm
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix

RANDOM_SEED = 2022


def read_df(file_name):
    df = pd.read_csv(file_name)
    
    df['win'] = df['score'] - df['loss']
    df.loc[df['score'] > df['loss'], 'win'] = 1
    df.loc[df['score'] < df['loss'], 'win'] = 0

    X = df.iloc[:, 5:-1]
    X.drop(columns=['ef','maxContiScoreCn', 'maxLeadScoreCn', 'playMin', 'playSec', 'scoreHighTimeCn', 'inout', 'inout1', 'idf'], inplace=True)
    y = df.iloc[:,-1]
    return X, y

def make_model(file_name):
    item = pd.read_csv(file_name)
    result = pd.DataFrame()

    #게임스코어
    #득점 + 0.4*야투성공개수 - 0.7*야투시도갯수 - 0.4*(자유투시도갯수 - 자유투성공갯수) + 
    #0.7 * 오펜스리바운드 + 0.3 * 디펜스리바운드 + 스틸 + 0.7 * 어시스트 + 0.7 * 블럭 - 0.4 * 개인파울 - 턴오버
    result['gameScore'] = item['score'] + 0.4 * item['fgt'] - 0.7 * item['fgtA'] - 0.4*(item['ftA'] - item['ft']) + \
    0.7 * item['offr'] + 0.3 * item['defr'] + item['stl'] + 0.7 * item['ast'] + 0.7 * item['bs'] - 0.4 * item['foul'] - item['to']

    #승률
    result['winRate'] = -3.590 + 4.112 * item['defr'] + 1.839 * item['fg'] / item['fgA'] + 4.474 * item['stl'] + \
        1.674 * item['threep'] / item['threepA'] - 2.2 * item['to'] + 1.109 * item['ftA'] + 2.320 * item['bs'] + \
        1.812 * item['offr'] + 0.650 * item['ft'] / item['ftA'] + 0.590 * item['ast']

    #팀포제션
    result['teamPossesion'] = item['fgtA'] + 0.44 * item['ftA'] - item['offr'] + item['tto']

    #PMG
    # result['PMG'] = result['teamPossesion'] - item['fg'] - 0.77*(item['fgA'] - item['fg']) - 0.44 * item['ft'] - \
    #     0.339 * (item['ftA'] - item['ft']) - item['to'] + 0.77 * item['offr'] + 0.55 * item['ast'] + \
    #     item['stl'] + 0.23 * item['defr'] + 0.2 * item['foul'] + 0.7 * item['bs']


    result['win'] = item['score'] > item['loss']
    X = result.iloc[:, :-1]
    y = result.iloc[:, -1]
    return X, y

def test_and_score(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.7, random_state=RANDOM_SEED)
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

if __name__ == "__main__":
    for game_num in range(5, 16):
        X, y = make_model("recent_avg_record_ver3_{}game.csv".format(str(game_num)))
        score = test_and_score(X, y)
        print("recent", game_num, "game score : ", score)
