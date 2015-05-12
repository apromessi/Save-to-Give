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
    # use one email for now - must match email in mint account
    password = db.Column(db.String(40), nullable = False)
    mint_password = db.Column(db.String(40))
    zipcode = db.Column(db.String(15)) # placeholder for now - in case location analysis later
    age = db.Column(db.Integer) # placeholder for now - in case demographic analysis later

    def __repr__(self):
        return "<User Object: %s email = %s>" % (self.user_id, self.email)


class Challenge(db.Model):
    """Challenges for the user - connects directly to relevant organization"""

    __tablename__ = "challenges"

    challenge_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    # do I need organization id as a foreign key?
    product_name = db.Column(db.String(100), nullable = False)
    description = db.Column(db.String(1000)) # not sure if this will be necessary
    challenge_price = db.Column(db.Integer, nullable = False)
    original_cost = db.Column(db.Integer)
    alternative_cost = db.Column(db.Integer)
    # do I really need all 3 costs or should I do math instead?

    def __repr__(self):
        return "<Challenge Object: %s product_name = %s, challenge_price = %s>" % (
                self.challenge_id, self.product_name, self.challenge_price)

class Accepted_Challenge(db.Model):
    """Connects User and Challenge classes
        Stores progress towards completing challenges"""

    __tablename__ = "accepted_challenges"

    ac_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.challenge_id"))
    progress = db.Column(db.Integer, nullable = False) # can I use a float?
    completed_at = db.Column(db.Datetime)

    def __repr__(self):
        return "<Accepted_Challenge Object: %s user_id=%s, challenge_id=%s, progress = %s>" % (
                self.ac_id, self.user_id, self.challenge_id, self.progress)

class Transaction(db.Model):
    """Contains transaction data from mintapi"""

    __tablename__ = "transactions"

    transaction_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    date = db.Column(db.Datetime)
    description = db.Column(db.String(100))
    category = db.Column(db.String(64))
    amount = db.Column(db.Integer) # can i use a float?
    label = db.Column(db.String(64)) # placeholder because not sure if necessary - shows up in transaction data

    def __repr__(self):
        return "<Transaction Object: %s user_id=%s, category = %s, amount = %s>" % (
                self.transaction_id, self.user_id, self.category, self.amount)

class Organization(db.Model):
    """Organization data pertaining to specific challenges."""

    __tablename__ = "organizations"

    org_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    org_name = db.Column(db.String(100))
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.challenge_id"))
    # or would the challenge have an org id?? which way does the foreign key go?? best practice?
    payment_method = db.Column(db.String(100)) # not quite sure what these will be yet
    org_url = db.Column(db.String(500)) # not sure if this is necessary - placeholder

    def __repr__(self):
        return "<Organization Object: %s org_name = %s>" % (
                self.org_id, self.org_name)