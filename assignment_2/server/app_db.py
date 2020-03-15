#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
import json
import re
import sqlite3

import requests
from bs4 import BeautifulSoup
from flask import Flask, g, redirect
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE = 'my_database.sqlite'
app.secret_key = "super secret key"


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
            """CREATE TABLE IF NOT EXISTS Items
               (id integer primary key,
               name text not null,
               brand text not null,
               site text not null,
               price integer)"""
        )
        db.commit()


@app.route('/get_all')
def get_all():
    db_cursor = get_db().cursor()
    db_cursor.row_factory = sqlite3.Row
    db_cursor.execute("SELECT * From Items")
    result = db_cursor.fetchall()
    json_result = json.dumps([dict(row) for row in result])
    return json_result


def create_new_item(data, site):
    db_conn = get_db()
    for i in data:
        user_json = json.loads(i)
        try:
            for key in ['shortName', 'brandName', 'price']:
                assert key in user_json, f'{key} not found in the request'
            query = f"INSERT INTO Items (name, brand, site, price) VALUES ('{user_json['shortName']}', '{user_json['brandName']}', '{site}', {user_json['price']});"
            db_conn.execute(query)
        except AssertionError:
            continue
    db_conn.commit()


def parse_citilink():
    citilink = "https://www.citilink.ru/catalog/mobile/smartfony/-premium/?available=1&status=55395790&p=2"
    r = requests.get(citilink)
    html = r.content
    soup = BeautifulSoup(html, "lxml")
    data = [item['data-params'] for item in soup.find_all('div', attrs={'data-params': True})]
    create_new_item(data, 'Citilink')


def parse_wildberries():
    wildberries = "https://www.wildberries.ru/catalog/0/search.aspx?search=%D0%BC%D1%83%D0%B6%D1%81%D0%BA%D0%B8%D0%B5%20%D1%87%D0%B5%D1%80%D0%BD%D1%8B%D0%B5%20%D0%B4%D0%B6%D0%B8%D0%BD%D1%81%D1%8B&sort=popular"
    r = requests.get(wildberries)
    html = r.content
    soup = BeautifulSoup(html, "lxml")
    data = list()
    names = map(lambda x: x.string, soup.find_all('span', class_="goods-name"))
    brand_names = map(lambda x: x.contents[0], soup.find_all("strong", {"class": "brand-name"}))
    prices = map(lambda x: re.sub("\D", "", x.string), soup.find_all("ins", class_='lower-price'))
    for name, brand_name, price in zip(names, brand_names, prices):
        name = name.replace('"', "")
        brand_name = brand_name.replace("'", "")
        json_model = f'{{"shortName":" {name} ","brandName": " {brand_name} ", "price": {price} }}'
        data.append(json_model)
    create_new_item(data, 'Wildberries')


@app.route('/', methods=['GET', 'POST'])
def add_parser_site():
    parse_citilink()
    parse_wildberries()
    return redirect('/get_all')


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
