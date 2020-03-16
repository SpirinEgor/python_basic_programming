from wtforms import Form, StringField


class BoardGameSearchForm(Form):
    search = StringField('Search for board game:')
