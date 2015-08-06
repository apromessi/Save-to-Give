def load_mint_auth():
    """
    Load mint authentication info from secrets file (which is not in github but
    stored locally). Purpose is to make demo-ing easier.
    """

    secrets = open("./secrets.txt")

    mint_auth = []

    for line in secrets:
        line = line.strip()
        mint_auth.append(line)

    return mint_auth
