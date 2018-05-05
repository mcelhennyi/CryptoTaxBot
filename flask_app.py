from DataStorage.tables import Trade, Withdrawal, Deposit, Base
from DataStorage.database_interface import DatabaseInterface
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
# from data import Articles
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps


app = Flask(__name__)

# Setup the db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////temp_db.db'
db = DatabaseInterface(verbose=True)

# Categories
CAT_ERROR = 'danger'
CAT_SUCCESS = 'success'


# Index
@app.route('/')
def index():
    return render_template('home.html')


@app.route('/withdrawals')
def withdrawals():
    withdraw_headers = Withdrawal.__table__.c.key()
    withdraw_list = []#db.query_withdrawals()

    print(withdraw_headers)

    # withdraw_query = db.query_withdrawals()
    # for withdraw in withdraw_query:
    #     assert isinstance(withdraw, Withdrawal)
    #     withdraw_list.append(dict(withdraw))

    # print(withdraw_query)



    return render_template('withdrawals.html', withdraw_headers=withdraw_headers, withdraw_list=withdraw_list)


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)
