from ast import parse
from selenium import webdriver
import selenium.common.exceptions as seleniumExceptions
# import chromedriver_binary
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, json, logging, datetime
import logging
from fake_useragent import UserAgent
import random
from datetime import datetime
from lxml.html.clean import Cleaner
import psycopg2
from selenium.common.exceptions import NoSuchElementException

def cleaner(x):
    cleaner = Cleaner()
    cleaner.remove_tags = ['a', 'p', 'div', 'figure', '<div>', 'span', 'blockquote','li', '[', ']']
    cleaner.javascript = True # This is True because we want to activate the javascript filter
    cleaner.style = True      # This is True because we want to activate the styles & stylesheet filter
    cleaned_text = cleaner.clean_html(str(x))

    return cleaned_text

# op = webdriver.ChromeOptions()
# # op.add_argument('headless')
# # op.add_argument('disable-gpu')
# ua = UserAgent()
driver = webdriver.Chrome()
first_href = 'https://kapital.kz/economic'
driver.get(first_href)
element = driver.find_element(By.CSS_SELECTOR, "main.main__contant")
ul = element.find_elements(By.XPATH, "//*[@id='main-container']/main/main/div[2]/ul[1]/li[1]")
href = []
i = 0
catpage_massiv = []
category_massiv = ["экономика"]
site_massiv = ["kapital.kz"]
location_massiv = ["Казахстан"]
url = 'https://kapital.kz'

while True:
    elements = driver.find_elements(By.CSS_SELECTOR, "div.main-news > article")
    next_div = 0
    while next_div < len(elements):
        # a = "https://www.inform.kz/ru/oficial-no-zapuschen-zheleznodorozhnyy-onlayn-portal-kitay-evropa_a4112335"
        try:
            a = elements[next_div].find_element(By.CSS_SELECTOR, "a.main-news__name").get_attribute("href")
            print("hjghxghcv",a)
            driver.get(a)
            error_exists = driver.find_elements(By.CSS_SELECTOR, "div.error__wrapper")

            if error_exists != []:
                next_div += 1
                driver.get(first_href)
                elements = driver.find_elements(By.CSS_SELECTOR, "div.catpage__news > div")
                continue
            # div = driver.find_element(By.XPATH, "//*[@id='main-container']/main[1]/main/div[3]/article")  
            time_element = driver.find_element(By.CLASS_NAME, 'information-article__date')
            dateFirst = time_element.text
            splited_date = dateFirst.split('.')
            date_format = splited_date[1:4]

            clean_date_str = dateFirst.replace(" · ", ".")
            splited_date = clean_date_str.split('.')
            date = str(splited_date[2])+"-"+str(splited_date[1])+"-"+str(splited_date[0])
            head = driver.find_element(By.CSS_SELECTOR, "header.article__header")
            title_web = head.find_element(By.CSS_SELECTOR, "h1")
            title = title_web.text
            print(title)
            content_div= driver.find_elements (By.CSS_SELECTOR, "div.article__body > div")
            text_list = [div.text for div in content_div]
            content = cleaner(text_list)
            start_index = content.find("['") + 2
            end_index = content.find("']</div>")
            list_of_strings = content[start_index:end_index].split("', '")
            result_string = ' '.join(list_of_strings)
            content = result_string
            
            conn = psycopg2.connect(dbname='diplom', user='postgres', 
                        password='marzhan', host='localhost')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM category WHERE name='%s'"%category_massiv[0])
            result_category=cursor.fetchall()
            if len(result_category) > 0:
                print("gbg")
            else:
                cursor.execute(f"INSERT INTO category (name) VALUES ('%s')"%category_massiv[0])
            cursor.execute("SELECT * FROM site WHERE name='%s'"%site_massiv[0])
            result_site = cursor.fetchall()

            if len(result_site) > 0:
                print("gbg")
            else:
                cursor.execute(f"INSERT INTO site (name) VALUES ('%s')"%site_massiv[0])

            cursor.execute("SELECT * FROM location  WHERE name='%s'"%location_massiv[0])
            result_location = cursor.fetchall()
            if len(result_location) > 0:
                print("gbg")
            else:
                cursor.execute(f"INSERT INTO location (name) VALUES ('%s')"%location_massiv[0])

            cursor.execute("SELECT id FROM category  WHERE name='%s'"%category_massiv[0])
            id_category = cursor.fetchone()
            id_category=id_category[0]
            cursor.execute("SELECT id FROM site  WHERE name='%s'"%site_massiv[0])
            id_site = cursor.fetchone()
            id_site=id_site[0]

            cursor.execute("SELECT id FROM location  WHERE name='%s'"%location_massiv[0])
            id_location=cursor.fetchone()
            id_location=id_location[0]

            news_massiv = (title, date, content, id_category, id_location, id_site)
            cursor.execute("INSERT INTO news (title, date, content, category_id, location_id, site_id) VALUES ('%s', '%s','%s','%s','%s','%s')"%(news_massiv[0].replace('\'', '-'),news_massiv[1],news_massiv[2].replace('\'', '-'),news_massiv[3],news_massiv[4],news_massiv[5]))

            print("FFFFFFFFF:", news_massiv)


            conn.commit()
            
            cursor.close()
            conn.close()
        except Exception as e:
            print("Error occured: ", e)
        finally:
            next_div += 1
            driver.get(first_href)
            elements = driver.find_elements(By.CSS_SELECTOR, "div.main-news > article")
      

    element = driver.find_element(By.CSS_SELECTOR, "main.main__contant")

    ul = element.find_elements(By.CSS_SELECTOR, "ul.pagination > li")

    first_href = ul[-1].find_element(By.CSS_SELECTOR, "a").get_attribute('href')

    a = ul[-1].find_element(By.CSS_SELECTOR, "a").get_attribute('href')

    if first_href is None:
        break

    driver.get(a)


time.sleep(10000)
last_page = 0