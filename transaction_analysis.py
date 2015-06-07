from model import connect_to_db, db
import datetime
import random
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
        categories[str(category).strip()] = 0
        amount = float(user_transactions["amount"][i])
        transaction_obj = Transaction(date = date, description = description,
                                        category = category, amount = amount)
        transaction_obj_list.append(transaction_obj)

    categories_to_remove = set(["paycheck", "bills & utilities", "business services", "transfer",
                                "federal tax", "credit card payment", "nan", "financial", "income",
                                "interest income", "pharmacy", "check", "atm fee", "doctor", 
                                "air travel", "hotel", "gas & fuel"])

    for category in categories.keys():
        if category in categories_to_remove:
            del categories[category]


    for transaction_obj in transaction_obj_list:
        category = transaction_obj.category
        if category in categories.keys():
            categories[category] += transaction_obj.amount

    categories_to_group = {"entertainment": ("amusement", "entertainment", "music", "sports"),
                            "taxi": ("taxi", "rental car & taxi"),
                            "shopping": ("clothing", "books", "electronics & software", "hair"),
                            "restaurants": ("restaurants", "food & dining", "fast food")}

    for category in categories_to_group.keys():
        for grouped_category in categories_to_group[category]:
            if grouped_category != category:
                categories[category] += categories[grouped_category]
                del categories[grouped_category]

    return categories


def spending_category_analysis(categories):
    """analyzes spending habits by comparing related buckets (eg. public transit 
        to taxis) [and by comparing your spending with average spending in SF 
        according to the Intuit Consumer Spending Index, based on user data 
        from Mint. --- don't have this data yet, hoping for a response to inquiry]"""

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
        challenge_ids.extend("alcohol_challenges")

    if categories["taxi"] > categories["public transportation"]:
        challenge_ids.extend(transit_challenges)

    if categories["entertainment"] > 200:
        challenge_ids.extend(entertainment_challenges)

    if challenge_ids == []:
        challenge_ids = random.sample(range(1, 13), 3)

    return challenge_ids

    
