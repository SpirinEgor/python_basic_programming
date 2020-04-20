import json
import sqlite3
import requests

from flask import Flask, g, request
from flask_cors import CORS
from bs4 import BeautifulSoup as bs

app = Flask(__name__)
CORS(app)

DATABASE = 'my_database.sqlite'
games = []


def get_db():
    db_conn = getattr(g, '_database', None)
    if db_conn is None:
        db_conn = g._database = sqlite3.connect(DATABASE)
    return db_conn


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.executescript("""DROP TABLE IF EXISTS BoardGames""")
        cursor.executescript(
            """CREATE TABLE BoardGames
            (id integer primary key,
            rank text not null,
            rating text not null,
            title text not null,
            price text not null,
            stock text not null)"""
        )

        db.commit()


def add_games(game_name=''):
    mosigra_url = "https://www.mosigra.ru/search/?q="
    bgg_url = "https://boardgamegeek.com/geeksearch.php?action=search&objecttype=boardgame&q="
    search_results = bs(requests.get(
        mosigra_url + game_name).content, "html.parser")
    for group in search_results.find_all("div", limit=7, class_="product-item"):
        game = {"rank": "", "rating": "",
                "title": "", "price": "", "stock": ""}
        game["title"] = get_game_title(group)
        game["rank"] = get_game_rank(bgg_url, game["title"])
        game["rating"] = get_game_rating(bgg_url, game["title"])
        game["price"] = get_game_price(group)
        game["stock"] = get_game_stock(group)
        games.append(game)
        print(game)
        print(games)


def get_game_title(group):
    found_title = group.find("h3", class_="product-list-title")
    if found_title is not None:
        return found_title.a.text.strip(' \n\t')
    return ""


def get_game_rank(bgg_url, game_title):
    bgg = bs(requests.get(bgg_url + game_title).content, "html.parser")
    found_rank = bgg.find("td", class_="collection_rank")
    if found_rank is not None:
        return found_rank.text.strip(' \n\t')
    return "N/A"


def get_game_rating(bgg_url, game_title):
    bgg = bs(requests.get(bgg_url + game_title).content, "html.parser")
    found_rating = bgg.find("td", class_="collection_bggrating")
    if found_rating is not None:
        return found_rating.text.strip(' \n\t')
    return "N/A"


def get_game_price(group):
    found_price = group.find(
        class_="product-list-price-container").find("span", class_="price-value")
    if found_price is not None:
        return found_price.text.strip(' \n\t')
    return "N/A"


def get_game_stock(group):
    found_stock = group.find(class_="stock-status")
    if found_stock is not None:
        return found_stock.text.strip(' \n\t')
    return "N/A"


def fill_bd():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        for game in games:
            print(game["title"])
            cursor.execute(f"""INSERT INTO BoardGames
                (rank, rating, title, price, stock) VALUES
                ('{game["rank"]}', '{game["rating"]}', '{game["title"]}', '{game["price"]}', '{game["stock"]}');""")
        db.commit()


@app.route('/get_all')
def get_all():
    db_cursor = get_db().cursor()
    db_cursor.row_factory = sqlite3.Row
    db_cursor.execute("SELECT * From BoardGames")
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
    add_games()
    fill_bd()
    app.run()
