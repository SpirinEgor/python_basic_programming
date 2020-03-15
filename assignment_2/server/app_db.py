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


#@app.route('/new_user', methods=['POST'])
#def create_new_user():
#    user_json = request.get_json()
#    for key in ['name', 'surname', 'age']:
#        assert key in user_json, f"{key} not found in the request"
#    query = f"INSERT INTO Users (name, surname, age) VALUES ('{user_json['name']}', '{user_json['surname']}', {user_json['age']});"
#    db_conn = get_db()
#    db_conn.execute(query)
#    db_conn.commit()
#    db_conn.close()
#    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

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
