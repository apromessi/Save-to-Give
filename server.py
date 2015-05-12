from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Challenge, Accepted_Challenge, Transaction, Organization, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined

##############################################################################################

@app.route("/")
def index():
    """Displays Homepage"""

    return "This is the homepage!!"

@app.route("/login", methods = ["POST", "GET"])
def login_form():
    """GET - displays a form that asks for email and password
        POST - collects that data and authenticates --> redirect to user profile"""

    if request.method == "GET":
        return "This is where you log in."
    if request.method == "POST":
        return "This is where I decide whether you're legit.Check against DB, add to session, redirect to profile."

@app.route("/register")
def registration_form():
    """GET - Displays a form for new users to enter information and connect to Mint
        POST - adds registration data to DB --> redirect to transaction analysis
        (or choose to browse challenges --> redirect to challenge browser tool)"""

    if request.method == "GET":
        return "Display registration form"
    if request.method == "POST":
        return "Get registration data and redirect."

@app.route("/all_challenges")
def browse_all_challenges():
    """Right now this is a "nice to have"
        - will allow an alternative for users who don't want to enter their Mint info"""

    return "Browse Challenge page"

@app.route("/transaction_analysis")
def display_transaction_analysis():
    """Scrapes data from Mint account and displays an analysis of transactions by category.
        Identfies places where User spends more money than necessary - ratio of "groceries"
        to "restaurants", search for key words like "Starbucks" or "cafe". Could also focus on week by week.
        Finds relevant challenges and displays challenge info for User, along with "Accept" buttons"""

    return "Graph of transactions, challenge info."

@app.route("/profile")
def profile():
    """Displays any relevant user information along with overall progress towards achieving challenges.
        Links to progress on specific challenges.
        Links to transaction analysis - and/or displays summarized version?"""

    return "Graph of overall progress - all accepted challenges listed, completed challenges and amounts, contributing to overall progress."

@app.route("/update_progress")
def update_progress():
    """Displays progress on individual challenges. Offers a way for User to update progress:
        2 options:
            1) enter in units completed - one coffee brewed instead of bought
            2) or perform another transactional analysis and assess progress (might be more interesting and challenging, but I'm not sure if I have enough information from Mint/broad categories of spending"""

    return "Update progress - two options. If complete, display congratulations message and offer link to donation page."

@app.route("/donate")
def donate():
    """Access payment gateway for appropriate organization
        Use stripe?"""

    return "Pay the monies!"


##########################################################################################
if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()