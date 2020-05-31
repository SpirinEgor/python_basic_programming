from flask import Flask
import requests

app = Flask(__name__)


@app.route('/')
def hello_world():
    r = requests.get('https://rplnews.ru/')
    html = r.text
    print(html)
    return "family_friendly"


@app.route('/family_friendly')
def family_friendly():
    return 'This server is now family-friendly'


if __name__ == '__main__':
    app.run()
