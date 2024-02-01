from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
# Set up the Chrome WebDriver (you need to download chromedriver.exe and specify its path)
driver = webdriver.Chrome()

# Open the webpage
url = 'https://eadaily.com/ru/news/economics/'
driver.get(url)

# Ждем, чтобы страница полностью загрузилась
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "content_column")))

# Нажимаем кнопку 10 раз
for i in range(3):
    try:
        # Find and click the button to load content (replace 'your_button_locator' with the actual locator)
        button_locator = (By.XPATH, '//*[@id="content_column"]/div[5]/div[1]/a')
        button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(button_locator))
        button.click()
    except (TimeoutException, NoSuchElementException):
        print("rrrrrrr")
        break
    finally:
        print("sdhsajhfjkhs")
        # Ждем, чтобы страница обновилась после нажатия кнопки
        time.sleep(2)

from ast import parse
from selenium import webdriver
import selenium.common.exceptions as seleniumExceptions
# import chromedriver_binary
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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



driver.get(url)
element = driver.find_element(By.CSS_SELECTOR, "div.two-columns")
ul = element.find_elements(By.CSS_SELECTOR, "ul.news-feed > li")

category_massiv = ["экономика"]
site_massiv = ["eadaily.com"]
location_massiv = ["Россия"]
next_div = 0

elements = driver.find_elements(By.CSS_SELECTOR, "ul.news-feed > li")
next_div = 0
while next_div < len(elements):
    try:
        a = elements[next_div].find_element(By.CSS_SELECTOR, "a").get_attribute("href")
        driver.get(a)

        head = driver.find_element(By.CSS_SELECTOR, "div.two-columns")
        title_web = head.find_element(By.CSS_SELECTOR, "h1")
        
        title = title_web.text
        print(title)
        datetime_element = driver.find_element(By.CSS_SELECTOR, 'time[itemprop="datePublished"]')
        datetime_text = datetime_element.get_attribute('datetime')
       
        date, time_with_timezone = datetime_text.split('T')

        print(date)
        content_div= driver.find_elements (By.CSS_SELECTOR, "div.news-text-body > p")
        text_list = [div.text for div in content_div]
        content = cleaner(text_list)
        start_index = content.find("['") + 2
        end_index = content.find("']</div>")
        list_of_strings = content[start_index:end_index].split("', '")
        result_string = ' '.join(list_of_strings)
        content = result_string
        print(content)
        # content_div= div.find_element(By.CSS_SELECTOR, "div.article__body-text")
        # content = content_div.text
        # print(content)
        conn = psycopg2.connect(dbname='diplom', user='postgres', 
                    password='marzhan', host='localhost')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM category WHERE name='%s'"%category_massiv[0])
        result_category=cursor.fetchall()
        print("fsdscfvhsdnfm,sm")
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
        driver.get(url)
        elements = driver.find_elements(By.CSS_SELECTOR, "ul.news-feed > li")
    
