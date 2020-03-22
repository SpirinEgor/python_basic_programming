import json
import sqlite3
import re
import json
import requests

from bs4 import BeautifulSoup
from requests import get
from flask import Flask, g, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE = 'my_database.sqlite'

def post_gift(name,price,link):
    url = 'http://127.0.0.1:5000/new_gift'
    headers = {'Content-type': 'application/json',  # Определение типа данных
               'Accept': 'text/plain',
               'Content-Encoding': 'utf-8'}
    data = {"name": str(name),
            "price": int(price),
            "link": str(link)}

    answer = requests.post(url, data=json.dumps(data), headers=headers)
    response = answer.json()
    
def get_db():
    db_conn = getattr(g, '_database', None)
    if db_conn is None:
        db_conn = g._database = sqlite3.connect(DATABASE)
    return db_conn


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('PRAGMA encoding="UTF-8";')
        cursor.executescript(
            """CREATE TABLE IF NOT EXISTS Gifts
               (id integer primary key, name text not null,
               price integer, link text not null)"""
        )
        db.commit()


@app.route('/get_all')
def get_all():
    db_cursor = get_db().cursor()
    db_cursor.row_factory = sqlite3.Row
    db_cursor.execute("SELECT * From Gifts")
    result = db_cursor.fetchall()
    json_result = json.dumps([dict(row) for row in result], ensure_ascii=False)
    return json_result
    
@app.route('/src_1', methods=['GET'])
def src_1():
    r = get(url = "https://funfrom.me/blog/podarki-dlya-devushki.html")

    soup = BeautifulSoup(r.content, 'html.parser')

    conts = soup.find_all(class_ = "product-container v2")
    for cont in conts:
        name = cont.find(class_ = 'product-name').contents[0]
        price = cont.find(class_='price')['data-price']
        link = cont.find(class_ = 'to-shop')['href']
        post_gift(name,price,link)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

@app.route('/src_2', methods=['GET'])
def src_2():
    r = get(url = "https://2cherry.ru/stati/Chto-podarit-devushke/")

    soup = BeautifulSoup(r.content, 'html.parser')

    items = soup.find_all(class_ = "idea-list__item")
    for item in items:
        name = item.find(class_ = "idea-list__title").contents[0]
        price = item.find(class_ = "price").contents[0].split(" ")[1]
        link = 'none'
        post_gift(name,price,link)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

@app.route('/src_3', methods=['GET'])
def src_3():
    r = get(url = "https://podarki.ru/idei/Samye-populyarnye-podarki-5505")

    soup = BeautifulSoup(r.content, 'html.parser')

    items = soup.find_all(class_ = "goods-block__item")
    for item in items:
        name = item.find(class_ = "good-card__name").contents[0]
        price = int(re.sub("[^0-9]", "", item.find(class_ = "good-card__price").contents[0]))
        link = "https://podarki.ru" + item.find(class_ = "good-card__link-product")['href']
        post_gift(name,price,link)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

@app.route('/delete_all', methods=['GET'])
def delete_all():
    conn = get_db()
    db_cursor = conn.cursor()
    db_cursor.execute("DELETE From Gifts")
    conn.commit()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

@app.route('/new_gift', methods=['POST'])
def create_new_gift():
    gift_json = request.get_json()
    for key in ['name', 'price', 'link']:
        assert key in gift_json, f"{key} not found in the request"
    print(gift_json)    
    query = u"INSERT INTO Gifts (name, price, link) VALUES ('%s', %s, '%s');" % (gift_json['name'], gift_json['price'], gift_json['link']) 
    db_conn = get_db()
    db_conn.execute(query)
    db_conn.commit()
    db_conn.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    init_db()
    app.run()
