import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn import svm
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix

RANDOM_SEED = 1234


def read_df(file_name):
    df = pd.read_csv(file_name)
    
    df['win'] = df['score'] - df['loss']
    df.loc[df['score'] > df['loss'], 'win'] = 1
    df.loc[df['score'] < df['loss'], 'win'] = 0

    X = df.iloc[:, 5:-1]
    X.drop(columns=['ef','maxContiScoreCn', 'maxLeadScoreCn', 'playMin', 'playSec', 'scoreHighTimeCn', 'inout', 'inout1', 'idf'], inplace=True)
    y = df.iloc[:,-1]
    return X, y

def test_and_score(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8, random_state=RANDOM_SEED)
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
    for game_num in range(6, 16):
        X, y = read_df("recent_avg_record_ver2_{}game.csv".format(str(game_num)))
        score = test_and_score(X, y)
        print("recent", game_num, " game score : ", score)