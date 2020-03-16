from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///BoardGame.db'
app.secret_key = "Board Games rocks!"

db = SQLAlchemy(app)
