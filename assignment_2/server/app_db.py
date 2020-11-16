import json
import sqlite3
import requests

from flask import Flask, g
from flask_cors import CORS
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

DATABASE = 'my_database.sqlite'
female_news = []


def get_db():
    db_conn = getattr(g, '_database', None)
    if db_conn is None:
        db_conn = g._database = sqlite3.connect(DATABASE)
    return db_conn


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.executescript("""DROP TABLE IF EXISTS FemaleNews""")
        cursor.executescript(
            """CREATE TABLE IF NOT EXISTS FemaleNews
               (id integer primary key,
               title text not null,
               source text not null)"""
        )

        db.commit()


def add_news(female_news):
    wonderzine = requests.get('https://www.wonderzine.com/')
    soup_wonderzine = BeautifulSoup(wonderzine.content, 'html.parser')
    wonderzine_news = soup_wonderzine.find_all('div', {"class": "title"})
    female_news += [(elem.a.text, 'Wonderzine') for elem in wonderzine_news]

    cosmopolitan = requests.get('https://www.cosmo.ru/news/')
    soup_cosmopolitan = BeautifulSoup(cosmopolitan.content, 'html.parser')
    cosmopolitan_news = soup_cosmopolitan.find_all('div', {"class": "article-tile__title-wrapper"})
    female_news += [(elem.h3.text, 'Cosmopolitan') for elem in cosmopolitan_news]

    vogue = requests.get('https://www.vogue.ru/lifestyle')
    soup_vogue = BeautifulSoup(vogue.content, 'html.parser')
    vogue_news = soup_vogue.find_all('a', {"data-test-id": "Hed"})
    female_news += [(elem.text, 'Vogue') for elem in vogue_news]

    female_news.sort(key=lambda x: x[0])


def fill_bd():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        cursor.executemany('INSERT INTO FemaleNews (title,source) VALUES(?,?)', female_news)

        db.commit()

@app.route('/get_all')
def get_all():
    db_cursor = get_db().cursor()
    db_cursor.row_factory = sqlite3.Row
    db_cursor.execute("SELECT * From FemaleNews")
    result = db_cursor.fetchall()
    json_result = json.dumps([dict(row) for row in result])
    return json_result


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    init_db()
    add_news(female_news)
    fill_bd()
    app.run()
