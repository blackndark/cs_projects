import os
#import stripe
import json

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

# Set up Stripe API test keys for test purposes
#stripe.api_key = "sk_test_51IaO5hIGKzkfFJKvTMHyTiMoYA4Hq494eVDyFS9tSjqs5mn9oVOzw74pmNAKfdF27pD1fw0tpMv62BKqYf0OkWux00nsHv7amR"

db.execute("CREATE TABLE IF NOT EXISTS transactions (username TEXT NOT NULL, symbol TEXT NOT NULL, price NUMERIC NOT NULL, shares NUMERIC NOT NULL, time DATETIME DEFAULT CURRENT_TIMESTAMP, value NUMERIC, current_price NUMERIC)")
# db.execute("CREATE UNIQUE INDEX time ON transactions (time)")


@app.route("/")
@login_required
def index():

    # In order to keep the holdings table up to date, dropping and creating the table each time is the easiest solution. Probably not the best though.
    db.execute("DROP TABLE IF EXISTS holdings")
    db.execute("CREATE TABLE holdings (username TEXT NOT NULL, symbol TEXT NOT NULL, shares NUMERIC NOT NULL, current_value NUMERIC, current_price NUMERIC)")

    # Collect username of the current user
    users_rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

    # We will iterate on all the transactions row by row and update curent_price via the API call
    rows = db.execute("SELECT * FROM transactions WHERE username = ?", users_rows[0]["username"])
    for row in range(len(rows)):
        symbol = rows[row]["symbol"]
        stock_quote = lookup(symbol)
        price = stock_quote["price"]
        db.execute("UPDATE transactions SET current_price = ? WHERE symbol = ?", price, symbol)

    # Group transactions table by username and stock symbol so that you know which user holds how many shares of a certain stock, then iterate through each row and insert into holdings table.
    holdings_dict = db.execute(
        "SELECT username, symbol, sum(shares) AS shares, current_price from transactions GROUP BY symbol, username")
    # TOTAL VALUE VARIABLE
    for row in range(len(holdings_dict)):
        if holdings_dict[row]["shares"] > 0:
            username = holdings_dict[row]["username"]
            symbol = holdings_dict[row]["symbol"]
            shares = holdings_dict[row]["shares"]
            current_price = holdings_dict[row]["current_price"]
            current_value = shares * current_price
            db.execute("INSERT INTO holdings (username, symbol, shares, current_value, current_price) VALUES(?, ?, ?, ?, ?)",
                       username, symbol, shares, current_value, current_price)

    # Select all holdings data for the given username to send to the html template
    holdings = db.execute("SELECT symbol, shares, current_price, current_value FROM holdings WHERE username = ?",
                          users_rows[0]["username"])

    # Select total value of holdings to use when calculating total account value. Take into account the situation when there are no holdings.
    value_of_holdings_list = db.execute(
        "SELECT sum(current_value) AS holdings_value FROM holdings WHERE username = ? GROUP BY username", users_rows[0]["username"])
    if not value_of_holdings_list:
        value_of_holdings = 0
    else:
        value_of_holdings = value_of_holdings_list[0]["holdings_value"]

    # Insert cash balance into holdings view as the row before the last one
    cash_balance = users_rows[0]["cash"]
    cash_balance_list = [{"symbol": "CASH", "current_value": cash_balance}]

    # Insert total account value as the last row to the holdings view
    total_account_value = cash_balance + value_of_holdings
    total_account_value_list = [{"symbol": "Total Account Value", "current_value": total_account_value}]

    balance_list = cash_balance_list + total_account_value_list

    # Add $ sign to prices via the usd function
    for row in range(len(holdings)):
        holdings[row]["current_value"] = usd(holdings[row]["current_value"])

    for row in range(len(balance_list)):
        balance_list[row]["current_value"] = usd(balance_list[row]["current_value"])

    return render_template("index.html", holdings=holdings, balance_list=balance_list)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    if request.method == "POST":

        # Control the submitted stock symbol
        symbol = request.form.get("symbol")
        stock_quote = lookup(symbol)
        if not stock_quote:
            return apology("There is no stock with the given symbol")

        # Control if the share number is a positive integer.
        shares = request.form.get("shares")
        # if not isinstance(shares, int):
        #    return apology("Please type a number")
        if not int(shares) > 0:
            return apology("Please type a positive number")

        # current price
        price = stock_quote["price"]

        # current cash
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        total_cash = rows[0]["cash"]

        # calculate the transaction amount and see if there is enough money in the account
        transaction_amount = int(shares) * price
        if total_cash < transaction_amount:
            return apology("You have insufficient funds for this transaction")

        value = transaction_amount

        # update transaction table and cash balance to execute the transaction
        total_cash -= transaction_amount
        db.execute("INSERT INTO transactions (username, symbol, price, shares, value) VALUES(?, ?, ?, ?, ?)",
                   rows[0]["username"], stock_quote["symbol"], price, shares, value)
        db.execute("UPDATE users SET cash = ? WHERE username = ?", total_cash, rows[0]["username"])

        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():

    # Remember user from the user ID
    username = db.execute("SELECT * FROM users where id = ?", session["user_id"])
    username = username[0]["username"]

    # Pull user's transaction data
    transactions = db.execute(
        "SELECT symbol, price, shares, TIME, value, current_price FROM transactions WHERE username = ?", username)

    # Add $ sign to prices via the usd function
    for row in range(len(transactions)):
        transactions[row]["price"] = usd(transactions[row]["price"])
        transactions[row]["current_price"] = usd(transactions[row]["current_price"])

    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():

    if request.method == "POST":

        # Check if the given stock symbol is valid via the API call
        symbol = request.form.get("symbol")
        stock_quote = lookup(symbol)
        if not stock_quote:
            return apology("There is no stock with the given symbol", 400)

        # Render the stock quote information via the html template
        return render_template("quoted.html", stock_quote=stock_quote)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get a username and control if it's not blank and if it's not already registered
        username = request.form.get("username")
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if not username:
            return apology("Please enter a username", 400)
        if len(rows) != 0:
            return apology("Username already registered", 400)

        # Get a password and control if the password is not blank and if the confirmation matches the password
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not password:
            return apology("Must provide password", 400)
        if confirmation != password:
            return apology("Passwords do not match", 400)

        # Hash the password via the imported hash function
        hashed_password = generate_password_hash(password)

        # Register the user via inserting into the users table with the given username and hashed password
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hashed_password)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():

    if request.method == "POST":

        # Controlling if the user can sell
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("Please select a share that you hold in your account")
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        username = rows[0]["username"]

        # Double check against html hacking and see if the user has the stock symbol in holdings table
        rows = db.execute("SELECT * FROM holdings WHERE username = ? AND symbol = ?", username, symbol)
        rows = rows[0]["symbol"]
        if not rows:
            return apology("The stock you selected is not owned")

        # Control if the number of shares to sell is positive.
        shares = request.form.get("shares")
        # if not isinstance(shares, int):
        #    return apology("Please type a number")
        if int(shares) < 1:
            return apology("Please submit a positive number")

        # Control if the number of shares that wants to be sold are greater than the number of shares which are hold in the account for the given stock symbol
        share_number = db.execute("SELECT shares FROM holdings WHERE symbol = ? AND username = ? GROUP BY symbol", symbol, username)
        share_number = share_number[0]["shares"]
        if int(shares) > share_number:
            return apology("Account doesn't have that much shares")

        # Actual selling
        # Updating cash balance
        cash = db.execute("SELECT * FROM users WHERE username = ?", username)
        cash = cash[0]["cash"]
        stock_quote = lookup(symbol)
        price = stock_quote["price"]
        cash += int(shares) * price
        db.execute("UPDATE users SET cash = ? WHERE username = ?", cash, username)

        # Updating transactions
        shares_sold = int("-" + str(shares))
        value = shares_sold * price
        db.execute("INSERT INTO transactions (username, symbol, price, shares, value) VALUES(?, ?, ?, ?, ?)",
                   username, stock_quote["symbol"], price, shares_sold, value)

        return redirect("/")

    else:
        # Pull the list of owned stock symbols to pass to the html template
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        username = rows[0]["username"]
        symbol = db.execute("SELECT symbol FROM holdings WHERE username = ? GROUP BY symbol", username)
        return render_template("sell.html", symbol=symbol)


 #   def errorhandler(e):
 #       """Handle error"""
 #       if not isinstance(e, HTTPException):
 #           e = InternalServerError()
 #       return apology(e.name, e.code)
 #
 #
 #   # Listen for errors
 #   for code in default_exceptions:
 #       app.errorhandler(code)(errorhandler)
 #
 #   DOMAIN = 'https://ide-fde3c812d2a44e09855368d0b11a4b54-8080.cs50.ws'


 #       @app.route('/create-checkout-session', methods=['POST'])
 #       def create_checkout_session():
 #           try:
 #               checkout_session = stripe.checkout.Session.create(
 #                   payment_method_types=['card'],
 #                   line_items=[
 #                       {
 #                           'price_data': {
 #                               'currency': 'usd',
 #                               'unit_amount': 50,
 #                               'product_data': {
 #                                   'name': 'Donation Amount',
 #                               },
 #                           },
 #                           'quantity': 1,
 #                       },
 #                   ],
 #                   mode='payment',
 #                   success_url=DOMAIN + '/success',
 #                   cancel_url=DOMAIN + '/cancel',
 #               )
 #               return jsonify({'id': checkout_session.id})
 #           except Exception as e:
 #               return jsonify(error=str(e)), 403
 #
 #
 #       @app.route("/success")
 #       def success():
 #           return render_template("success.html")
 #
 #
 #       @app.route("/cancel")
 #       def cancelled():
 #           return render_template("cancel.html")


