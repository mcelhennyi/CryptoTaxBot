from DataStorage.tables import Trade, Withdrawal, Deposit, Base
from DataStorage.database_interface import DatabaseInterface
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from datetime import datetime

app = Flask(__name__)

# Setup the db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////temp_db.db'
db = DatabaseInterface(verbose=False)

# Categories
CAT_ERROR = 'danger'
CAT_SUCCESS = 'success'


# Index
@app.route('/')
def index():
    return render_template('home.html')


@app.route('/withdrawals')
def withdrawals():
    withdraw_list = []
    withdraw_headers, withdraw_results = db.query_all_withdrawals('binance')
    for withdraw in withdraw_results:
        assert isinstance(withdraw, Withdrawal)
        withdraw_list.append(withdraw.to_dict())
        print(withdraw.to_dict())

    return render_template('withdrawals.html', headers=withdraw_headers, data_list=withdraw_list)


@app.route('/deposits')
def deposits():
    deposit_list = []
    deposit_headers, deposit_results = db.query_all_deposits('binance')
    for deposit in deposit_results:
        print(deposit)
        deposit_dict = deposit.to_dict()
        deposit_dict['insert_time'] = datetime.fromtimestamp(deposit_dict['insert_time']/1000.0
                                                             ).strftime('%m-%d-%Y %I:%M:%S%p')
        deposit_list.append(deposit_dict)
        # print(deposit.to_dict())

    return render_template('deposits.html', headers=deposit_headers, data_list=deposit_list)


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)
