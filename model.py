"""Models and database functions for final project"""

from flask_sqlalchemy import SQLAlchemy
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
        return "<Donation Object: %s product_name = %s, donation_amount = %s>" % (
                self.donation_id, self.product_name, self.donation_amount)


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
    """Connects User and Challenge classes
        Stores progress towards completing challenges"""

    __tablename__ = "accepted_challenges"

    ac_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.challenge_id"))
    donation_id = db.Column(db.Integer, db.ForeignKey("donations.donation_id"))
    progress = db.Column(db.Float, nullable = False)
    completed_at = db.Column(db.DateTime)

    challenge = db.relationship("Challenge", backref = db.backref("accepted_challenges"))
    user = db.relationship("User", backref = db.backref("accepted_challenges"))
    donation = db.relationship("Donation", backref = db.backref("accepted_challenge"), uselist=False)

    def __repr__(self):
        return "<Accepted_Challenge Object: %s user_id=%s, challenge_id=%s, progress = %s>" % (
                self.ac_id, self.user_id, self.challenge_id, self.progress)


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