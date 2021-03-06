import datetime
import random
import mintapi
import keyring


class Transaction(object):
    """
    Contains transaction data from mintapi - NOT STORED IN DB
    """

    def __init__(self, transaction_id, date, description, category, amount):
        self.transaction_id = transaction_id
        self.date = date
        self.description = description
        self.category = category
        self.amount = amount

    def __repr__(self):
        return "<Trans Object: %s user_id=%s, category = %s, amount = %s>" % (
            self.transaction_id, self.user_id, self.category, self.amount)


def get_transactions(mint_username, mint_password):
    """
    Grab transactions from mintapi and create transaction objects.
    BUT - don't load them into database.
    """

    # NOTE - for demo use secrets file for authentication instead of keyring

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
        categories[str(category).strip()] = 0
        amount = float(user_transactions["amount"][i])
        transaction_obj = Transaction(transaction_id=i,
                                      date=date,
                                      description=description,
                                      category=category,
                                      amount=amount)
        transaction_obj_list.append(transaction_obj)

    categories_to_remove = set(["paycheck", "bills & utilities",
                                "business services", "transfer",
                                "federal tax", "credit card payment",
                                "nan", "financial", "income",
                                "interest income", "pharmacy", "check",
                                "atm fee", "doctor", "air travel", "hotel",
                                "gas & fuel"])

    for category in categories.keys():
        if category in categories_to_remove:
            del categories[category]

    for transaction_obj in transaction_obj_list:
        category = transaction_obj.category
        if category in categories.keys():
            categories[category] += transaction_obj.amount

    categories_to_group = {"entertainment": ("amusement",
                                             "entertainment",
                                             "music",
                                             "sports"),
                           "restaurants": ("restaurants",
                                           "food & dining",
                                           "fast food"),
                           "shopping": ("clothing",
                                        "books",
                                        "electronics & software",
                                        "hair"),
                           "taxi": ("taxi",
                                    "rental car & taxi")}

    for category in categories_to_group.keys():
        for grouped_category in categories_to_group[category]:
            if grouped_category != category:
                categories[category] += categories[grouped_category]
                del categories[grouped_category]

    return categories


def spending_category_analysis(categories):
    """
    Analyzes spending habits by comparing related buckets (eg. public transit
    to taxis)
    """

    challenge_ids = []

    # GROUPS:
    cafe_challenges = [1, 4]
    grocery_challenges = [5, 6]
    restaurant_challenges = [2, 3]
    alcohol_challenges = [7, 8, 9]
    transit_challenges = [12]
    entertainment_challenges = [10, 11]

    if categories["coffee shops"]/categories["groceries"] > .3:
        challenge_ids.extend(cafe_challenges)

    if categories["groceries"] > 300:
        challenge_ids.extend(grocery_challenges)

    if categories["restaurants"] > categories["groceries"]:
        challenge_ids.extend(restaurant_challenges)

    if categories["alcohol & bars"] * 2 > categories["restaurants"]:
        challenge_ids.extend(alcohol_challenges)

    if categories["taxi"] > categories["public transportation"]:
        challenge_ids.extend(transit_challenges)

    if categories["entertainment"] > 200:
        challenge_ids.extend(entertainment_challenges)

    if challenge_ids == []:
        challenge_ids = random.sample(range(1, 13), 3)

    return challenge_ids
