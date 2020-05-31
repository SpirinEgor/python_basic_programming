import json
import sqlite3
import requests
from bs4 import BeautifulSoup


from flask import Flask, g, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE = 'my_database.sqlite'


def extract_news_ya(tag):
    return (tag.a['aria-label'], f"<a href=\"{tag.a['href']}\">Find out more!</a>")


def get_db():
    db_conn = getattr(g, '_database', None)
    if db_conn is None:
        db_conn = g._database = sqlite3.connect(DATABASE)
    return db_conn


def get_news():
    ya = requests.get('https://yandex.ru/')
    html_ya = ya.content
    soup_ya = BeautifulSoup(html_ya, 'html.parser')
    pew_news = []
    for tag in soup_ya.find_all('ol'):
        if (tag.attrs.get("class") is not None and tag.get_attribute_list("class").count("news__list") == 1):
            pew_news.extend(map(extract_news_ya, tag.find_all('li')))

    iw = requests.get('https://www.infowars.com/news/')
    html_iw = iw.content
    soup_iw = BeautifulSoup(html_iw, 'html.parser')
    for tag in soup_iw.find_all('div'):
        if (tag.attrs.get("class") is not None and tag.get_attribute_list("class").count("article-content") == 1):
            link = tag.h3.a
            pew_news.append((link.text.strip(), f"<a href=\"{link['href']}\">Find out more!</a>"))

    bf = requests.get('https://www.buzzfeednews.com/')
    html_bf = bf.content
    soup_bf = BeautifulSoup(html_bf, 'html.parser')
    for tag in soup_bf.find_all('h2'):
        if (tag.attrs.get("class") is not None and tag.get_attribute_list("class").count("newsblock-story-card__title") == 1):
            link = tag.a
            pew_news.append((link.text.strip(), f"<a href=\"{link['href']}\">Find out more!</a>"))

    return pew_news


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.executescript(
            """CREATE TABLE IF NOT EXISTS PewNews
               (id integer primary key, name text not null,
               link text not null)"""
        )

        cursor.executescript(
            """DELETE FROM PewNews"""
        )

        pew_news = get_news()
        cursor.executemany("""INSERT INTO PewNews (name,link) VALUES(?,?);""", pew_news)
        db.commit()


@app.route('/get_all')
def get_all():
    db_cursor = get_db().cursor()
    db_cursor.row_factory = sqlite3.Row
    db_cursor.execute("SELECT * From PewNews")
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
