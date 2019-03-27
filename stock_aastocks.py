from requests_html import HTMLSession
import time


def getStockInfo(stock):
    start_time = time.time()
    stockCode = stock.split('.')[0]
    s = '{:05d}'.format(int(stockCode))
    stock_dict = {}
    session = HTMLSession()
    session.browser
    url = 'http://www.aastocks.com/tc/stocks/quote/quick-quote.aspx?symbol={0}'.format(s)
    print(url)
    r = session.get(url)
    r.html.render()
    price = r.html.xpath('//*[@id="b5158c54"]/span/span')
    name = r.html.xpath('//*[@id="SQ_Name"]')
    print(r.html.html)
    # print(name)
    elapsed_time = time.time() - start_time
    print('time: ',elapsed_time,'s')
    return stock_dict


def main(stock):
    stock_dict = getStockInfo(stock)
    # print(stock_dict)


if __name__ == '__main__':
    # stock = sys.argv[1]
    stock = '0700.HK'
    main(stock)
    print('This is in stock_yahoo.py: ', stock)
