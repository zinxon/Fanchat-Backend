from requests_html import HTMLSession
from opencc import OpenCC
import sys


def getStockInfo(stock):
    cc = OpenCC('s2t')
    stockCode = stock.split('.')[0]
    s = '{:05d}'.format(int(stockCode))
    session = HTMLSession()
    session.browser
    url = 'http://stock.finance.sina.com.cn/hkstock/quotes/{0}.html'.format(s)
    stock_dict = {}
    r = session.get(url)
    r.html.render()
    name = r.html.find('#stock_cname', first=True)
    price = r.html.find('#mts_stock_hk_price', first=True)
    stockQuan = r.html.find('div.deta03', first=True).find('ul')[
        1].find('li')[3]
    news = r.html.find('#js_ggzx', first=True).find('a')
    # print("{0} ({1})".format(cc.convert(name.text), s))
    # print(price.text)
    # print(cc.convert(stockQuan.text))
    for new in news:
        print(new.text, new.links)
    stock_dict = {'stock_name': cc.convert(name.text), 'stock_code': s,
                  'stock_price': price.text, 'stock_quan': cc.convert(stockQuan.text), 'news': news}
    return stock_dict


def main(stock):
    stock_dict = getStockInfo(stock)
    print("{0} ({1})".format(
        stock_dict['stock_name'], stock_dict['stock_code']))
    print(stock_dict['stock_price'])
    print(stock_dict['stock_quan'])
    # print(stock_dict)


if __name__ == '__main__':
    stock = sys.argv[1]
    main(stock)
    print('This is in stock.py: ', stock)
