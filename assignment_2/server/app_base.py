import requests
from bs4 import BeautifulSoup

import json
import sqlite3

from flask import Flask, g, request
from flask_cors import CORS

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
            """CREATE TABLE IF NOT EXISTS Sneakers
               (id integer primary key, title text not null,
               price integer, photo text not null)"""
        )
        db.commit()


@app.route('/get_all')
def get_all():
    db_cursor = get_db().cursor()
    db_cursor.row_factory = sqlite3.Row
    db_cursor.execute("SELECT * From Sneakers")
    result = db_cursor.fetchall()
    json_result = json.dumps([dict(row) for row in result])
    return json_result


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def add_new_sneaker(ptitle, pprice, pphoto):
    sneaker_json = {'title':ptitle, 'price':pprice, 'photo':pphoto}
    for key in ['title', 'price', 'photo']:
        assert key in sneaker_json, f'{key} not found in the request'
    query = f"INSERT INTO Sneakers (title, price, photo) VALUES ('{ptitle}', {pprice}, '{pphoto}');"
    db_conn = get_db()
    db_conn.execute(query)
    db_conn.commit()
    db_conn.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/', methods=['GET', 'POST'])
def parse_site():
    # adidas
    a = requests.get('https://adidas-store.ru/')
    html = a.content
    soup = BeautifulSoup(html)
    for group in soup.find_all('li', class_="product"):
        image = group.find('img')['src']
        name = group.find('h2', class_="woocommerce-loop-product__title").string
        price = group.find('span', class_="woocommerce-Price-amount").contents[1][:-3].replace(",", "")
        if name != None and price != None and image != None:
            add_new_sneaker(name, int(price), image)



if __name__ == '__main__':
    init_db()
    app.run()
