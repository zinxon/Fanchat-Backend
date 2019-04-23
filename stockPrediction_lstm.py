from datetime import datetime
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.plotly as py
import plotly.tools as tls
import plotly.io as pio
from requests_html import HTMLSession
from sklearn.linear_model import LinearRegression
from IPython.display import Image
import firebase_admin
from firebase_admin import credentials, firestore
import threading
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dropout
import tensorflow as tf


db = firestore.client()

valid_set_size_percentage = 10
test_set_size_percentage = 10


def getUrlFromDB(stockCode):
    url = ""
    doc_ref = db.collection('stockPrediction').document(stockCode)
    print("in getURLfromDB")
    try:
        doc = doc_ref.get()
        print(u'url-lstm: {}'.format(doc.to_dict()['url-lstm']))
        url = doc.to_dict()['url-lstm']
        print('{0} 的url已存在Firebase'.format(stockCode))
    except Exception:
        print('現在為你生成{}圖表'.format(stockCode))
    # path = '/{0}/url'.format(stockCode)
    return url


def getStockInfo(stockCode):
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={0}&outputsize=full&apikey=TIR873DLX4ZC9WTV'.format(
        stockCode)
    stock_detail = HTMLSession().get(url).json()['Time Series (Daily)']


# df is the original unprocessing dataframe
    df = pd.DataFrame.from_dict(stock_detail).T  # .T for .transpose()
    df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
    df.index.names = ['Date']  # rename index
    df = df.sort_index(ascending=True)
    df.rename(columns={'1. open': 'Open', '2. high': 'High', '3. low': 'Low',
                       '4. close': 'Close', '5. volume': 'Volume'}, inplace=True)  # rename column
    df[['Open']] = df[['Open']].astype(float)
    df[['High']] = df[['High']].astype(float)
    df[['Low']] = df[['Low']].astype(float)
    df[['Close']] = df[['Close']].astype(float)
    df[['Volume']] = df[['Volume']].astype(int)
    df['Date_int'] = pd.to_datetime(df.index)
    df['Date_int'] = df['Date_int'].map(datetime.toordinal)
    return df


def processing(df, stockCode):
    df = df[-2000:]
    date = df.index
    date = date.values
    date = date.reshape(-1, 1)
    sc = MinMaxScaler(feature_range=(0, 1))
    df_scaled = sc.fit_transform(df[['Close']])
    valid_set_size = int(
        np.round(valid_set_size_percentage/100*len(df_scaled)))
    test_set_size = int(np.round(test_set_size_percentage/100*len(df_scaled)))
    train_set_size = len(df_scaled) - (valid_set_size + test_set_size)

    training_set_scaled = df_scaled[:train_set_size]
    valid_set_scaled = df_scaled[train_set_size:train_set_size+valid_set_size]
    test_set_scaled = df_scaled[train_set_size+valid_set_size:]

    X_train = []
    y_train = []
    X_valid = []
    y_valid = []
    X_test = []
    y_test = []

    for i in range(60, len(training_set_scaled)):
        X_train.append(training_set_scaled[i-60:i, 0])
        y_train.append(training_set_scaled[i, 0])

    for i in range(60, len(valid_set_scaled)):
        X_valid.append(valid_set_scaled[i-60:i, 0])
        y_valid.append(valid_set_scaled[i, 0])

    for i in range(60, len(test_set_scaled)):
        X_test.append(test_set_scaled[i-60:i, 0])
        y_test.append(test_set_scaled[i, 0])

    X_train, y_train = np.array(X_train), np.array(y_train)
    X_valid, y_valid = np.array(X_valid), np.array(y_valid)
    X_test, y_test = np.array(X_test), np.array(y_test)

    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    X_valid = np.reshape(X_valid, (X_valid.shape[0], X_valid.shape[1], 1))
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    regressor = load_model('trained_model/model/{}_model.h5'.format(stockCode))

    predicted_stock_price = regressor.predict(X_test)
    predicted_stock_price = sc.inverse_transform(predicted_stock_price)
    # regressor.evaluate(X_test, y_test)

    real_stock_price = df[['Close']][train_set_size+valid_set_size:]
    real_stock_price = real_stock_price[60:]

    date_predict = date[train_set_size+valid_set_size+60:]

    fig = plt.figure(figsize=(18, 9))
    plt.plot(date_predict, real_stock_price, color='black',
             label='{} Stock Price'.format(stockCode))
    plt.plot(date_predict, predicted_stock_price, color='green',
             label='Predicted {} Stock Price'.format(stockCode))
    plt.title('{} Stock Price Prediction'.format(stockCode))
    plt.xlabel('Time')
    plt.ylabel('{} Stock Price'.format(stockCode))
    plt.legend()
    plt.show()
    # finishTime = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    plotly_fig = py.plot_mpl(fig, filename="my first plotly plot")
    return plotly_fig


def dbProcessing(stockCode):
    df = getStockInfo(stockCode)
    url = processing(df, stockCode)
    doc_ref = db.collection('stockPrediction').document(stockCode)
    doc_ref.set({'url-lstm': url})
    msg = '{0} 的預測url已加到Firebase'.format(stockCode)
    print(msg)


def predictStock_lstm(stockCode):
    start_time = time.time()
    url = getUrlFromDB(stockCode)
    # t = threading.Thread(target=dbProcessing, args=[stockCode])
    # t.start()
    if url == "":
        return url
    elapsed_time = time.time() - start_time
    print('time: ', elapsed_time, 's')
    print(url,' in lstm')
    return url


if __name__ == '__main__':
    stockCode = '0700.HK'
    predictStock_lstm(stockCode)
    # df = getStockInfo(stockCode)
    # url = processing(df, stockCode)
