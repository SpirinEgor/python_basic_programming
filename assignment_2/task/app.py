import json
import sqlite3

from flask import Flask, g, request, render_template, send_file
from flask_cors import CORS

from common_db import DATABASE

app = Flask(__name__)
CORS(app)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db

@app.route('/scripts')
def get_scripts():
    return send_file('scripts.js')

@app.route('/')
def get_index():
    return send_file('index.html')

@app.route('/get/size')
def get_size():
    db_cursor = get_db().cursor()
    db_cursor.execute(''' SELECT COUNT(*) FROM Titles ''')
    return json.dumps({'size': db_cursor.fetchone()[0]})

@app.route('/get/<text>/<count>/<offset>')
def get_titles(text, count, offset):
    db_cursor = get_db().cursor()
    db_cursor.row_factory = sqlite3.Row
    db_cursor.execute(f'''
        SELECT * FROM Titles
        WHERE title LIKE "%{text}%"
        ORDER BY title
        LIMIT {offset}, {count} ''')
    result = db_cursor.fetchall()

    dicts = []

    for row in result:
        base_dict = dict(row)

        db_cursor.execute(f"SELECT * From Chapters{base_dict['id']} ORDER BY volume, chapter")
        chapter_result = db_cursor.fetchall()

        base_dict['chapters'] = [dict(chapter_row) for chapter_row in chapter_result]

        dicts.append(base_dict)

    json_result = json.dumps(dicts)
    return json_result

@app.route('/get/<count>/<offset>')
def get_all_titles(count, offset):
    return get_titles('', count, offset)

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('_database', None)
    if db is not None:
        db.close()
    driver = g.pop('_driver', None)
    if driver is not None:
        driver.close()

if __name__ == '__main__':
    app.run()
