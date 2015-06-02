from jinja2 import StrictUndefined
import os
import keyring
import datetime
from dateutil.tz import tzlocal

from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import (User, Challenge, Accepted_Challenge, Donation, Transaction,
                    Organization, Progress_Update, connect_to_db, db)
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


@app.route("/donation_info/<int:donation_id>")
def donation_info(donation_id):
    """Display information about each donation item, including price, description and org"""

    donation_obj = Donation.query.get(donation_id)
    org_obj = Organization.query.get(donation_obj.org_id)
    print org_obj

    return render_template("donation_info.html", donation_obj = donation_obj, org_obj = org_obj)


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


@app.route("/challenge_builder_step3/<float:donation_amt>")
def challenge_builder_step3(donation_amt):
    """match calculated donation_amt from form to donation_price in database"""
    
    donation_object_list = Donation.query.order_by("ABS(donation_price - " +
                                                     str(donation_amt) + ")").all()
    donation_object_list = donation_object_list[:3]

    donation_objects_dicts = []

    for donation_obj in donation_object_list:
        org_obj = Organization.query.get(donation_obj.org_id)
        org_name = org_obj.org_name
        donation_obj = donation_obj.__dict__
        donation_obj["org_name"] = org_name
        donation_obj.pop("_sa_instance_state")
        donation_objects_dicts.append(donation_obj)

    return jsonify(donation_objects = donation_objects_dicts)


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
        accepted_at = datetime.datetime.now(tzlocal())
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

    user_obj = User.query.get(user_id)
    accepted_challenges = user_obj.accepted_challenges

    progress_updates_dicts = []
    goal = 0

    for ac_obj in accepted_challenges:
        progress_updates = ac_obj.progress_updates
        accepted_at = {"updated_at": ac_obj.accepted_at, "update_amt": 0}
        progress_updates_dicts.append(accepted_at)
        # not sure if I want to add accepted_at for every challenge or not
        for update in progress_updates:
            update = update.__dict__
            update.pop("_sa_instance_state")
            progress_updates_dicts.append(update)
        goal += ac_obj.donation.donation_price

    progress_updates_dicts = [(update['updated_at'], update) for update in progress_updates_dicts]
    progress_updates_dicts.sort()
    progress_updates_dicts = [update for (key, update) in progress_updates_dicts]
                                                                                                                       
    return jsonify(progress_updates = progress_updates_dicts, goal = goal)


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
    completed_at = ac_obj.completed_at
    total_progress = ac_obj.calculate_total_progress()
    donation_description = ac_obj.donation.description
    org_name = Organization.query.get(ac_obj.donation.org_id).org_name

    return render_template("view_challenge.html", ac_id = ac_id, qty = qty,
                                                alternative_items = alternative_items,
                                                alternative_cost = alternative_cost,
                                                original_items = original_items,
                                                original_cost = original_cost,
                                                donation_item = donation_item,
                                                donation_price = donation_price,
                                                completed_at = completed_at,
                                                total_progress = total_progress,
                                                donation_description = donation_description,
                                                org_name = org_name)


@app.route("/indiv_progress_chart/<int:ac_id>")
def indiv_progress_chart(ac_id):
    """Provides progress information for chart on view_challenge.html"""

    ac_obj = Accepted_Challenge.query.get(ac_id)
    progress_updates = ac_obj.progress_updates
    progress_updates_dicts = []
    accepted_at = {"updated_at": ac_obj.accepted_at, "update_amt": 0}
    progress_updates_dicts.append(accepted_at)
    for update in progress_updates:
        update = update.__dict__
        update.pop("_sa_instance_state")
        progress_updates_dicts.append(update)
    goal = ac_obj.donation.donation_price
                                                                                                                       
    return jsonify(progress_updates = progress_updates_dicts, goal = goal)


@app.route("/update_progress", methods = ["POST"])
def update_progress():
    """Logs progress updates by taking information from the view challenge page
        and adding progress objects"""

    ac_id = request.form["ac_id"]
    progress_amt = request.form["progress_amt"]
    ac_obj = Accepted_Challenge.query.get(ac_id)

    progress_update = Progress_Update(ac_id = ac_id,
                                    updated_at = datetime.datetime.now(),
                                    update_amt = progress_amt)
    db.session.add(progress_update)

    total_progress = ac_obj.calculate_total_progress()
    print total_progress
    ac_obj.determine_completion()
    print ac_obj.completed_at, "****************************"

    db.session.commit()

    return redirect("/view_challenge?ac_id=" + str(ac_id))
    

@app.route("/cancel_challenge")
def cancel_challenge():
    """Removes accepted_challenge object from database and redirects to profile
        - challenge lists should display the updated information."""

    ac_id = request.args["ac_id"]
    ac_obj = Accepted_Challenge.query.get(ac_id)

    db.session.delete(ac_obj)

    ac_progress_objs = ac_obj.progress_updates
    for progress_obj in ac_progress_objs:
        db.session.delete(progress_obj)

    db.session.commit()

    return redirect("/profile")


@app.route("/donate/<int:ac_id>")
def donate(ac_id):
    """Access payment gateway for appropriate organization
        Use paypal?
        Set accepted_challenge completed_at attribute to current time.
        Create a progress_updates with full donation price as update_amt and 
        updated_at as current time"""

    ac_obj = Accepted_Challenge.query.get(ac_id)
    if ac_obj.completed_at == None:
        ac_obj.completed_at = datetime.datetime.now()
        completed_prog_obj = Progress_Update(ac_id = ac_id,
                                            updated_at = datetime.datetime.now(),
                                            update_amt = ac_obj.donation.donation_price)
        db.session.add(completed_prog_obj)

    org_id = ac_obj.donation.org_id
    org_obj = Organization.query.get(org_id)
    donation_item = ac_obj.donation.donation_item
    original_items = ac_obj.challenge.original_items

    db.session.commit()

    return render_template("donate.html", org_obj = org_obj, donation_item = donation_item,
                            original_items = original_items)


##########################################################################################
if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()