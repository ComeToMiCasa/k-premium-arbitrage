from fetch_data import *
from order import *
from main import *
import math
from safety import *
from symbols import *
import csv
import traceback


def fetch_minimums(currency):

    # Load all markets and currencies from Binance
    markets = binance.load_markets()
    currency_data = binance.currencies[currency]

    # print(currency_data["limits"])
    # print(currency_data)

    def extract_limits(currency_data, markets):
        info = currency_data.get("info", {})
        limits = {}

        # Extract trade limits
        trade_limits = info.get("networkList", [])
        for network in trade_limits:
            if network.get("isDefault", False):
                limits["trade"] = {
                    "min": float(network.get("withdrawMin", 0)),
                    "max": float(network.get("withdrawMax", float("inf"))),
                }
                break

        # Extract withdrawal limits
        withdrawal_limits = info.get("networkList", [])
        for network in withdrawal_limits:
            if network.get("isDefault", False) and network.get("withdrawEnable", False):
                limits["withdrawal"] = {
                    "min": float(network.get("withdrawMin", 0)),
                    "fee": float(network.get("withdrawFee", 0)),
                }
                break

        market = markets[currency + "/USDT"]
        # The minimum notional value is stored in the 'limits' dictionary
        min_notional = market["limits"]["cost"]["min"]

        limits["notional"] = min_notional

        limits["precision"] = market["precision"]

        return limits

    return extract_limits(currency_data, markets)

    # Fetch minimum trade amount and minimum withdrawal amount
    # min_trade_amount = currency_data["limits"]["amount"]["min"]
    # min_withdrawal_amount = currency_data["limits"]["withdraw"]["min"]

    # return {
    #     "minimum_trade_amount": min_trade_amount,
    #     "minimum_withdrawal_amount": min_withdrawal_amount,
    # }


def get_detailed_withdrawal_info(symbol):

    currencies = binance.fetch_currencies()

    if symbol in currencies:
        currency = currencies[symbol]
        info = currency["info"] if "info" in currency else {}

        min_amount = (
            currency["limits"]["withdraw"]["min"]
            if "limits" in currency and "withdraw" in currency["limits"]
            else "Not specified"
        )
        fee = currency["fee"] if "fee" in currency else "Not specified"

        network_fee = info.get("networkFee", "Not specified")
        withdrawal_fee = info.get("withdrawFee", "Not specified")

        return (
            f"{symbol}:\n"
            f"  Minimum withdrawal: {min_amount}\n"
            f"  Total fee: {fee}\n"
            f"  Network fee: {network_fee}\n"
            f"  Withdrawal fee: {withdrawal_fee}\n"
            f"Note: Total fee usually includes both network and withdrawal fees."
        )
    else:
        return f"Currency {symbol} not found"


def fetch_tradable_currencies():
    # Fetch all tradable currencies from Coinone
    coinone_currencies = coinone.fetch_currencies()

    # Fetch market data from Binance spot and futures
    binance_spot_markets = binance.fetch_markets()
    binance_futures_markets = binanceusdm.fetch_markets()

    # Extract currency symbols that are tradable on Binance spot and futures with USDT as the quote
    binance_spot_symbols = {
        market["base"]
        for market in binance_spot_markets
        if market["active"]
        and market["symbol"] == market["base"] + "/USDT"
        and market["spot"]
    }
    binance_futures_symbols = {
        market["base"]
        for market in binance_futures_markets
        if market["active"] and market["symbol"] == market["base"] + "/USDT:USDT"
    }

    # Filter Coinone currencies to find those tradable on both Binance spot and futures
    tradable_currencies = [
        symbol
        for symbol, details in coinone_currencies.items()
        if symbol in binance_spot_symbols and symbol in binance_futures_symbols
    ]

    return tradable_currencies


def fetch_currency_details():
    try:
        # Fetch all tradable currencies
        tradable_currencies = fetch_tradable_currencies()

        # Initialize a dictionary to hold all currency details
        currency_details = {}

        # Iterate over each tradable currency
        for currency in tradable_currencies:
            # Fetch deposit address and tag for the currency
            address, tag = fetch_deposit_address(coinone, currency, True)

            # Fetch available networks for the currency
            networks = fetch_available_networks(binance, currency)

            # Construct a dictionary for the current currency with all details
            currency_info = {
                "address": address,
                "tag": tag,
                "networks": networks,
            }

            # Store the dictionary using the currency as the key
            currency_details[currency] = currency_info

        return currency_details

    except Exception as e:
        print(f"Error in fetch_currency_details: {e}")
        traceback.print_exc()
        return {}


import os
import time
import hmac
import hashlib
import requests
import json


def generate_nonce():
    """
    Generates a nonce using a Unix timestamp.
    """
    return str(int(time.time() * 1000))


def write_currency_details_to_csv():
    try:
        # Fetch currency details
        currency_details = fetch_currency_details()

        # Open a file to write
        with open("target_currency_data.csv", mode="w", newline="") as file:
            writer = csv.writer(file)

            # Write the header
            writer.writerow(["Currency", "Address", "Tag", "Networks"])

            # Write data for each currency
            for currency, details in currency_details.items():
                # Prepare networks data as a string
                networks_str = "; ".join(
                    [f"{net[0]}: {net[1]}" for net in details["networks"]]
                )

                # Write a row for the current currency
                writer.writerow(
                    [currency, details["address"], details["tag"], networks_str]
                )

        print("Data successfully written to target_currency_data.csv")

    except Exception as e:
        print(f"Error in write_currency_details_to_csv: {e}")
        traceback.print_exc()


def buy_minimum_amount(currency):

    limits = fetch_minimums(currency)

    # minimum notional/withdraw worth of crypto
    # cost = max(
    #     limits["notional"], limits["withdrawal"]["min"] + limits["withdrawal"]["fee"]
    # )
    notional_cost = limits["notional"]

    withdraw_min_amount = limits["withdrawal"]["min"] + limits["withdrawal"]["fee"]

    precision = limits["precision"]["amount"]
    # return

    symbol = currency + "/USDT"

    try:
        # Round up the withdraw_min_amount to the nearest valid value based on precision
        step_size = 1 / (10**precision)
        rounded_amount = math.ceil(withdraw_min_amount / step_size) * step_size

        order = binance.create_market_buy_order(symbol, rounded_amount)

    except Exception as e:
        print("Notional error")
        try:
            order = binance.create_market_buy_order_with_cost(symbol, notional_cost)
        except Exception as e:
            print(e)
            return

    return order


def comprehensive_withdraw_test():
    with open("target_currency_data.csv") as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            withdraw_test_cycle(row)

        pass


def withdraw_test_cycle(row):
    currency = row[0]

    buy_order = buy_minimum_amount(currency)

    # print(buy_order)

    network_1 = row[4]

    address, tag, network = fetch_deposit_address(coinone, currency, True)

    if network_1 != network:
        print("network error")
        return

    withdrawal = withdraw(binance, binance_master, currency, 100, address, tag, network)
    # print(withdrawal)
    withdrawal_id = withdrawal["id"]
    # TODO: test withdrawal completion
    wait_for_withdrawal_completion(binance_master, coinone, currency, withdrawal_id)

    sell_order = try_target_sell(currency)

    return buy_order, withdrawal, sell_order

    # print(currency, address, tag, network_1, network_2)


"""
TODO
1. test buy_minimum_amount
2. test withdraw, wait_for_withdrawal_completion
3. test try_target_sell
4. test withdraw_test_cycle
"""


"""
TODO
엑셀 파일에서 withdraw test 할 코인 확인
돈 떨어질때까지 테스트하고 한 것 체크
전부 USDT로 바꿔서 수익 비교
이후 반복
"""


def run_test():

    # print(fetch_minimums("EOS"))
    # print(fetch_available_networks(binance, "EOS"))
    # print(len(fetch_tradable_currencies()))
    # print(fetch_currency_details()["ETH"])
    # write_currency_details_to_csv()
    # comprehensive_withdraw_test()
    # buy_order = buy_minimum_amount("XRP")
    # print(buy_order)

    currency = "TRX"

    # print(fetch_minimums(currency))
    # buy_order = buy_minimum_amount(currency)
    # print(buy_order, end="\n\n")

    # address, tag, network = fetch_deposit_address(coinone, currency, True)

    # withdrawal = withdraw(binance, binance_master, currency, 100, address, tag, network)
    # # print(withdrawal, end="\n\n")
    # withdrawal_id = withdrawal["id"]
    # print(withdrawal_id)
    # # print(address, tag, network)
    # wait_for_coinone_deposit_completion(currency, withdrawal_id)
    # # deposit_status = wait_for_coinone_deposit_completion(currency, withdrawal_id)
    order_details = try_target_sell(currency)
    print(order_details)
    # print("Withdrawal Complete")
    # print(deposit_status)

    # print(fetch_coinone_deposit_history(currency))
    # pass
    # print(binance_master.fetch_withdrawals(code=currency, limit=1))
    # print(
    #     fetch_coinone_deposit_status(
    #         currency, "3e03e924bd4719c08c73cdb21e0ebe34ac8e84d4da39aa2768ecd3e1505c258e"
    #     )
    # )


if __name__ == "__main__":
    # print(float(set_significant_digits(0.12345678, 6)))

    # data = read_address_network_csv("address_network.csv")
    # state = State(krw_balance=0, usdt_balance=0)
    # # print(conc_find_highest_premium(1300, list(data.keys())))
    # # print(safety_check('MINA', data))
    # # cycle(state, data)
    # print(is_futures_tradable("AMP"))
    run_test()
