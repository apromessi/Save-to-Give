from model import Accepted_Challenge, Progress_Update, connect_to_db, db
from server import app
import datetime


def load_accepted_challenges():
    """
    clear accepted challenges from database and reload fake accepted_challenges
    for demo from accepted_challenges.csv into database.
    """

    db.session.query(Accepted_Challenge).delete()

    accepted_challenges_file = open("./seed_data/accepted_challenges.csv")

    for text in accepted_challenges_file:
        lines = text.strip().splitlines()
        for line in lines:
            line = line.split(",")
            if line[6] != "":
                accepted_at = datetime.datetime.strptime(
                    line[5], "%Y-%m-%d %H:%M:%S.%f")
                completed_at = datetime.datetime.strptime(
                    line[6], "%Y-%m-%d %H:%M:%S.%f")
                accepted_challenge = Accepted_Challenge(
                    user_id=line[1],
                    challenge_id=line[2],
                    donation_id=line[3],
                    accepted_qty=line[4],
                    accepted_at=accepted_at,
                    completed_at=completed_at)
            else:
                accepted_at = datetime.datetime.strptime(
                    line[5], "%Y-%m-%d %H:%M:%S.%f")
                accepted_challenge = Accepted_Challenge(
                    user_id=line[1],
                    challenge_id=line[2],
                    donation_id=line[3],
                    accepted_qty=line[4],
                    accepted_at=accepted_at)
            db.session.add(accepted_challenge)

    db.session.commit()


def load_progress_updates():
    """
    clear progress updates from database and reload fake progress_updates
    for demo from progress_updates.csv into database
    """

    db.session.query(Progress_Update).delete()

    progress_updates_file = open("./seed_data/progress_updates.csv")

    for text in progress_updates_file:
        lines = text.strip().splitlines()
        for line in lines:
            line = line.split(",")
            updated_at = datetime.datetime.strptime(
                line[2], "%Y-%m-%d %H:%M:%S.%f")
            progress_update = Progress_Update(ac_id=line[1],
                                              updated_at=updated_at,
                                              update_amt=line[3])
            db.session.add(progress_update)

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    load_accepted_challenges()
    load_progress_updates()
