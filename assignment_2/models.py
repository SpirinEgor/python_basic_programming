from app_server import db


class BoardGame(db.Model):
    __tablename__ = "BoardGame"
    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.String)
    title = db.Column(db.String)
    rating = db.Column(db.String)
    price = db.Column(db.String)
    stock = db.Column(db.String)
