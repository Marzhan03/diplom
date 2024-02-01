import dotenv, os
dotenv.load_dotenv()
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from lxml.html.clean import Cleaner
from DAL import DAL



class KazInform:
    def __init__(self):
        self.category_massiv = ["экономика"]
        self.site_massiv = "kazInform"
        self.location = os.getenv("LOCATION")
        self.first_href = os.getenv("INFORM_FIRST_HREF")
        self.driver = webdriver.Chrome()
        self.next_div = 0
        self.dal = DAL()

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
        cleaner.remove_tags = ['a', 'p', 'div', 'figure', '<div>', 'span', 'blockquote','li', '[', ']']
        cleaner.javascript = True # This is True because we want to activate the javascript filter
        cleaner.style = True      # This is True because we want to activate the styles & stylesheet filter
        cleaned_text = cleaner.clean_html(str(x))

        return cleaned_text
    
    def parse(self):
        self.driver.get(self.first_href)
        while True:
            print("dssafdsf")
            elements = self.driver.find_elements(By.CSS_SELECTOR, "div.catpage__news > div")
            while self.next_div < len(elements):
                try:
                    a = elements[self.next_div].find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    print("hjghxghcv",a)
                    self.driver.get(a)
                    error_exists = self.driver.find_elements(By.CSS_SELECTOR, "div.error__wrapper")

                    if error_exists != []:
                        self.next_div += 1
                        self.driver.get(self.first_href)
                        elements = self.driver.find_elements(By.CSS_SELECTOR, "div.catpage__news > div")
                        continue

                    div = self.driver.find_element(By.CSS_SELECTOR, "div.article__body")
                    dateFirst = div.find_element(By.CSS_SELECTOR, "div.article__time")
                    dateFirst_text = dateFirst.text
                    splited_date = dateFirst_text.split(' ')
                    date_format = splited_date[1:4]
                    months = {
                        "Январь": 1, "Февраль": 2, "Март": 3, "Апрель": 4, "Май": 5, "Июнь": 6,
                        "Июль": 7, "Август": 8, "Сентябрь": 9, "Октябрь": 10, "Ноябрь": 11, "Декабрь": 12
                    }
                    month_num = months[date_format[1]]
                    date = str(date_format[2])+"-"+str(month_num)+"-"+str(date_format[0])
                    head = div.find_element(By.CSS_SELECTOR, "div.article__head")
                    title_web = head.find_element(By.CSS_SELECTOR, "h1")
                    title = title_web.text
                    content_div= div.find_element(By.CSS_SELECTOR, "div.article__body-text")
                    content = content_div.text
                    print(title)
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
                    elements = self.driver.find_elements(By.CSS_SELECTOR, "div.catpage__news > div")
            

            element = self.driver.find_element(By.CSS_SELECTOR, "section.catpage")

            ul = element.find_elements(By.XPATH, "/html/body/main/section/div/div/div[1]/ul[2]/li")

            first_href = ul[-1].find_element(By.CSS_SELECTOR, "a").get_attribute('href')

            a = ul[-1].find_element(By.CSS_SELECTOR, "a").get_attribute('href')

            if first_href is None:
                break

            self.driver.get(a)


        time.sleep(10000)
