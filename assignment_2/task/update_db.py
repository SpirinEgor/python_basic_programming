import sqlite3
from time import sleep
from types import SimpleNamespace

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Firefox

from common_db import DATABASE, convert_title
import col_mangachan
import col_mangafox



def add_title(info):
    print(info)
    data.cursor.execute(f''' INSERT INTO Titles (title, link, cover) VALUES ("{convert_title(info.title)}", "{info.link}", "{info.cover}") ''')
    no = data.cursor.lastrowid
    data.cursor.execute(f''' CREATE TABLE Chapters{no}
                            ( link ntext not null
                            , volume integer
                            , chapter integer
                            )''')
    return no

def update_chapters(collector, info, t_id):
    data.driver.get(info.link)
    page = data.driver.find_element_by_tag_name('body')

    for chapter in collector.get_chapters(page):
        print(chapter)
        data.cursor.execute(f''' INSERT INTO Chapters{t_id}
                                (link, volume, chapter)
                            VALUES
                                ("{chapter.link}", "{chapter.volume}", "{chapter.chapter}") ''')

def update_title(collector, info):
    print(info.link)

    data.cursor.execute(f''' SELECT id FROM Titles WHERE link="{info.link}" ''')

    t_id = data.cursor.fetchone()

    if t_id is None:
        t_id = add_title(info)
        update_chapters(collector, info, t_id)
        data.db.commit()
    else:
        t_id = t_id[0]
    

def update_source(collector):
    data.driver.get(collector.base_url)

    cnt = 0

    for info in collector.get_links(data):
        update_title(collector, info)
        cnt += 1
        
        if cnt == 200:
            fini_driver()
            init_driver()
            cnt = 0

def update_all():
    init_db()
    init_driver()
    for collector in [col_mangachan.collector(), col_mangafox.collector()]:
        update_source(collector)
    fini_driver()
    fini_db()

def init_driver():
    data.driver = Firefox()

def fini_driver():
    data.driver.close()
    data.driver.quit()

def init_db():
    data.db = sqlite3.connect(DATABASE)
    data.cursor = data.db.cursor()
    data.cursor.execute(
        ''' CREATE TABLE IF NOT EXISTS Titles
                ( id integer primary key
                , title ntext not null
                , link ntext not null
                , cover ntext not null
                )''')
    data.db.commit()

def fini_db():
    data.db.close()

data = SimpleNamespace()

update_all()
