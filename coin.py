import requests


class Coin:
    def __init__(self, config, coin):
        self.api = config["api"]
        self.api = self.api.replace("{COIN}", coin)
        self.data = None
        self.read()

    def price(self, symbol, decimal):
        price = self.data["market_data"]["current_price"][symbol]
        price = "{:.{}f}".format(price, decimal)
        return price

    def marketcap(self, symbol, decimal):
        marketcap = self.data["market_data"]["market_cap"][symbol]
        marketcap = "{:.{}f}".format(marketcap, decimal)
        return marketcap

    def last_price(self, row, decimal):
        return "{:.{}f}".format(row[0], decimal)

    def read(self):
        try:
            self.data = requests.get(self.api).json()
            return self.data
        except Exception:
            return None


class Symbol:
    USD = "usd"
    MXN = "mxn"


class Crypto:
    POOH = "pooh"
