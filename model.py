"""Models and database functions for final project"""

from flask_sqlalchemy import SQLAlchemy
import datetime
db = SQLAlchemy()

class User(db.Model):
    """User data - includes access to their mint account"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    email = db.Column(db.String(64), nullable = False)
    mint_username = db.Column(db.String(64))
    password = db.Column(db.String(40), nullable = False)
    zipcode = db.Column(db.String(15)) # placeholder for now - in case location analysis later
    age = db.Column(db.Integer) # placeholder for now - in case demographic analysis later
    # removed mint password from database - intead going to try and use keychain

    def accepted_challenge_info(self, user_id):
        """Provides all relevant info about users current and completed challenges.
            Takes user_id as parameter and returns current and
            completed challenges as 2 lists within a list."""
        
        users_ac_objects = Accepted_Challenge.query.filter(
                            Accepted_Challenge.user_id == user_id).all()

        users_current_challenges = []
        users_completed_challenges = []
        
        for ac_object in users_ac_objects:
            qty = ac_object.accepted_qty
            alternative_items = ac_object.challenge.alternative_items
            original_items = ac_object.challenge.original_items
            donation_item = ac_object.donation.donation_item
            donation_price = ac_object.donation.donation_price
            
            total_progress = ac_object.calculate_total_progress()
            progress_percent = total_progress/ac_object.donation.donation_price

            if ac_object.completed_at == None:
                challenge = (qty, alternative_items, original_items, donation_item,
                            donation_price, progress_percent, ac_object.ac_id)
                users_current_challenges.append(challenge)
            else:
                challenge = (qty, alternative_items, original_items, donation_item,
                            donation_price, ac_object.completed_at, ac_object.ac_id)
                users_completed_challenges.append(challenge)

        return [users_current_challenges, users_completed_challenges]


    def __repr__(self):
        return "<User Object: %s email = %s>" % (self.user_id, self.email)


class Donation(db.Model):
    """Donation objects that connect directly to relevant organization
        Connect to challenges table via association table and
        matching donation_amount and savings from challenge"""

    __tablename__ = "donations"

    donation_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    org_id = db.Column(db.Integer, db.ForeignKey("organizations.org_id"))
    donation_item = db.Column(db.String(100), nullable = False)
    description = db.Column(db.String(1000)) # not sure if this will be necessary
    donation_price = db.Column(db.Float, nullable = False)
    # make amount a suggested donation?

    def __repr__(self):
        return "<Donation Object: %s donation_item = %s, donation_price = %s>" % (
                self.donation_id, self.donation_item, self.donation_price)


class Challenge(db.Model):
    """Challenges for the user
        connects to matching donations via savings and donation_amount"""

    __tablename__ = "challenges"

    challenge_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    original_items = db.Column(db.String(100))
    original_cost = db.Column(db.Float)
    alternative_items = db.Column(db.String(100))
    alternative_cost = db.Column(db.Float)

    # 

    def __repr__(self):
        return "<Challenge Object: %s, original_items = %s>" % (
                self.challenge_id, self.original_items)


class Accepted_Challenge(db.Model):
    """Connects User, Challenge, and Donation classes.
        Stores information about user's specific challenges."""

    __tablename__ = "accepted_challenges"

    ac_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.challenge_id"))
    donation_id = db.Column(db.Integer, db.ForeignKey("donations.donation_id"))
    accepted_qty = db.Column(db.Integer)
    accepted_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    challenge = db.relationship("Challenge", backref = db.backref("accepted_challenges"))
    user = db.relationship("User", backref = db.backref("accepted_challenges"))
    donation = db.relationship("Donation", backref = db.backref("accepted_challenge"),
                                uselist=False)

    def calculate_total_progress(self):
        progress_updates = self.progress_updates
        total_progress = 0
        for update in progress_updates:
            total_progress += float(update.update_amt)
        return total_progress
        # or do I want percentage?

    def determine_completion(self):
        if self.completed_at == None:
            total_progress = self.calculate_total_progress()
            donation_price = self.donation.donation_price
            if total_progress >= donation_price:
                self.completed_at = datetime.datetime.now()

    def __repr__(self):
        return "<Accepted_Challenge Object: %s user_id=%s, challenge_id=%s>" % (
                self.ac_id, self.user_id, self.challenge_id)


class Progress_Update(db.Model):
    """Stores progress towards completing specific challenges.
        (information about separate update events, which, when combined, will be used to
        determine when a user has completed a challenge and can donate the money they saved.
        Progress update timestamps and amounts will be shown on the charts.)"""

    __tablename__ = "progress_updates"

    progress_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    ac_id = db.Column(db.Integer, db.ForeignKey("accepted_challenges.ac_id"))
    updated_at = db.Column(db.DateTime)
    update_amt = db.Column(db.Float)

    accepted_challenge = db.relationship("Accepted_Challenge",
                                            backref = db.backref("progress_updates"))

    def __repr__(self):
        return "<Progress Update Object: %s ac_id=%s, update_amt=%s, updated_at=%s" % (
                self.progress_id, self.ac_id, self.update_amt, self.updated_at)


class Transaction(db.Model):
    """Contains transaction data from mintapi"""

    __tablename__ = "transactions"

    transaction_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    date = db.Column(db.DateTime)
    description = db.Column(db.String(100))
    category = db.Column(db.String(64))
    amount = db.Column(db.Float)
    # add more info for whether a particular transaction counts towards a challenge - would also allow user to input relevant transactions - or apply an existing transaction to progress?
    user = db.relationship("User", backref = db.backref("transactions"))

    def __repr__(self):
        return "<Transaction Object: %s user_id=%s, category = %s, amount = %s>" % (
                self.transaction_id, self.user_id, self.category, self.amount)


class Organization(db.Model):
    """Organization data pertaining to specific challenges."""

    __tablename__ = "organizations"

    org_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    org_name = db.Column(db.String(100))
    payment_method = db.Column(db.String(100)) # not quite sure what these will be yet
    org_url = db.Column(db.String(500)) # not sure if this is necessary - placeholder

    donations = db.relationship("Donation", backref = db.backref('donations'))

    def __repr__(self):
        return "<Organization Object: %s org_name = %s>" % (
                self.org_id, self.org_name)

##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///secrets.db'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."