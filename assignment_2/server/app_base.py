from flask import Flask
import requests                                                                                                                                                                        

app = Flask(__name__)


@app.route('/')
def hello_world():
    r = requests.get('https://rplnews.ru/')                                                                                                                                                 
    html = r.text
    print(html)
    return "zalupa"


@app.route('/zalupa')
def zalupa():
    return 'Zalupa'


if __name__ == '__main__':
    app.run()
