from fetch_data import *
from order import *
from main import *
import math
from safety import *
from symbols import *


def run_test():

    # print(fetch_balance(binance, "USDT"))
    # print(fetch_balance(binance, "BTC"))

    # # print(buy(binance, "BTC", "USDT", 10))
    # print(sell(binance, "BTC", "USDT", 100))
    # print(fetch_balance(binance, "USDT"))
    # print(fetch_balance(binance, "BTC"))

    # adjust_balances_to_leverage(binance, binance_futures, 5)
    # print(fetch_balance(binance, "USDT"))
    # print(fetch_balance(binance_futures, "USDT"))
    # short(binance_futures, "BTC", 100, 1)
    # fetch_open_positions(binance_futures)
    # close_short(binance_futures, "BTC", "USDT")
    # fetch_open_positions(binance_futures)

    # binance_futures.fapiPrivatePostLeverage
    # adjust_and_hedge("BTC", 5)

    # try_target_short(binance_futures, "BTC", 5)
    # short(binance_futures, "BTC", 100, 5)
    # print(sell_and_close("BTC"))
    # print(fetch_balance(binance, "USDT"))
    # print(fetch_balance(binance, "TRX"))

    # print(buy(binance, "TRX", "USDT", 5))
    # print(fetch_balance(binance, "TRX"))
    # address, tag, network = fetch_deposit_address(coinone, "TRX", False)
    # print(address, tag, network)
    # withdraw(binance, binance_master, "TRX", 10, address, tag, network)
    # print(fetch_balance(binance, "TRX"))

    # print(fetch_balance(binance, "TRX"))
    # balance = fetch_balance(binance, "TRX")
    # transfer_to_master(binance, binance_master, "TRX", balance/10)
    # print(fetch_balance(binance, "TRX"))
    # print(fetch_balance(binance_master, "TRX"))
    print(is_currency_depositable(coinone, "ABL"))
    print(is_trade_suspended_coinone(coinone, "ABL"))
    # print(fetch_available_networks(binance_master, currency))

    # print(fetch_available_networks(coinone, "WLD"))

    pass


if __name__ == "__main__":
    # print(float(set_significant_digits(0.12345678, 6)))

    data = read_address_network_csv("address_network.csv")
    state = State(krw_balance=0, usdt_balance=0)
    # print(conc_find_highest_premium(1300, list(data.keys())))
    # print(safety_check('MINA', data))
    # cycle(state, data)
    print(is_futures_tradable("AMP"))
