import requests
from bs4 import BeautifulSoup
import re
import psycopg2
import lxml
from lxml.html.clean import Cleaner



class ZakonKzParser:
    def __init__(self):
        self.catpage_massiv = []
        self.item_href_massiv = []
        self.news = []
        self.category_massiv = ["экономика"]
        self.site_massiv = ["zakon.kz"]
        self.location_massiv = ["Казахстан"]
        self.main_url = "https://www.zakon.kz"
        self.page_url = "https://www.zakon.kz/ekonomika-biznes/"


    def cleaner(self, x):
        cleaner = Cleaner()
        cleaner.remove_tags = ['a', 'p', 'div', '<div>', 'span', 'blockquote','li']
        cleaner.javascript = True # This is True because we want to activate the javascript filter
        cleaner.style = True      # This is True because we want to activate the styles & stylesheet filter

        cleaned_text = cleaner.clean_html(str(x))

        readalso_index = cleaned_text.index("Читайте также")
        cleaned_text = cleaned_text[:readalso_index]
        return cleaned_text
  

    def begin_parse(self):   
        response = requests.get(self.page_url)
        response_text = response.text
        soup = BeautifulSoup(response_text, "html.parser")
        paginationList = soup.find("div", {"class": "paginationWrap"})
        paginationLi = paginationList.find_all("li")
        for li in paginationLi:
            li_href = li.find('a')
            li_href = self.main_url+li_href['href']
            response = requests.get(li_href)
            response_text = response.text
            soup = BeautifulSoup(response_text, "html.parser")
            catpagenews = soup.find("div", {"class": "zmainCard"})
            catpageCard = catpagenews.find_all("div", {"class": "zmainCard_item card_md"})
            for item in catpageCard:
                item_href = item.find('a')
                item_href=self.main_url+item_href['href']
                response = requests.get(item_href)
                response_text = response.text
                soup = BeautifulSoup(response_text, "html.parser")
                newslist = soup.find("section", {"class": "article"})
                content = newslist.find("div", {"class": "z-row"})
                listcontent = content.find("div", {"class": "z-col-lg-8 z-col-md-9"})
                article = listcontent.find("div", {"class": "articleBlock"})
                title = article.find("h1").text
                newscontent = article.find("div", {"class":"content"})
                contentNews = self.cleaner(newscontent)
                date = article.find("time", {"class": "date"})
                datetime = date['datetime']
                conn = psycopg2.connect(dbname='diplom', user='postgres', 
                    password='cao95records', host='localhost')
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM category WHERE name='%s'"%self.category_massiv[0])
                result_category=cursor.fetchall()
                if len(result_category) > 0:
                    print("gbg")
                else:
                    cursor.execute(f"INSERT INTO category (name) VALUES ('%s')"%self.category_massiv[0])
                cursor.execute("SELECT * FROM site WHERE name='%s'"%self.site_massiv[0])
                result_site = cursor.fetchall()
                if len(result_site) > 0:
                    print("gbg")
                else:
                    cursor.execute(f"INSERT INTO site (name) VALUES ('%s')"%self.site_massiv[0])
                cursor.execute("SELECT * FROM location  WHERE name='%s'"%self.location_massiv[0])
                result_location = cursor.fetchall()
                if len(result_location) > 0:
                    print("gbg")
                else:
                    cursor.execute(f"INSERT INTO location (name) VALUES ('%s')"%self.location_massiv[0])
                cursor.execute("SELECT id FROM category  WHERE name='%s'"%self.category_massiv[0])
                id_category = cursor.fetchone()
                id_category=id_category[0]
                cursor.execute("SELECT id FROM site  WHERE name='%s'"%self.site_massiv[0])
                id_site = cursor.fetchone()
                id_site=id_site[0]
                cursor.execute("SELECT id FROM location  WHERE name='%s'"%self.location_massiv[0])
                id_location=cursor.fetchone()
                id_location=id_location[0]

                news_massiv = (title, datetime, contentNews, id_category, id_location, id_site)
                cursor.execute("INSERT INTO news (title, date, content, category_id, location_id, site_id) VALUES ('%s', '%s','%s','%s','%s','%s')"%(news_massiv[0],news_massiv[1],news_massiv[2].replace('\'', '-'),news_massiv[3],news_massiv[4],news_massiv[5]), is_insert=True)
                conn.commit()

                cursor.close()
                conn.close()

        