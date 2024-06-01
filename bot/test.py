from fetch_data import *
from order import *


def run_test():
    print(fetch_balance(binance_test, "BNB"))
    print(fetch_balance(binance_test, "USDT"))
    order_details = buy(binance_test, "BNB", "USDT", 5)
    print(order_details)
    print(fetch_balance(binance_test, "BNB"))
    print(fetch_balance(binance_test, "USDT"))
    pass


run_test()
