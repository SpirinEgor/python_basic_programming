#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
import json
import sqlite3
import requests
import re

from bs4 import BeautifulSoup
from flask import Flask, g, request, url_for, redirect, flash, render_template, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE = 'my_database.sqlite'
app.secret_key = "super secret key"
pattern = "\www.(.*?)\."


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
            """CREATE TABLE IF NOT EXISTS Users
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
    db_cursor.execute("SELECT * From Users")
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
            query = f"INSERT INTO Users (name, brand, site, price) VALUES ('{user_json['shortName']}', '{user_json['brandName']}', '{site}', {user_json['price']});"
            db_conn.execute(query)
        except AssertionError:
            continue
    db_conn.commit()
    db_conn.close()


def parse_site(ref):
    r = requests.get(ref)
    html = r.content
    soup = BeautifulSoup(html, "lxml")
    site = re.findall(pattern, ref)[0]
    data = ""
    if site == "citilink":
        data = [item['data-params'] for item in soup.find_all('div', attrs={'data-params': True})]
    elif site == "wildberries":
        data = list()
        names = list(map(lambda x: x.string, soup.find_all('span', class_="goods-name")))
        brand_names = list(map(lambda x: x.contents[0], soup.find_all("strong", {"class": "brand-name"})))
        prices = list(map(lambda x: re.sub("\D", "", x.string), soup.find_all("ins", class_='lower-price')))
        for name, brandName, price in zip(names, brand_names, prices):
            json_model = '{"shortName":"' + name.replace('"',
                                                         "") + '","brandName":"' + brandName.replace("'", "") + '","price":' + price + "}"
            data.append(json_model)
    create_new_item(data, site)


@app.route('/', methods=['GET', 'POST'])
def add_parser_site():
    if request.method == "POST":
        ref_of_site = request.form['name']
        # ref_of_site = "https://www.citilink.ru/catalog/mobile/smartfony/-premium/?available=1&status=55395790&p=2"
        ref_of_site = "https://www.wildberries.ru/catalog/0/search.aspx?search=%D0%BC%D1%83%D0%B6%D1%81%D0%BA%D0%B8%D0%B5%20%D1%87%D0%B5%D1%80%D0%BD%D1%8B%D0%B5%20%D0%B4%D0%B6%D0%B8%D0%BD%D1%81%D1%8B&sort=popular"
        parse_site(ref_of_site)
        return redirect('/get_all')

    return render_template("index.html")


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
