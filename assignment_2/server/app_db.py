import json
import sqlite3
import requests
from bs4 import BeautifulSoup

from flask import Flask, g, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

DATABASE = 'my_database.sqlite'
products = []


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
            """CREATE TABLE IF NOT EXISTS Products
            (id integer primary key,
            shop text not null,
            name text not null)"""
        )

        db.commit()


def add_xiaomi():
    xiaomi = requests.get('https://www.mi.com/ru/list/')
    mi_soup = BeautifulSoup(xiaomi.content, 'html.parser')
    mi_products = mi_soup.find_all('a', {"class": "product-name"})
    for prod in mi_products:
        if not prod.text.startswith("https://www.mi.com/ru/list/"):
            products.append(('Xiaomi', prod.text))


def add_ozon():
    ozon = requests.get('https://www.svyaznoy.ru/catalog/phone/225')
    oz_soup = BeautifulSoup(ozon.content, 'html.parser')
    oz_products = oz_soup.find_all('div', {"class": "s-menu-el"})
    for prod in oz_products:
        if prod.a.get('href').startswith("/catalog/phone/225/"):
            products.append(('Ozon', prod.a.text))


def fill_bd():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        for prod in products:
            print(prod[1])
            cursor.execute(f"""INSERT INTO Products
                (shop,name) VALUES
                ('{prod[0]}', '{prod[1]}');""")
        db.commit()


@app.route('/get_all')
def get_all():
    db_cursor = get_db().cursor()
    db_cursor.row_factory = sqlite3.Row
    db_cursor.execute("SELECT * From Products")
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
    add_xiaomi()
    add_ozon()
    fill_bd()
    app.run()
