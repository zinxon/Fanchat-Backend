from requests_html import HTMLSession
import sys
import time
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate(
    "fanchat-firebase-adminsdk-hbuwz-9bbdc73723.json")
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()


def getStockInfo(stockCode):
    start_time = time.time()
    stock_dict = {}
    session = HTMLSession()
    session.browser

    url = 'https://hk.finance.yahoo.com/quote/{0}/profile'.format(stockCode)
    print(url)
    r = session.get(url)
    # r.html.render()
    try:
        name = r.html.xpath(
            '//*[@id="Col1-0-Profile-Proxy"]/section/div[1]/div/h3')[0].full_text
    except Exception:
        name = "unknown"
    try:
        sector = r.html.xpath(
            '//*[@id="Col1-0-Profile-Proxy"]/section/div[1]/div/div/p[2]/span[2]')[0].full_text
    except Exception:
        sector = "unknown"
    try:
        industry = r.html.xpath(
            '//*[@id="Col1-0-Profile-Proxy"]/section/div[1]/div/div/p[2]/span[4]')[0].full_text
    except Exception:
        industry = "unknown"
    try:
        employees = r.html.xpath(
            '//*[@id="Col1-0-Profile-Proxy"]/section/div[1]/div/div/p[2]/span[6]/span')[0].full_text
    except Exception:
        employees = "unknown"
    try:
        discribe = r.html.xpath(
            '//*[@id="Col1-0-Profile-Proxy"]/section/section[2]/p')[0].full_text
    except Exception:
        discribe = "unknown"
    try:
        website = r.html.xpath(
            '//*[@id="Col1-0-Profile-Proxy"]/section/div[1]/div/div/p[1]/a[2]')[0].full_text
    except Exception:
        website = "unknown"
    try:
        district = r.html.xpath(
            '//*[@id="Col1-0-Profile-Proxy"]/section/div[1]/div/div/p[1]')[0].full_text
    except Exception:
        district = "unknown"

    # print(name[0].full_text, sector[0].full_text,
    #       industry[0].full_text, employees[0].full_text, discribe[0].full_text)
    elapsed_time = time.time() - start_time
    stock_dict = {'name': name, 'stockCode': stockCode, 'sector': sector, 'industry': industry,
                  'employees': employees, 'discribe': discribe, 'website': website}
    print(stock_dict)
    doc_ref = db.collection('stockCode').document(stockCode)
    doc_ref.set(stock_dict)
    print('time: ', elapsed_time, 's')
    return stock_dict


def main():
    f = open("stockCode.txt", "r")
    # stockCode = f.readline().strip()
    # getStockInfo(stockCode)
    # print(stockCode)
    for stockCode in f:
        stockCode = stockCode.rstrip()
        print(stockCode)
        getStockInfo(stockCode)
        print('己加入Firebase: ', stockCode)
    # print(stock_dict)


if __name__ == '__main__':
    main()
    # stock = sys.argv[1]
    # stock = '0001.HK'
    # print('This is in stock_yahoo_peo.py: ', stock)
