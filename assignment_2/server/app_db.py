import json
import sqlite3
import requests

from flask import Flask, g
from flask_cors import CORS
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

DATABASE = 'my_database.sqlite'


def get_db():
    db_conn = getattr(g, '_database', None)
    if db_conn is None:
        db_conn = g._database = sqlite3.connect(DATABASE)
    return db_conn


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.executescript(
            """CREATE TABLE IF NOT EXISTS FemaleNews
               (id integer primary key,
               title text not null,
               source text not null)"""
        )

        femaleNews = []

        wonderzine = requests.get('https://www.wonderzine.com/')
        soup_wonderzine = BeautifulSoup(wonderzine.content, 'html.parser')
        wonderzine_news = soup_wonderzine.find_all('div', {"class": "title"})
        for elem in wonderzine_news:
            femaleNews.append((elem.a.text, 'Wonderzine'))


        cosmopolitan = requests.get('https://www.cosmo.ru/news/')
        soup_cosmopolitan = BeautifulSoup(cosmopolitan.content, 'html.parser')
        cosmopolitan_news = soup_cosmopolitan.find_all('a', {"class": "news-section-link"})
        for elem in cosmopolitan_news:
            femaleNews.append((elem.h3.text, 'Cosmopolitan'))


        vogue = requests.get('https://www.vogue.ru/lifestyle')
        soup_vogue = BeautifulSoup(vogue.content, 'html.parser')
        vogue_news = soup_vogue.find_all('h3', {"data-test-id": "Hed"})
        for elem in vogue_news:
            femaleNews.append((elem.text, 'Vogue'))

        femaleNews.sort(key=lambda x: x[0])

        for elem in femaleNews:
            print(elem[0])
            cursor.execute("""INSERT INTO FemaleNews (title,source) VALUES(?,?)""", (elem[0], elem[1]))

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
    app.run()
