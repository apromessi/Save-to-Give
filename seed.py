from model import User, Donation, Challenge, Organization, connect_to_db, db
from server import app


def load_users():
    """
    load fake users from users.csv into database
    """

    users_file = open("./seed_data/users.csv")

    for text in users_file:
        lines = text.strip().splitlines()
        for line in lines:
            line = line.split(",")
            a_user = User(firstname=line[1],
                          lastname=line[2],
                          email=line[3],
                          password=line[5])
            db.session.add(a_user)

    db.session.commit()


def load_challenges():
    """
    load challenge estimates from challenges.csv into database
    """

    challenges_file = open("./seed_data/challenges.csv")

    for text in challenges_file:
        lines = text.strip().splitlines()
        for line in lines:
            line = line.split(",")
            a_challenge = Challenge(original_items=line[1],
                                    original_cost=float(line[2]),
                                    alternative_items=line[3],
                                    alternative_cost=float(line[4]))
            db.session.add(a_challenge)

    db.session.commit()


def load_donations():
    """
    load donation options from donations.csv into database
    """

    donations_file = open("./seed_data/donations.csv")

    for text in donations_file:
        lines = text.strip().splitlines()
        for line in lines:
            line = line.split("#")
        a_donation = Donation(org_id=line[1],
                              donation_item=line[2],
                              description=line[3].strip('"'),
                              donation_price=float(line[4]))
        db.session.add(a_donation)

    db.session.commit()


def load_orgs():
    """
    load organization table from orgs.csv into database
    """

    orgs_file = open("./seed_data/orgs.csv")

    for text in orgs_file:
        lines = text.strip().splitlines()
        for line in lines:
            line = line.split(",")
        an_organization = Organization(org_name=line[1],
                                       payment_method=line[2],
                                       org_url=line[3])
        db.session.add(an_organization)

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    load_users()
    load_challenges()
    load_donations()
    load_orgs()
