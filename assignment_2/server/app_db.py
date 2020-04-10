import json
import sqlite3
import requests

from flask import Flask, g, request
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
            """CREATE TABLE IF NOT EXISTS University
               (id integer primary key, university text not null,
               menuItem text not null, link text not null)"""
        )

        db.commit()


def fill_spbu():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        spbu = requests.get('https://spbu.ru/news-events')
        spbu_html = spbu.content
        spbu_soup = BeautifulSoup(spbu_html, 'html.parser')
        for item in spbu_soup.find_all('li', {"class": "menu-item"}):
            cursor.execute("""INSERT INTO University
                           (university, menuItem, link) VALUES(?,?,?);""",
                           ("SPBU", item.a.text, item.a['href']))

        db.commit()


def fill_msu():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        msu = requests.get('https://www.msu.ru/')
        msu_html = msu.content
        msu_soup = BeautifulSoup(msu_html, 'html.parser')
        ul = msu_soup.find_all('ul', {"class": "nav"})[0]
        for item in ul.find_all('a'):
            cursor.execute("""INSERT INTO University
                           (university, menuItem, link) VALUES(?,?,?);""",
                           ("MSU", item.text, item['href']))

        db.commit()


@app.route('/get_all')
def get_all():
    db_cursor = get_db().cursor()
    db_cursor.row_factory = sqlite3.Row
    db_cursor.execute("SELECT * From University")
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
    fill_spbu()
    fill_msu()
    app.run()

