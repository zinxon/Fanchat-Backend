import sys
import time
import requests
from selenium import webdriver


def getStockInfo(stock):
    # replace with .Firefox(), or with the browser of your choice
    browser = webdriver.Chrome()
    url = 'https://hk.finance.yahoo.com/quote/{0}/news'.format(stock)
    browser.get(url)  # navigate to the page
    new_list = []
    news = browser.find_element_by_xpath(
        '//*[@id="latestQuoteNewsStream-0-Stream"]/ul').text
    browser.quit()
    print(news)
    return new_list


def main(stock):
    stock_dict = getStockInfo(stock)
    # print(stock_dict)


if __name__ == '__main__':
    # stock = sys.argv[1]
    stock = '1810.HK'
    main(stock)
    print('This is in stock_yahoo.py: ', stock)
