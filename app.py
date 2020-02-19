from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import pandas as pd

import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "<h1>Hello Flask!</h1>"

@app.route('/crawler_shopee')
def shopee():
    if 'keyword' in request.args:
        keyword = request.args['keyword']
    else:
        keyword = '筆記型電腦'

    article_arr = crawler_shopee(keyword, 1)
    # print('keyword = ', keyword)
    # print('article_arr = ', article_arr)
    df = pd.DataFrame(article_arr, columns=['name', 'link', 'img', 'sales_volume', 'ad'])  # 使用 columns 調整排列順序
    # print('df = ', df)
    df['sales_volume'] = df['sales_volume'].astype('int')
    df = df.sort_values(by='sales_volume', ascending=False)
    df['key'] = range(1, len(df) + 1) # 增加 index 欄位

    return df.to_json(orient='records', force_ascii=False)

def crawler_shopee(keyword, page):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions
    from selenium.webdriver.common.by import By
    from bs4 import BeautifulSoup
    import time
    import os
    import pymysql.cursors
    import re

    options = Options()
    options.add_argument("window-size=1920,1080")
    options.add_argument("--headless")  # 不要開啟瀏覽器
    # options.add_argument('--no-sandbox')  # 以最高权限运行
    # 谷歌文档提到需要加上这个属性来规避bug
    options.add_argument('--disable-gpu')
    #设置不加载图片
    options.add_argument("blink-settings=imagesEnabled=false")
    driver = webdriver.Chrome('./chromedriver',options=options)
    # driver.maximize_window()  # 瀏覽器視窗設為最大

    try:
        article_arr = []
        
        for i in range(page):
            url = 'https://shopee.tw/search?keyword={0}&page={1}&sortBy=sales'.format(keyword, i)
            
            driver.get(url)

            # 等待選單內容出現
            element = WebDriverWait(driver, 5).until(
                expected_conditions.presence_of_element_located((By.CLASS_NAME, "shopee-search-item-result__item"))
            )

            # 頁面往下滑動
            scroll_height = 0
            scroll_time = 7
            # scroll_time = 3
            for i in range(scroll_time):
                scroll_height += 500
                driver.execute_script('window.scrollTo(0, ' + str(scroll_height) + ');')
                time.sleep(2)

            # 取得內容
            soup = BeautifulSoup(driver.page_source, 'lxml')
            # print(soup)
            host = 'https://shopee.tw'
            articles = soup.select('.shopee-search-item-result__item')
            for article in articles:
                name = article.select('[data-sqe="name"]')[0].text
                link = host + article.select('a')[0]['href']
                img = article.select('a > div > div > img')[0]['src']
                sales_volume = '0' if article.select('[data-sqe="rating"]')[0].next_sibling.text == '' else article.select('[data-sqe="rating"]')[0].next_sibling.text
                sales_volume = re.findall(r'\d+', sales_volume)[0]
                ad = True if len(article.select('[data-sqe="ad"]')) > 0 else False

                article_arr.append({
                    'name': name,
                    'link': link,
                    'img': img,
                    'sales_volume': sales_volume,
                    'ad': ad
                })

        return article_arr
    except Exception as e:
        print(e)
    finally:
        driver.close()
        

if __name__ == '__main__':
  app.config["DEBUG"] = True
  app.config["JSON_AS_ASCII"] = False
  app.run()