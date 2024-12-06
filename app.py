import urllib.parse
from channel import Channel
from config import ConfigManager
from db import DataBase
from coin import Coin, Symbol, Crypto
from altseason import AltSeason


def difference(current_price, last_price):
    absolute = abs(current_price - last_price)
    percentage = (absolute / max(last_price, current_price)) * 100

    if current_price > last_price:
        sign = '+'
    elif current_price < last_price:
        sign = '-'
    else:
        sign = ''

    return sign, str(percentage)


def format_number(number_str):
    if number_str.endswith('.00'):
        number_str = number_str[:-3]
    number = float(number_str)
    formatted_number = '{:,.0f}'.format(number)
    return formatted_number


if __name__ == "__main__":

    config = ConfigManager()
    config = config.read()
    coin = Coin(config, Crypto.POOH)

    database = DataBase(config)
    exists = database.exists()

    if not exists:
        success = database.connect()
        if success:
            database.migrate()

    database.connect()
    channel = Channel(config)
    try:
        config = ConfigManager()
        config = config.read()
        coin = Coin(config, Crypto.POOH)
        enabled = config["enabled"]
        tolerance = config["tolerance"]
        if enabled:
            current_price = coin.price(Symbol.USD, 12)
            marketcap = coin.marketcap(Symbol.USD, 2)
            row = database.get_last_record()
            if row is not None:
                last_price = coin.last_price(row, 12)
                flag = False

                if float(current_price) >= (float(last_price) * (1.0 + (tolerance / 100.0))):
                    flag = True
                elif float(current_price) <= (float(last_price) * (1.0 - (tolerance / 100.0))):
                    flag = True

                if (flag):
                    sign, changed = difference(
                        float(current_price), float(last_price))
                    changed = "{:.2f}".format(float(changed))

                    alt_season_message = ""
                    alt_season = AltSeason("https://www.blockchaincenter.net/en/altcoin-season-index/")
                    index_value, percentage_value = alt_season.get_current_index()
                    if index_value is not None and percentage_value is not None:
                        alt_season_message = "AltSeason: Z (Index X-Y)"
                        alt_season_message = alt_season_message.replace("X", index_value)
                        alt_season_message = alt_season_message.replace("Y", percentage_value)

                        if index_value >= percentage_value:
                           alt_season_message = alt_season_message.replace("Z", "Yes")
                        else:
                             alt_season_message = alt_season_message.replace("Z", "No")

                    channel.send_message("$" + Crypto.POOH.upper() + "\nPrice: $" + str(
                        current_price) + " USD\nMarketCap: $" + format_number(str(marketcap)) + " " + Symbol.USD.upper() +
                        "\nChange: " + sign + changed + "%"
                        "\n" + alt_season_message + "\n\n"
                        "<a href=\"https://app.uniswap.org/swap?inputCurrency=ETH&outputCurrency=0xb69753c06bb5c366be51e73bfc0cc2e3dc07e371\">Buy POOH</a> | " + 
                        "<a href=\"https://www.dextools.io/app/en/ether/pair-explorer/0xaf06e7c7170eb22d52eb09b5ec5d1373c34164e9\">Chart</a> | " +
                        "<a href=\"https://etherscan.io/token/0xb69753c06bb5c366be51e73bfc0cc2e3dc07e371#balances\">Holders</a>")
                    database.add_record(current_price)
            else:
                database.add_record(current_price)
    except Exception:
        pass
