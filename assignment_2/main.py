import requests

from bs4 import BeautifulSoup as bs
from app_server import app
from app_db_setup import init_db, db_session
from forms import BoardGameSearchForm
from flask import flash, render_template, request, redirect
from models import BoardGame
from tables import Results


@app.route('/', methods=['GET', 'POST'])
def index():
    search_form = BoardGameSearchForm(request.form)
    if request.method == 'POST':
        return search(search_form)
    return render_template('index.html', form=search_form)


@app.route('/')
def search(search_form):
    search_string = search_form.data['search']
    clear_db()
    add_game(search_string)
    results = db_session.query(BoardGame).all()
    if not results:
        flash(f"No {search_string} found!")
        return redirect('/')
    else:
        table = Results(results)
        table.border = True
        return render_template('index.html', form=search_form, table=table)


def clear_db():
    old = db_session.query(BoardGame).all()
    for x in old[::-1]:
        db_session.delete(x)

def add_game(game_name):
    mosigra_url = "https://www.mosigra.ru/search/?q="
    bgg_url = "https://boardgamegeek.com/geeksearch.php?action=search&objecttype=boardgame&q="
    search_results = bs(requests.get(mosigra_url + game_name).content, "html.parser")
    for group in search_results.find_all("div", limit=42, class_="product-item"):
        game = BoardGame()
        game.title = get_game_title(group)
        game.rank = get_game_rank(bgg_url, game.title)
        game.rating = get_game_rating(bgg_url, game.title)
        game.price = get_game_price(group)
        game.stock = get_game_stock(group)
        db_session.add(game)


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
    found_price = group.find(class_="product-list-price-container").find("span", class_="price-value")
    if found_price is not None:
        return found_price.text.strip(' \n\t')
    return "N/A"


def get_game_stock(group):
    found_stock = group.find(class_="stock-status")
    if found_stock is not None:
        return found_stock.text.strip(' \n\t')
    return "N/A"

if __name__ == '__main__':
    init_db()
    app.run()
