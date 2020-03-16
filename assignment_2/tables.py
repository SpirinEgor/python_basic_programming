from flask_table import Table, Col


class Results(Table):
    id = Col('Id', show=False)
    rank = Col('Rank')
    rating = Col('Rating')
    title = Col('Title')
    price = Col('Price')
    stock = Col('Stock')
