from pandas_datareader import data, wb
from datetime import datetime
import time
import numpy as np
import pandas as pd
import plotly.plotly as py
import plotly.io as pio
from requests_html import HTMLSession
from sklearn.linear_model import LinearRegression
from IPython.display import Image
import firebase_admin
from firebase_admin import credentials, firestore
import threading


cred = credentials.Certificate(
    "fanchat-firebase-adminsdk-hbuwz-9bbdc73723.json")
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()

moving_average_gruop = [7, 20, 50]
moving_average_gruop_name = ['Rolling_mean_' +
                             str(i) for i in moving_average_gruop]


def getUrlFromDB(stockCode):
    url = ""
    doc_ref = db.collection('stockPrediction').document(stockCode)
    try:
        doc = doc_ref.get().to_dict()
        url = doc['url']
        # print(u'{}'.format(doc.to_dict()))
        print(url)
        print('{0} 的url已存在Firebase'.format(stockCode))
    except Exception:
        print('現在為你生成{}圖表'.format(stockCode))
    # path = '/{0}/url'.format(stockCode)
    return url


def getStockInfo(stockCode):
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={0}&outputsize=compact&apikey=TIR873DLX4ZC9WTV'.format(
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
    for i in range(0, len(moving_average_gruop_name)):
        df[moving_average_gruop_name[i]] = df['Close'].rolling(
            moving_average_gruop[i]).mean()
    df['Date_int'] = pd.to_datetime(df.index)
    df['Date_int'] = df['Date_int'].map(datetime.toordinal)
    return df


def bbands(price, window_size=10, num_of_std=2):
    rolling_mean = price.rolling(window=window_size).mean()
    rolling_std = price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std*num_of_std)
    lower_band = rolling_mean - (rolling_std*num_of_std)
    return rolling_mean, upper_band, lower_band


def processing(df, stockCode):
    prices = df[['Close']].values
    moving_average = []
    for i in range(0, len(moving_average_gruop_name)):
        moving_average.append(df[[moving_average_gruop_name[i]]].values)
    # print(moving_average)
    date_int = df[['Date_int']].values
    # print(df)
    # split data into 3 parts
    prices_1 = prices[10:40]
    prices_2 = prices[40:-30]
    prices_3 = prices[-30:]
    date_int_1 = date_int[10:40]
    date_int_2 = date_int[40:-30]
    date_int_3 = date_int[-30:]

    regressor_1 = LinearRegression(n_jobs=-1)
    regressor_2 = LinearRegression(n_jobs=-1)
    regressor_3 = LinearRegression(n_jobs=-1)
    regressor_1.fit(date_int_1, prices_1)
    regressor_2.fit(date_int_2, prices_2)
    regressor_3.fit(date_int_3, prices_3)
    print('Regression Done!!')
    predict_price_1 = regressor_1.predict(date_int_1)
    predict_price_2 = regressor_2.predict(date_int_2)
    predict_price_3 = regressor_3.predict(date_int_3)
    predict_price_std_1 = predict_price_1.std()
    predict_price_std_2 = predict_price_2.std()
    predict_price_std_3 = predict_price_3.std()
    prices_upper_1, prices_lower_1 = predict_price_1 + \
        predict_price_std_1*2, predict_price_1 - predict_price_std_1*2
    prices_upper_2, prices_lower_2 = predict_price_2 + \
        predict_price_std_2*2, predict_price_2 - predict_price_std_2*2
    prices_upper_3, prices_lower_3 = predict_price_3 + \
        predict_price_std_3*2, predict_price_3 - predict_price_std_3*2

    INCREASING_COLOR = '#17BECF'

    DECREASING_COLOR = '#7F7F7F'
    data = [dict(
        type='candlestick',
        open=df.Open,
        high=df.High,
        low=df.Low,
        close=df.Close,
        x=df.index,
        yaxis='y2',
        name=stockCode,
        increasing=dict(line=dict(color=INCREASING_COLOR)),
        decreasing=dict(line=dict(color=DECREASING_COLOR)),
    )]

    layout = dict()

    fig = dict(data=data, layout=layout)

    fig['layout'] = dict()
    fig['layout']['plot_bgcolor'] = 'rgb(250, 250, 250)'
    fig['layout']['xaxis'] = dict(rangeselector=dict(visible=True))
    fig['layout']['yaxis'] = dict(domain=[0, 0.2], showticklabels=False)
    fig['layout']['yaxis2'] = dict(domain=[0.2, 0.8])
    fig['layout']['legend'] = dict(
        orientation='h', y=0.9, x=0.3, yanchor='bottom')
    fig['layout']['margin'] = dict(t=40, b=40, r=40, l=40)
    fig['layout']['title'] = 'Moving Linear Regression | Time vs. Price ({0})'.format(
        stockCode)
    fig['layout']['yaxis2']['title'] = 'Cost (HK$)'

    # # Clip the ends
    ma = moving_average_gruop
    mv_x_1 = df.index[ma[0]:]
    mv_y_1 = moving_average[0][ma[0]:]

    fig['data'].append(dict(x=mv_x_1, y=mv_y_1, type='scatter', mode='lines',
                            line=dict(width=1),
                            marker=dict(color='#E377C2'),
                            yaxis='y2', name='MA({0})'.format(ma[0])))

    mv_x_2 = df.index[ma[1]:]
    mv_y_2 = moving_average[1][ma[1]:]

    fig['data'].append(dict(x=mv_x_2, y=mv_y_2, type='scatter', mode='lines',
                            line=dict(width=1),
                            marker=dict(color='#A487C2'),
                            yaxis='y2', name='MA({0})'.format(ma[1])))

    mv_x_3 = df.index[ma[2]:]
    mv_y_3 = moving_average[2][ma[2]:]

    fig['data'].append(dict(x=mv_x_3, y=mv_y_3, type='scatter', mode='lines',
                            line=dict(width=1),
                            marker=dict(color='#C597C2'),
                            yaxis='y2', name='MA({0})'.format(ma[2])))

    colors = []

    for i in range(len(df.Close)):
        if i != 0:
            if df.Close[i] > df.Close[i-1]:
                colors.append(INCREASING_COLOR)
            else:
                colors.append(DECREASING_COLOR)
        else:
            colors.append(DECREASING_COLOR)

    fig['data'].append(dict(x=df.index, y=df.Volume,
                            marker=dict(color=colors),
                            type='bar', yaxis='y', name='Volume'))

    bb_avg, bb_upper, bb_lower = bbands(df.Close)

    fig['data'].append(dict(x=df.index, y=bb_upper, type='scatter', yaxis='y2',
                            line=dict(width=1),
                            marker=dict(color='#ccc'), hoverinfo='none',
                            legendgroup='Bollinger Bands', name='Bollinger Bands'))

    fig['data'].append(dict(x=df.index, y=bb_lower, type='scatter', yaxis='y2',
                            line=dict(width=1),
                            marker=dict(color='#ccc'), hoverinfo='none',
                            legendgroup='Bollinger Bands', showlegend=False))

    fig['data'].append(dict(x=df.index[10:40], y=predict_price_1, type='scatter', yaxis='y2',
                            line=dict(width=1),
                            marker=dict(color='#000'),
                            legendgroup='Linear Regression', name='Linear Regression', ))
    fig['data'].append(dict(x=df.index[40:70], y=predict_price_2, type='scatter', yaxis='y2',
                            line=dict(width=1),
                            marker=dict(color='#000'),
                            legendgroup='Linear Regression', showlegend=False, name='Linear Regression'))
    fig['data'].append(dict(x=df.index[70:100], y=predict_price_3, type='scatter', yaxis='y2',
                            line=dict(width=1),
                            marker=dict(color='#000'),
                            legendgroup='Linear Regression', showlegend=False, name='Linear Regression'))

    # py.plot(fig, filename='candlestick', auto_open=True)
    url = py.iplot(fig, filename=stockCode)
    # pio.write_image(
    #     fig, 'images/{0}.jpeg'.format(stockCode), validate=True)
    img_bytes = pio.to_image(fig, format='png')
    # print(img_bytes[:20])
    return url.resource


def chartProcessing(stockCode):
    print("Yay! I still got executed, even though my function has already returned!")
    df = getStockInfo(stockCode)
    url = processing(df, stockCode)
    doc_ref = db.collection('stockPrediction').document(stockCode)
    doc_ref.set({'url': url})
    msg = '{0} 的預測url已加到Firebase'.format(stockCode)
    print(msg)


def predictStock(stockCode):
    start_time = time.time()
    url = getUrlFromDB(stockCode)
    t = threading.Thread(target=chartProcessing, args=[stockCode])
    t.start()
    if url == "":
        return url
    elapsed_time = time.time() - start_time
    print('time: ', elapsed_time, 's')
    return url


if __name__ == '__main__':
    stockCode = '0700.HK'
    predictStock(stockCode)
    # print(df)
