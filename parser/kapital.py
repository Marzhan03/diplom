import dotenv, os
dotenv.load_dotenv()
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from lxml.html.clean import Cleaner
from DAL import DAL



class Kapital:
    def __init__(self):
        self.category_massiv = ["экономика"]
        self.site_massiv = "kapital.kz"
        self.location = os.getenv("LOCATION")
        self.first_href = os.getenv("KAPITAL_FIRST_HREF")
        self.url = os.getenv("KAPITAL_URL")
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
        element = self.driver.find_element(By.CSS_SELECTOR, "main.main__contant")
        ul = element.find_elements(By.XPATH, "//*[@id='main-container']/main/main/div[2]/ul[1]/li[1]")
        while True:
            elements = self.driver.find_elements(By.CSS_SELECTOR, "div.main-news > article")
            while self.next_div < len(elements):
                try:
                    a = elements[self.next_div].find_element(By.CSS_SELECTOR, "a.main-news__name").get_attribute("href")
                    print("hjghxghcv",a)
                    self.driver.get(a)
                    error_exists = self.driver.find_elements(By.CSS_SELECTOR, "div.error__wrapper")

                    if error_exists != []:
                        self.next_div += 1
                        self.driver.get(self.first_href)
                        elements = self.driver.find_elements(By.CSS_SELECTOR, "div.catpage__news > div")
                        continue

                    time_element = self.driver.find_element(By.CLASS_NAME, 'information-article__date')
                    dateFirst = time_element.text
                    clean_date_str = dateFirst.replace(" · ", ".")
                    splited_date = clean_date_str.split('.')
                    date = str(splited_date[2])+"-"+str(splited_date[1])+"-"+str(splited_date[0])
                    head = self.driver.find_element(By.CSS_SELECTOR, "header.article__header")
                    title_web = head.find_element(By.CSS_SELECTOR, "h1")
                    title = title_web.text
                    content_div= self.driver.find_elements (By.CSS_SELECTOR, "div.article__body > div")
                    text_list = [div.text for div in content_div]
                    content = self.cleaner(text_list)
                    start_index = content.find("['") + 2
                    end_index = content.find("']</div>")
                    list_of_strings = content[start_index:end_index].split("', '")
                    result_string = ' '.join(list_of_strings)
                    content = result_string
                    
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
                    elements = self.driver.find_elements(By.CSS_SELECTOR, "div.main-news > article")
            

            element = self.driver.find_element(By.CSS_SELECTOR, "main.main__contant")

            ul = element.find_elements(By.CSS_SELECTOR, "ul.pagination > li")

            self.first_href = ul[-1].find_element(By.CSS_SELECTOR, "a").get_attribute('href')

            a = ul[-1].find_element(By.CSS_SELECTOR, "a").get_attribute('href')

            if self.first_href is None:
                break

            self.driver.get(a)


        time.sleep(10000)
