from jinja2 import StrictUndefined
import os
import keyring
import datetime

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Challenge, Accepted_Challenge, Donation, Transaction, Organization, connect_to_db, db
from transaction_analysis import load_transactions


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

    return render_template("homepage.html")


@app.route("/login", methods = ["POST", "GET"])
def login_form():
    """GET - displays a form that asks for email and password
        POST - collects that data and authenticates --> redirect to user profile"""
        
    if request.method == "POST":
        email = request.form["username_input"]
        password = request.form["password_input"]
        user_object = User.query.filter(User.email == email).first()
        
        if user_object:
            if user_object.password == password:
                session["login"] = email
                flash("You logged in successfully")
                return redirect("/profile")
            else:
                flash("Incorrect password. Try again.")
                return redirect("/login")
        else:
            flash("We do not have this email on file. Click Register if you would like to create an account.")
            return redirect("/login")

    return render_template("login.html")



@app.route("/logout")
def logout():
    """Logout - link removes User from session and redirects to homepage. Flashes message confirming that User has logged out."""
    
    # password seems to not be in keychain anymore...i think this is a good thing?

    session.pop("login")
    flash("You've successfully logged out. Goodbye.")
    return redirect("/")


@app.route("/register", methods = ["GET", "POST"])
def registration_form():
    """GET - Displays a form for new users to enter information and connect to Mint
        POST - adds registration data to DB --> redirect to transaction analysis
        (or choose to browse challenges --> redirect to challenge browser tool)"""

    if request.method == "POST":

        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["email"]
        password = request.form["password"]
        age = request.form["age"]
        zipcode = request.form["zipcode"]

        mint_username = request.form["mint_username"]
        mint_password = request.form["mint_password"]

        if User.query.filter(User.email == email).first():
            flash("Hmm...we already have your email account on file. Please log in.")
            return redirect("/login")
        else:
            new_user = User(firstname = firstname, lastname = lastname, email = email,
                            password = password, mint_username = mint_username,
                            age = age, zipcode = zipcode)
            db.session.add(new_user)
            db.session.commit()

            session["login"] = email
            keyring.set_password("system", mint_username, mint_password)
            load_transactions(mint_username)

            flash("Thanks for creating an account!")
            return redirect("/")

    return render_template("register.html")


@app.route("/challenge_builder")
def challenge_builder_step1():
    """Displays an interactive form for users to create their own challenge by interacting with
        existing challenge and donation objects and calculating amount of times they are
        willing to substitute

        STEP 1: iterate through all challenge objects and put original_items into the challenges list, which gets put into a dropdown in challenge_builder.html"""

    challenges_list = db.session.query(Challenge.original_items).all()
    challenges_list = [challenge[0] for challenge in challenges_list]

    return render_template("challenge_builder.html", challenges_list = challenges_list)


@app.route("/challenge_builder_step2/<path:original_items>")
def challenge_builder_step2(original_items):
    """sends challenge object information back to challenge_builder form,
        including raw price difference for savings calculator"""

    challenge_obj = Challenge.query.filter(Challenge.original_items == original_items).first()
    
    alternative_items = challenge_obj.alternative_items
    original_cost = challenge_obj.original_cost
    alternative_cost = challenge_obj.alternative_cost

    savings = original_cost - alternative_cost

    return jsonify(original_items = original_items, alternative_items = alternative_items,
                    savings = savings)


@app.route("/challenge_builder_step3/<int:donation_amt>")
def challenge_builder_step3(donation_amt):
    """match calcualted donation_amt from form to donation_price in database"""
    
    max_donation_amt = int(donation_amt) + 3
    min_donation_amt = int(donation_amt) - 3
    print donation_amt
    
    donation_obj_list = Donation.query.filter(Donation.donation_price < max_donation_amt,
                                            Donation.donation_price > min_donation_amt,)

    donation_item_price = []

    for donation_obj in donation_obj_list:
        donation_item = donation_obj.donation_item
        donation_price = donation_obj.donation_price
        donation_item_price.append((donation_item, donation_price))

    print donation_item_price

    return jsonify(donation_item_price = donation_item_price)

@app.route("/transaction_analysis")
def display_transaction_analysis():
    """Scrapes data from Mint account and displays an analysis of transactions by category.
        Identfies places where User spends more money than necessary - ratio of "groceries"
        to "restaurants", search for key words like "Starbucks" or "cafe". Could also focus on week by week.
        Finds relevant challenges and displays challenge info for User, along with "Accept" buttons"""

    return "Graph of transactions, challenge info."


@app.route("/profile", methods=["GET", "POST"])
def profile():
    """Displays any relevant user information along with overall progress towards achieving challenges.
        Links to progress on specific challenges.
        Links to transaction analysis - and/or displays summarized version?"""

    a_user = User.query.filter(User.email == session["login"]).one()

    if request.method == "POST":
        original_items = request.form.get("original_items")
        qty = request.form.get("qty")
        donation_item = request.form.get("donation_item")

        challenge_id = db.session.query(Challenge.challenge_id).filter(
                            Challenge.original_items == original_items).one()
        donation_id = db.session.query(Donation.donation_id).filter(
                            Donation.donation_item == donation_item).one()
        accepted_at = datetime.datetime.now()
        # completed_at = datetime.datetime.now() + datetime.timedelta(days = 2)
        
        accepted_challenge = Accepted_Challenge(user_id = a_user.user_id,
                                                challenge_id = challenge_id[0],
                                                donation_id = donation_id[0],
                                                accepted_qty = qty,
                                                accepted_at = accepted_at)
                                                # completed_at = completed_at)  

        db.session.add(accepted_challenge)
        db.session.commit()
        flash("You have successfully added a challenge!")

    users_current_challenges, users_completed_challenges = a_user.accepted_challenge_info(a_user.user_id)

    return render_template("profile.html", firstname = a_user.firstname,
                                        user_id = a_user.user_id,
                                        users_current_challenges = users_current_challenges,
                                        users_completed_challenges = users_completed_challenges)


@app.route("/overall_progress_chart/<int:user_id>")
def overall_progress_chart(user_id):
    """Sends relevant challenge data to display on the overall_progress_chart on the profile page"""

    users_current_challenges, users_completed_challenges = a_user.accepted_challenge_info(user_id)
    
    pass


@app.route("/view_challenge")
def view_challenge():
    """Display progress and information on individual challenges.
    Offers a way for User to update progress:
        2 options:
            1) enter in units completed - one coffee brewed instead of bought
            2) or perform another transactional analysis and assess progress (might be more interesting and challenging, but I'm not sure if I have enough information from Mint/broad categories of spending
        Either way - can make donation amount suggested/optional rather than required ("I estimate you will have saved $x, but really you saved $y - donate that instead")"""

    ac_id = request.args["ac_id"]
    ac_obj = Accepted_Challenge.query.get(ac_id)
    qty = ac_obj.accepted_qty
    alternative_items = ac_obj.challenge.alternative_items
    alternative_cost = ac_obj.challenge.alternative_cost
    original_items = ac_obj.challenge.original_items
    original_cost = ac_obj.challenge.original_cost
    donation_item = ac_obj.donation.donation_item
    donation_price = ac_obj.donation.donation_price

    return render_template("view_challenge.html", ac_id = ac_id, qty = qty,
                                                alternative_items = alternative_items,
                                                alternative_cost = alternative_cost,
                                                original_items = original_items,
                                                original_cost = original_cost,
                                                donation_item = donation_item,
                                                donation_price = donation_price)


@app.route("/update_progress")
def update_progress():
    """Logs progress updates by taking information from the view challenge page
        and adding progress objects"""

    pass

@app.route("/cancel_challenge")
def cancel_challenge():
    """Removes accepted_challenge object from database and redirects to profile
        - challenge lists should display the updated information."""

    #TODO - remove accepted challenge object
    ac_id = request.args["ac_id"]
    ac_obj = Accepted_Challenge.query.get(ac_id)

    db.session.delete(ac_obj)

    # TODO - make sure progress object functionality works here

    ac_progress_objs = ac_obj.progress_updates
    for progress_obj in ac_progress_objs:
        db.session.delete(progress_obj)

    db.session.commit()

    return redirect("/profile")


@app.route("/donate")
def donate():
    """Access payment gateway for appropriate organization
        Use paypal?"""

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