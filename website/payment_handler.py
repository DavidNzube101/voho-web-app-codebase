from flask import Blueprint, render_template, flash, request, redirect, url_for, current_app, send_from_directory, session, jsonify
from flask_login import login_required, current_user


import base64
import random
import requests
import imghdr
import datetime as dt

from . import DateToolKit as dtk
# from .db import db
from . import id_generator
# from .db import dbORM
from . import function_pool
# from . import encrypt
from . import ScreenGoRoute

from .SarahDBClient.db import db
from .SarahDBClient.db import dbORM
from .SarahDBClient import encrypt

if dbORM == None:
    User, Notes = None, None
else:
    User, Notes = dbORM.get_all("UserAPRO"), None


today = dt.datetime.now().date()


payment_handler_actions = Blueprint('payment_handler_actions', __name__)
pha = payment_handler_actions

is_test = True

# Replace with your Flutterwave public and secret keys
FLUTTERWAVE_PUBLIC_KEY = 'FLWSECK_TEST-e82b295786adf1fc47b908a84abac060-X'
FLUTTERWAVE_SECRET_KEY = 'FLWSECK_TEST-e82b295786adf1fc47b908a84abac060-X'

# Your Flutterwave endpoint
FLUTTERWAVE_API_URL = 'https://api.flutterwave.com/v3/payments/initialize'

@pha.route('/pay', methods=['POST'])
def initialize_payment():
    amount = request.form['amount']
    email = request.form['email']
    # Other parameters as needed

    headers = {
        'Authorization': f'Bearer {FLUTTERWAVE_SECRET_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        "amount": amount,
        "email": email,
        "public_key": FLUTTERWAVE_PUBLIC_KEY,
        # Other parameters as required
    }

    response = requests.post(FLUTTERWAVE_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        print(data)
        link = data['data']['link']
        return redirect(link)
    else:
        return jsonify({'error': 'Payment initialization failed'})























# ------------------------------------------------------------------------------------------------------------------
@pha.route("/proceed-payments", methods=['POST'])
def proceedPayments():

    auth_headers ={
        "Authorization": "Bearer sk_live_647e9e80e664c352203ad6efbde838ba1ee0d404",
        "Content-Type": "application/json"
    }
    customer_email = dbORM.get_all('User')[f'{current_user.id}']['email']
    auth_data = { "email": customer_email, "amount": "100000" } #"{}".format(products[product_id]['price'])
    auth_data = json.dumps(auth_data)
    req = requests.post('https://api.paystack.co/transaction/initialize', headers=auth_headers, data=auth_data)
    response_data = json.loads(req.text)
    paystack_uri = response_data['data']['authorization_url']
    return redirect(paystack_uri)

@pha.route("/callback/<string:amount>/<string:currency>/<string:transaction_type>")
def showTestSuccess(amount, currency, transaction_type):
    TID = id_generator.generateTID()

    deposited_amount = float(amount)
    u = dbORM.get_all("User")[f'{current_user.id}']
    current_balance = float(u['wallet_balance'])

    naira_equivalent_deposited_amount = float(function_pool.convertCurrency(deposited_amount, u['preferred_currency'], "NGN"))

    dbORM.update_entry(
        "User", 
        f"{dbORM.find_one('User', 'id', str(current_user.id))}", 
        encrypt.encrypter(str({"wallet_balance": f"{naira_equivalent_deposited_amount + current_balance}"})),
        False
        )
    print(f"Updated!\nOld Balance: {current_balance}\nDeposit: {naira_equivalent_deposited_amount}\nNew Balance: {naira_equivalent_deposited_amount + current_balance}")

    
    transaction_data = {
        'user_id': f"{current_user.id}",
        'transaction_type': transaction_type,
        'amount': deposited_amount,
        'datestamp': function_pool.getDateTime()[0],
        'timestamp': function_pool.getDateTime()[1],
        'transaction_status': "Success",
        'third_party': "Paystack",
        'transaction_id': TID,
        'initial_currency': currency
    }
    deposit_data = {
        "datestamp": function_pool.getDateTime()[0],
        "timestamp": function_pool.getDateTime()[1],
        "status": "Success",
        "third_party": "Paystack",
        "amount": deposited_amount,
        "transaction_id": TID,
        "user_id": f"{current_user.id}",
        "initial_currency": currency
    }
    dbORM.add_entry("TransactionHistory", f"{encrypt.encrypter(str(transaction_data))}")
    dbORM.add_entry("DepositHistory", f"{encrypt.encrypter(str(deposit_data))}")

    return ScreenGoRoute.go_to("1", _redirect=True)

@pha.route("/callback")
def showSuccess():
    ref = request.args['trxref']
    auth_headers ={
        "Authorization": "Bearer sk_live_647e9e80e664c352203ad6efbde838ba1ee0d404",
        "Content-Type": "application/json"
    }
    req = requests.get('https://api.paystack.co/transaction/verify/{}'.format(ref), headers=auth_headers)
    tr_data = json.loads(req.text)
    message = tr_data['data']['status']
    amount = tr_data['data']['amount']
    amount = (amount/100)
    amount = "{:.2f}".format(amount)
    tr_id = tr_data['data']['id']
    # dbORM.update_entry(
    #     "UserN100", 
    #     f"{dbORM.find_one('User', 'id', str(current_user.id))}", 
    #     encrypt.encrypter(str({"is_premium_account": "True"})),
    #     False
    #     )
    return ScreenGoRoute.go_to("6", _redirect=True)
