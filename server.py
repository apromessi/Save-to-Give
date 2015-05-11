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
        return "<User Object: user_id = %s, email = %s>" % (self.user_id, self.email)


class Challenges(db.Model):
    """Challenges for the user - connects directly to relevant organization"""

    __tablename__ = "challenges"

    challenge_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    # do I need organization id as a foreign key?
    product_name = db.Column(db.String(100), nullable = False)
    description = db.Column(db.String(1000)) # not sure if this will be necessary
    challenge_price = db.Column(db.Integer, nullable = False)
    original_cost = db.Column(db.Integer)
    alternative_cost = db.Column(db.Integer) # do I really need all 3 costs or should I do math instead?
    