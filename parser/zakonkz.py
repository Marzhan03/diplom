import dotenv, os
dotenv.load_dotenv()
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from lxml.html.clean import Cleaner
from DAL import DAL
import re



class Zakon:
    print("fdlsadfl")
    def __init__(self):
        self.category_massiv = ["экономика"]
        self.site_massiv = "zakon.kz"
        self.location = os.getenv("LOCATION")
        self.first_href = os.getenv("ZAKON_FIRST_HREF")
        self.url = os.getenv("ZAKON_URL")
        self.driver = webdriver.Chrome()
        self.next_div = 0
        self.i = 2
        self.dal = DAL()
        self.match = 5

    def check_existence(self, table, column, field):
        result = self.dal.select(table, column, where="name='%s'"%field, fetch=True)

        if len(result) > 0:
            print("gbg")
        else:
            self.dal.insert(table, 'name', field)

        id = self.dal.select(table, column, where="name='%s'"%field, fetch=False)
        id = id[0]

        return id

    def cleaner(self, x):
        cleaner = Cleaner()
        cleaner.remove_tags = ['a', 'p', 'div', '<div>', 'span', 'blockquote','li']
        cleaner.javascript = True # This is True because we want to activate the javascript filter
        cleaner.style = True      # This is True because we want to activate the styles & stylesheet filter
        cleaned_text = cleaner.clean_html(str(x))
        readalso_index = cleaned_text.index("Читайте также")
        cleaned_text = cleaned_text[:readalso_index]
        return cleaned_text
    
    def parse(self):
        self.driver.get(self.first_href)
        while True:
            print("dkflsdj")
            elements = self.driver.find_elements(By.CSS_SELECTOR, "div.zmainCard > div")
            while self.next_div < len(elements):
                try:
                    print(self)
                    a = elements[self.next_div].find_element(By.TAG_NAME, "a").get_attribute("href")
                    self.driver.get(a)
                    title = self.driver.find_element(By.CSS_SELECTOR, "div.articleBlock > h1").text
                    print("wwwwwwww", title)
                    newscontent = self.driver.find_element(By.CSS_SELECTOR, "div.content").text
                    content = self.cleaner(newscontent)
                    print(content)
                    date = self.driver.find_element(By.CSS_SELECTOR,"time.date").text
                    months = {
                    'января': '01',
                    'февраля': '02',
                    'марта': '03',
                    'апреля': '04',
                    'мая': '05',
                    'июня': '06',
                    'июля': '07',
                    'августа': '08',
                    'сентября': '09',
                    'октября': '10',
                    'ноября': '11',
                    'декабря': '12'
                    }
                    time_str, date_str = date.split(', ')
                    day, month, year = date_str.split()
                    month = months[month]

                    date = str(year)+"-"+str(month)+"-"+str(day)
                   
                    self.dal.connection_open()
                    id_category = self.check_existence("category", "*", self.category_massiv[0])
                    id_site= self.check_existence("site", "*", self.site_massiv)
                    id_location=self.check_existence("location", "*", self.location)
                    news_massiv = (title, date, content, id_category, id_location, id_site)
                    column_names = 'title, date, content, category_id, location_id, site_id'
                    values = (
                        news_massiv[0].replace('\'', '-'),
                        news_massiv[1],
                        news_massiv[2].replace('\'', '-'),
                        news_massiv[3],
                        news_massiv[4],
                        news_massiv[5]
                    )
                    self.dal.insert("news", column_names, *values)
                    self.dal.connection_close()
                except Exception as e:
                    print("Error occured: ", e)
                finally:
                    self.next_div += 1
                    self.driver.get(self.first_href)
                    elements = self.driver.find_elements(By.CSS_SELECTOR, "div.zmainCard > div")
            
            print("kdfsfhsdjgfsdhj")
            element = self.driver.find_element(By.XPATH, "/html/body/section/div/div[3]")

            ul = element.find_elements(By.CSS_SELECTOR, "ul.pagination > li")
            self.first_href = ul[-1].find_element(By.CSS_SELECTOR, "a").get_attribute('href')
            self.match = re.search(r'\?p=(\d+)', self.first_href)
            
            
            a="https://www.zakon.kz/ekonomika-biznes/?p="+str(self.i)
            print(a)
            self.i=self.i+1
            if self.i == self.match:
                break
            self.driver.get(a)
            self.next_div = 0
            print(self.driver)



        
