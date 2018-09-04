from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import re
from pyquery import PyQuery as pq
#import config
import pymongo
import os
import requests
from hashlib import md5 
from urllib.parse import urlencode
import config
client = pymongo.MongoClient(config.MONGO_URL)
db = client[config.MONGO_DB]
#opt = webdriver.ChromeOptions()
#opt.set_headless()
#driver = webdriver.Chrome(options=opt)
#driver = webdriver.Chrome()
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(chrome_options=chrome_options)
wait = WebDriverWait(driver,6)
def search():
    try:
        driver.get("https://www.taobao.com")
        input = wait.until(
          EC.presence_of_element_located((By.CSS_SELECTOR,"#q"))             
        )
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#J_TSearchForm > div.search-button > button")))
        input.send_keys("滑板")
        submit.click()
        total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"#mainsrp-pager > div > div > div > div.total")))
        prodects()
        return total.text 
    except TimeoutError:
        return search()                          
def next_page(page_number):
    try:
        input = wait.until(
              EC.presence_of_element_located((By.CSS_SELECTOR,"#mainsrp-pager > div > div > div > div.form > input"))             
            )
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit")))
        input.clear()
        input.send_keys(page_number)
        submit.click()
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,"#mainsrp-pager > div > div > div > ul > li.item.active > span"),str(page_number)))
        prodects()
    except TimeoutError:
        return next_page(page_number)
    
def prodects():
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,"#mainsrp-itemlist .items .item")))
    html = driver.page_source
    doc = pq(html)  
    items = doc("#mainsrp-itemlist .items .item").items()                                      
    for item in items:
        product = {
            'image':item.find('.pic .img').attr('src'),
            'price':item.find('.price').text(),
            'deal':item.find('.deal-cnt').text()[:-3],
            'title':item.find('.title').text(),
            'shop':item.find('.shop').text(),
            'location':item.find('.location').text()
        }     
        save_to_mongo(product)
        def parse_image(product['image'],product['title']):
#解析图片地址
def parse_image(url,title):
    print("正在解析图片","https:"+ str(url))
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}

    try:
        response = requests.get("https:"+ str(url),headers=headers)
        if response.status_code == 200:
            if response.content:
                save_image_to_file(response.content,title)
            return response.content
        return None
    except:
        print("图片解析失败")
        
    
#保存图片到本地
def save_image_to_file(content,title):
    if content:
        print("正在保存图片",title)
        titles = "淘宝"
        if not os.path.exists(titles):  #如果文件夹不存在就创建
            os.mkdir(titles)
        try:
            file_path = '{0}/{1}.{2}'.format(titles,md5(content).hexdigest(),'jpg')
            if not os.path.exists(file_path):
                with open(file_path,'wb') as f:
                    f.write(content) 
                    f.close()
                   
        except Exception:
            print("保存图片失败")
    else:
        print("None")

#保存到mongo数据库    
def save_to_mongo(result):
    try:
        if db[config.MONGO_TABLE].insert(result):
            print('存储数据到数据库成功',result)
    except Exception:
        print("存储到数据库错误！",result)
def main():
    try:
        total = search()
        total = int(re.compile("(\d+)").search(total).group(1))
        for i in range(2,total+1):
            next_page(i)
    except Exception as e:
        print("错误",e)
    finally:
        driver.close()
  

if __name__ == "__main__":
    main()
                                                    
                                                    
                                                    
                                                    
                                                    
                                    
                                                    
