# /index.py

from flask import Flask, request, jsonify, render_template, make_response
from requests_html import HTMLSession
from selenium import webdriver
from opencc import OpenCC
from threading import Thread
import multiprocessing as mp
from stock import getStockInfo
from stockPrediction_1 import predictStock
from subprocess import check_output
from opencc import OpenCC
import os
import dialogflow
import json

app = Flask(__name__)
log = app.logger
cc = OpenCC('s2t')


@app.route('/', methods=['GET'])
def index():
    return "<h1>This is a webhook for Dialogflow - FanChat!</h1>"


def handle_verification():
    '''
    Verifies facebook webhook subscription
    Successful when verify_token is same as token sent by facebook
    app
    '''
    VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
    if (request.args.get('hub.verify_token', '') == VERIFY_TOKEN):
        print("Verified")
        return request.args.get('hub.challenge', '')
    else:
        print("Wrong token")
        return "Error, wrong validation token"


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """This method handles the http requests for the Dialogflow webhook
    This is meant to be used in conjunction with the weather Dialogflow agent
    """
    req = request.get_json(silent=True, force=True)
    print(req)
    print("Request:", json.dumps(req, indent=4))
    res = processRequest(req)
    return make_response(jsonify({'fulfillmentText': res}))


def processRequest(req):
    try:
        action = req.get('queryResult').get('action')
        res = {}
    except AttributeError:
        return 'json error'

    if action == "input.welcome":
        res = get_welcome(req)
    elif action == 'get_crypto_price':
        res = get_crypto_price(req)
    elif action == 'get_stock_price':
        res = get_stock_price(req)
    elif action == 'get_featured_news':
        res = get_featured_news(req)
    elif action == 'compare_stock':
        res = compare_stock(req)
    elif action == 'get_stock_prediction':
        res = get_stock_prediction(req)
    elif action == 'get_stock_new':
        res = get_stock_new(req)
    elif action == 'add_stock':
        res = add_stock(req)
    else:
        res = {}
    print('Action: '+action)
    print('Response: '+res)
    return res


def get_welcome(req):
    response = '你好老友！我叫FanChat，我係一個財務資訊型既聊天機械人。'
    return response


def get_crypto_price(req):
    parameters = req['queryResult']['parameters']
    fromType = parameters['cryptoCurrencies'][0]
    toType = 'HKD'
    if parameters['number']:
        number = parameters['number']
    else:
        number = 1
    if parameters['realCur']:
        toType = parameters['realCur']
    elif (len(parameters['cryptoCurrencies']) > 1):
        toType = parameters['cryptoCurrencies'][1]
    print('fromType: ', fromType, ' toType: ', toType)
    crypto_dict = call_alphavantage_api_crypto(fromType, toType, number)
    res = "{3} {0}(s) 依家 {1}${2}".format(
        crypto_dict['fromType'], crypto_dict['toType'], crypto_dict['value'], crypto_dict['coin_number'])
    return res


def get_stock_price(req):
    parameters = req['queryResult']['parameters']
    stock = parameters['stock']
    stock_original = parameters['stockName']
    if parameters['number']:
        number = parameters['number']
    else:
        number = 1
    print(stock)
    # out = check_output(['python','stock.py',stock])
    # out = cc.convert(out.decode("utf-8"))
    # print(out)
    stock_dict = call_alphavantage_api_stock(stock, stock_original, number)
    res = "{4}股{0} ({1}) 依家 HK${2} 在 {3}".format(
        stock_dict['stock_original'], stock_dict['stock'], stock_dict['stock_value'], stock_dict['time'], stock_dict['stock_number'])
    # res = "{3}股{0} ({1}) 依家 HK${2}".format(test_dict['stock_name'],test_dict['stock_code'],test_dict['stock_price'],number)
    return res


def get_featured_news(req):
    new_detail = HTMLSession().get(
        'https://api.rss2json.com/v1/api.json?rss_url=http%3A%2F%2Fwww.etnet.com.hk%2Fwww%2Ftc%2Fnews%2Frss.php%3Fsection%3Deditor').content
    new_detail = json.loads(new_detail)
    # https://api.rss2json.com/v1/api.json?rss_url=https%3A%2F%2Fnews.mingpao.com%2Frss%2Fpns%2Fs00004.xml 明報新聞網-每日明報 RSS 經濟
    # https://www.google.com/alerts/feeds/18147058901783421505/7083091648256545836 Google - 騰訊
    new_title = new_detail['feed']['title']
    new_items = new_detail['items']
    response_list = ""
    for i in range(0, len(new_items)):
        content = '''
        {0}
        '''.format(new_items[i]['title'])
        response_list += content
        print('responselist', response_list)
    res = str(response_list)
    return res


def get_stock_prediction(req):
    parameters = req['queryResult']['parameters']
    stock = parameters['stock']
    # ma_indes = [7,20,50]
    res = predictStock(stock)
    return res


def get_stock_new(req):
    parameters = req['queryResult']['parameters']
    stock = parameters['stock']
    # stock_dict = {}
    # new_list = []
    # browser = webdriver.Chrome()
    # url = 'https://hk.finance.yahoo.com/quote/{0}/news'.format(stock)
    # browser.get(url)  # navigate to the page
    # new_list = []
    # news = browser.find_element_by_xpath(
    #     '//*[@id="latestQuoteNewsStream-0-Stream"]/ul').text
    # browser.quit()
    return str(stock + "-新聞正在爬取")


def compare_stock(req):
    res = ''
    parameters = req['queryResult']['parameters']
    stocklist = []
    stocklist_original = []
    # parameter from Dialogflow input
    stocklist_parameter = parameters['stock']
    stocklist_original_parameter = parameters['stockName']
    compare = parameters['compare']
    for i in range(len(stocklist_parameter)):
        stocklist.append(stocklist_parameter[i])
        stocklist_original.append(stocklist_original_parameter[i])
    stock_detail_list = call_alphavantage_api_stock_compare(
        stocklist, stocklist_original)
    stock_detail_list_str = str(stock_detail_list)
    # print(stock_detail_list_str)
    if compare == '平':
        # seq = [x['stock_value'] for x in stock_detail_list]
        # stock_compare = min(seq)
        stock_compare = min(stock_detail_list, key=lambda x: x['stock_value'])
    elif compare == '貴':
        stock_compare = max(stock_detail_list, key=lambda x: x['stock_value'])
    compare_result = 'compare result: {3}股{0} HK${1} 是最{2}'.format(
        stock_compare['stock_original'], stock_compare['stock_value'], compare, stock_compare['stock_number'])
    res = stock_detail_list_str + '\n' + compare_result
    print(res)
    return res


def add_stock(req):
    parameters = req['queryResult']['parameters']
    stock = parameters['stock']
    stock_original = parameters['stockName']
    res = "已關注 {1} - {0}".format(stock, stock_original)
    return res


def call_alphavantage_api_crypto(fromType, toType, number):
    api_key = os.getenv('ALPHAVANTAGE_API_KEY')
    host = 'https://www.alphavantage.co'
    path = '/query?function=CURRENCY_EXCHANGE_RATE&from_currency=' + \
        fromType + '&to_currency='+toType+'&apikey='+api_key
    crypto_detail = HTMLSession().get(host+path).content
    crypto_detail = json.loads(crypto_detail)
    print(crypto_detail)
    crypto_detail_body = crypto_detail['Realtime Currency Exchange Rate']
    rate_float = float(crypto_detail_body['5. Exchange Rate'])
    value = rate_float * float(number)
    crypto_dict = {'fromType': crypto_detail_body['2. From_Currency Name'],
                   'toType': crypto_detail_body['3. To_Currency Code'], 'value': value, 'coin_number': number}
    return crypto_dict


def call_alphavantage_api(stock):
    api_key = os.getenv('ALPHAVANTAGE_API_KEY')
    host = 'https://www.alphavantage.co'
    path = '/query?function=TIME_SERIES_INTRADAY&outputsize=compact&symbol={0}&interval=1min&apikey={1}'.format(
        stock, api_key)
    stock_detail = HTMLSession().get(host+path).content
    stock_detail = json.loads(stock_detail)
    url = host+path
    print(url)
    return stock_detail  # return python dict of stock (unprocessing)


def call_alphavantage_api_stock(stock, stock_original, number=1):
    stock_detail = call_alphavantage_api(stock)
    time_series = stock_detail['Time Series (1min)']
    now_time = tuple(time_series.items())[0][0]
    now_price = time_series[now_time]['4. close']
    now_time_split = now_time.split(' ')[0]
    value = float(now_price) * (number)
    # print(now_time)
    # print(now_price)
    stock_dict = {'stock_original': stock_original, 'stock': stock, 'stock_number': number,
                  'stock_price': now_price, 'stock_value': value, 'time': now_time_split}
    # return {'res': res, 'stock_dict': stock_dict}
    return stock_dict  # return processed dict of stock


def call_alphavantage_api_stock_compare(stocklist, stocklist_original):
    stock_dict_list = []
    for i in range(len(stocklist)):
        stock_dict_list.append(call_alphavantage_api_stock(
            stocklist[i], stocklist_original[i]))
    return stock_dict_list

# https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=0700.HK&interval=5min&apikey=TIR873DLX4ZC9WTV

    # run Flask app
if __name__ == "__main__":
    app.run()
