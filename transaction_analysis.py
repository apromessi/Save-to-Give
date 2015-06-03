from model import Transaction, connect_to_db, db
import datetime
import mintapi
import keyring
import pandas as pd


def get_transactions(mint_username, mint_password):
    """Grab transactions from mintapi and create transaction objects.
    BUT - don't load them into database."""

    # mint_password = keyring.get_password("system", mint_username)
    mint = mintapi.Mint(mint_username, mint_password)
    user_transactions = mint.get_transactions()

    categories = set([])

    for i in range(len(user_transactions.index)):
        date = str(user_transactions["date"][i])[:10]
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
        description = user_transactions["description"][i]
        category = user_transactions["category"][i]
        categories.add(category)
        amount = float(user_transactions["amount"][i])
        transaction_obj = Transaction(date = date, description = description,
                                        category = category, amount = amount)

    return categories


# def transaction_category_analysis(user_id):
#     """Determine how many transactions a user has made in each Mint category.
#         How much have they spent per category? What percent is that of the whole?"""

#     pass

# def load_transactions(mint_username):
#     """Load transactions from mintapi into database."""

#     mint_password = keyring.get_password("system", mint_username)
#     mint = mintapi.Mint(mint_username, mint_password)
#     user_transactions = mint.get_transactions()

#     for i in range(len(user_transactions.index)):
#         date = str(user_transactions["date"][i])[:10]
#         date = datetime.datetime.strptime(date, "%Y-%m-%d")
#         description = user_transactions["description"][i]
#         category = user_transactions["category"][i]
#         amount = float(user_transactions["amount"][i])
#         transaction_obj = Transaction(user_id = 1, date = date, description = description,
#                                         category = category, amount = amount)
#         # TODO: fix user_id to refer to the user currently logged in, and change parameters to also refer to the user currently logged in --- call it in app (in register/log in routes) rather than in name == main.
#         db.session.add(transaction_obj)
    
#     db.session.commit()