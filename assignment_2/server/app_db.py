from flask import Flask, g, request
from flask_cors import CORS
import requests
import bs4
import json
import sqlite3

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
            """CREATE TABLE IF NOT EXISTS Accounts
               (name text not null,
               screen_name text not null,
               profile text)"""
        )
        db.commit()


def parse_row(row):
    return row.text.replace('\n', '').split(':', 1)


def parse_block(block):
    return (
        block.find('span', 'profile_info_header').text,
        dict(
            [
                parse_row(row)
                for row in block.find_all('div', 'profile_info_row')
            ]
        )
    )


def parse_profile(profile):
    return dict(
        [
            parse_block(block)
            for block in profile.find_all('div', 'profile_info_block')
        ]
    )


def row_to_json(row):
    res = dict(row)
    res['profile'] = json.loads(res['profile'])
    return res


@app.route('/get_accounts')
def get_accounts():
    db_cursor = get_db().cursor()
    db_cursor.row_factory = sqlite3.Row
    db_cursor.execute("SELECT * From Accounts")
    result = db_cursor.fetchall()
    json_result = json.dumps([row_to_json(row) for row in result])
    return json_result


@app.route('/add_account', methods=["POST"])
def add_account():
    header = {
        'User-Agent':
            'Mozilla/5.0 ' +
            '(X11; Ubuntu; Linux x86_64; rv:74.0) ' +
            'Gecko/20100101 Firefox/74.0'
    }
    screen_name = request.get_json()['screen_name']
    url = 'https://vk.com/' + screen_name
    req = requests.get(url, headers=header)
    if not req.ok:
        return 'Error'
    html = bs4.BeautifulSoup(req.text)
    profile_short = html.find(id='profile_short')
    profile_full = html.find(id='profile_full')
    profile = bs4.BeautifulSoup(
        f'''<div class="profile_info_block">
                <div class="profile_info_header_wrap">
                    <span class="profile_info_header">Краткая информация</span>
                </div>
                {profile_short}
        </div>
        {profile_full}'''
    )
    page_name = html.find('h1', 'page_name').text
    json_result = json.dumps(parse_profile(profile)).replace('\'', '')
    db_conn = get_db()
    db_conn.execute(
        f"DELETE FROM Accounts WHERE screen_name = '{screen_name}';"
    )
    db_conn.commit()
    db_conn.execute(f"""INSERT INTO Accounts (name, screen_name, profile) VALUES (
        '{page_name}',
        '{screen_name}',
        '{json_result}'
    );""")
    db_conn.commit()
    db_conn.close()
    return (
        json.dumps({'success': True}),
        200,
        {'ContentType': 'application/json'}
    )


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    init_db()
    app.run()

