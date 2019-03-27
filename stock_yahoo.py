from requests_html import HTMLSession
# from opencc import OpenCC
import sys
import time


def getStockInfo(stock):
    start_time = time.time()
    # cc = OpenCC('s2t')
    stock_dict = {}
    session = HTMLSession()
    session.browser
    url = 'https://hk.finance.yahoo.com/quote/{0}/news'.format(stock)
    r = session.get(url)
    r.html.render()
    # name = r.html.find('h1', first=True)
    # price = r.html.xpath('//*[@id="quote-header-info"]/div[3]/div/div/span[1]')
    # news = r.html.xpath('//*[@id="quoteNewsStream-0-Stream"]/ul')
    news = r.html.xpath('//*[@id="latestQuoteNewsStream-0-Stream"]')
    # print(name.text)
    # print(price[0].text)
    for new in news:
        print(new.text)
    elapsed_time = time.time() - start_time
    print('time: ', elapsed_time, 's')
    return stock_dict


def main(stock):
    stock_dict = getStockInfo(stock)
    # print(stock_dict)


if __name__ == '__main__':
    # stock = sys.argv[1]
    stock = '1810.HK'
    main(stock)
    print('This is in stock_yahoo.py: ', stock)
