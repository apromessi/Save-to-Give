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

    categories = {}
    transaction_obj_list = []

    for i in range(len(user_transactions.index)):
        date = str(user_transactions["date"][i])[:10]
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
        description = user_transactions["description"][i]
        category = user_transactions["category"][i]
        categories[category] = 0
        amount = float(user_transactions["amount"][i])
        transaction_obj = Transaction(date = date, description = description,
                                        category = category, amount = amount)
        transaction_obj_list.append(transaction_obj)

    for transaction_obj in transaction_obj_list:
        category = transaction_obj.category
        categories[category] += transaction_obj.amount

    return categories