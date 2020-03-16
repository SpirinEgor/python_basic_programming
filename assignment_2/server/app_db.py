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
        cursor.executescript("""DROP TABLE IF EXISTS Books""")
        cursor.executescript(
            """CREATE TABLE Books
               (id integer primary key, 
               library text not null,
               author text not null,
               title text not null)"""
        )

        Books = []

        page = requests.get("https://aldebaran.ru/genre/klassika/")
        soup = BeautifulSoup(page.content, 'html.parser')
        books = soup.find_all('div', {"class": "book_info clearfix"})
        for book in books:
            title = book.find('p', class_="booktitle").a.text
            info = book.find('div', class_="book_intro").text
            book_info = {
                "library" : "aldebaran.ru",
                "title" : title,
                "info" : info
            }
            Books.append(book_info)

        page = requests.get("https://libs.ru/best-100-russian/")
        soup = BeautifulSoup(page.content, 'html.parser')
        books = soup.find_all('div', class_="book-cardLong-info")
        for book in books:
            title = book.find('div', class_="book-cardLong-name").find('a').text
            info = book.find('div', class_="book-cardLong-descr", recurcive=False).text
            book_info = {
                "library" : "libs.ru",
                "title" : title,
                "info" : info
            }
            Books.append(book_info)

        for book in Books:
            print(book["title"])
            cursor.execute(f"""INSERT INTO Books (library, title, author)
                            VALUES ('{book["library"]}', '{book["title"]}', '{book["info"]}');""")
        db.commit()


@app.route('/get_all')
def get_all():
    db_cursor = get_db().cursor()
    db_cursor.row_factory = sqlite3.Row
    db_cursor.execute("SELECT * From Books")
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
