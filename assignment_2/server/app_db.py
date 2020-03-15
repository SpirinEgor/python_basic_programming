import json
import sqlite3
import requests
import transliterate
import chardet

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
            """CREATE TABLE IF NOT EXISTS Cafes
               (id integer primary key,
               name text not null,
               description text)"""
        )
        add_new_cafe('https://www.casatualondon.com/?utm_source=tripadvisor&utm_medium=referral')
        add_new_cafe('https://dunord.spb.ru/')
        add_new_cafe('http://www.fvolchek.ru/')
        add_new_cafe('https://king-pyshka.ru/')
        add_new_cafe('https://www.epicpies.co.uk/?utm_source=tripadvisor&utm_medium=referral')
        add_new_cafe('https://www.kartoshka.com')
        add_new_cafe('https://vk.com/lecafeveranda')
        add_new_cafe('https://www.cofix.ru')
        db.commit()


def add_new_cafe(url):
    assert url != ''
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    name = soup.title.string.split(' - ')[0].split(' | ')[0]
    lang = chardet.detect(name.encode('cp1251'))
    lang = lang.get('language')
    name = transliterate.translit(name, "ru", reversed = True if lang != ' ' else False)
    descr = soup.find('meta', attrs={'name':'description'})['content']
    descr = transliterate.translit(descr, "ru", reversed = True if lang != ' ' else False)
    db_conn = get_db()
    cursor = db_conn.cursor()
    cursor.execute(f"SELECT id FROM Cafes WHERE name =\"{name}\";")
    if cursor.fetchone():
        cursor.execute(f"UPDATE Cafes SET description = \"{descr}\" WHERE name =\"{name}\";")
    else:
        cursor.execute(f"INSERT INTO Cafes (name, description) VALUES (\"{name}\", \"{descr}\");")
    db_conn.commit()


@app.route('/get_all')
def get_all():
    db_cursor = get_db().cursor()
    db_cursor.row_factory = sqlite3.Row
    db_cursor.execute("SELECT * From Cafes")
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
