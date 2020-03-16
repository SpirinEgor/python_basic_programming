import requests

from bs4 import BeautifulSoup
from app_server import app
from app_db_setup import init_db, db_session
from forms import BoardGameSearchForm
from flask import flash, render_template, request, redirect
from models import BoardGame
from tables import Results

init_db()


@app.route('/', methods=['GET', 'POST'])
def index():
    search = BoardGameSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)
    return render_template('index.html', form=search)


@app.route('/')
def search_results(search):
    search_string = search.data['search']
    old = db_session.query(BoardGame).all()
    for x in old[::-1]:
        db_session.delete(x)
    add_game(search_string)
    results = db_session.query(BoardGame).all()
    if not results:
        flash("No {} found!".format(search_string))
        return redirect('/')
    else:
        table = Results(results)
        table.border = True
        return render_template('index.html', form=search, table=table)


def add_game(game_name):
    mosigra_url = "https://www.mosigra.ru/search/?q="
    bgg_url = "https://boardgamegeek.com/geeksearch.php?action=search&objecttype=boardgame&q="
    r = requests.get(mosigra_url + "{}".format(game_name))
    html = r.content
    s = BeautifulSoup(html, "html.parser")
    for group in s.find_all("div", limit=42, class_="product-item"):
        game = BoardGame()
        game.title = str(group.find(
            "h3", class_="product-list-title").a.text).strip(' \n\t')
        bgg = BeautifulSoup(requests.get(
            bgg_url + "{}".format(game.title)).content, "html.parser")
        find_rank = bgg.find("td", class_="collection_rank")
        game.rank = str(find_rank.text if find_rank !=
                        None else "N/A").strip(' \n\t')
        find_rating = bgg.find("td", class_="collection_bggrating")
        game.rating = str(find_rating.text if find_rating !=
                          None else "N/A").strip(' \n\t')
        game.price = str(group.find(class_="product-list-price-container").find(
            "span", class_="price-value").text).strip(' \n\t')
        game.stock = str(group.find(class_="stock-status").text).strip(' \n\t')
        print(game)
        db_session.add(game)


if __name__ == '__main__':
    app.run()
