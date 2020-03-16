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
            """CREATE TABLE IF NOT EXISTS Facts
               (id integer primary key, fact text not null)"""
        )
        db.commit()


@app.route('/get_all')
def get_all():
    db_cursor = get_db().cursor()
    db_cursor.row_factory = sqlite3.Row
    db_cursor.execute("SELECT * From Facts")
    result = db_cursor.fetchall()
    json_result = json.dumps([dict(row) for row in result])
    return json_result


@app.route('/new_year', methods=['POST'])
def create_new_year():
    user_json = request.get_json()
    assert 'year' in user_json, f'Year not found in the request'
    addr = "https://ru.wikipedia.org/wiki/"+user_json['year']+"_год"
    wiki = requests.get(addr)
    html = wiki.content
    soup = BeautifulSoup(html, 'html.parser')
    Facts = []
    div = soup.find(attrs={"class" : "mw-parser-output"})
    ul = div.find_all('ul')
    for tag in ul[1].find_all('li'):
            if (tag.attrs.get("class") == None):
                Facts.append(tag.get_text())
    db_conn = get_db()
    db_conn.execute("DELETE From Facts")
    for facts in Facts:
        query = f"INSERT INTO Facts (fact) VALUES ('{facts}');"
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