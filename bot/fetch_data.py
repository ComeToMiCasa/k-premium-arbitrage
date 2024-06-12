import ccxt
from dotenv import load_dotenv
import os
import requests
import concurrent.futures
import time
import json
import threading
from address import get_address_from_csv
from decimal import Decimal

from symbols import coinone_tradeable_symbols
from exchanges import *

# Load environment variables from .env file
load_dotenv()


def fetch_exchange_price(exchange, symbol: str):
    """
    Fetch the latest price for a given symbol from the specified exchange.

    :param exchange: The exchange instance (e.g., ccxt.binance()).
    :param symbol: The trading pair symbol (e.g., 'BTC/USDT').
    :return: The last price of the symbol from the specified exchange.
    """
    return exchange.fetch_ticker(symbol)['last']


def fetch_fx_rate():
    """
    Fetch the current USD to KRW exchange rate using the Alpha Vantage API.

    :return: The current exchange rate from USD to KRW, or None if the rate could not be retrieved.
    """
    # Base URL for the Alpha Vantage API
    BASE_URL = 'https://www.alphavantage.co/query'

    # Parameters for the API call
    params = {
        'function': 'CURRENCY_EXCHANGE_RATE',
        'from_currency': 'USD',
        'to_currency': 'KRW',
        'apikey': alphavantage_api_key
    }

    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        try:
            exchange_rate = data['Realtime Currency Exchange Rate']['5. Exchange Rate']
            return float(exchange_rate)
        except KeyError:
            print("Error: Could not retrieve exchange rate from the response.")
            return None
    else:
        print(
            f"Error: API request failed with status code {response.status_code}.")
        return None


def calc_price_diff(target: str = 'BTC', ex_a=None, ex_b=None, fx_rate: float = 1200):
    """
    Calculate the price difference and percentage difference between two exchanges for a given target currency.

    :param target: The target currency (e.g., 'BTC').
    :param ex_a: The first exchange instance (e.g., ccxt.coinone()).
    :param ex_b: The second exchange instance (e.g., ccxt.binance()).
    :param fx_rate: The exchange rate from USDT to KRW.
    :return: A tuple containing the price difference, percentage difference, and prices from both exchanges.
    """
    ex_a_price_krw = fetch_exchange_price(ex_a, target + "/KRW")
    ex_b_price = fetch_exchange_price(ex_b, target + "/USDT")

    # print(ex_a_price_krw, ex_b_price, fx_rate)

    ex_a_price = ex_a_price_krw / fx_rate

    price_diff = ex_a_price - ex_b_price
    price_diff_percent = price_diff / ex_b_price * 100

    return price_diff, price_diff_percent, ex_a_price_krw, ex_a_price, ex_b_price, fx_rate


def conc_calc_transfer_loss(fx_rate: float):
    """
    Concurrently calculate transfer loss for all specified transfer mediums.

    :param fx_rate: The exchange rate from USDT to KRW.
    :return: A sorted list of transfer mediums and their respective price differences and percentage differences.
    """
    def fetch_and_calc(medium):
        try:
            price_diff, price_diff_percent, _, _, _, _ = calc_price_diff(
                medium, coinone, binance, fx_rate)
            return (medium, price_diff, price_diff_percent)
        except Exception as e:
            print(e)

    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(
            fetch_and_calc, medium): medium for medium in transfer_mediums}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)

    results.sort(key=lambda x: x[2])
    return results


def conc_find_highest_premium(fx_rate: float, currencies, ex=coinone):
    """
    Concurrently find the cryptocurrency with the highest premium on Coinone compared to Binance.

    :param fx_rate: The exchange rate from USDT to KRW.
    :param ex: The exchange instance to compare (default is ccxt.coinone()).
    :return: A sorted list of trading pairs with their premiums in descending order.
    """
    def calc_premium_for_symbol(symbol, ex, fx_rate):
        target = symbol.split('/')[0]
        # print("Calculating " + target + "...")

        try:
            price_diff, price_diff_percent, _, _, _, _ = calc_price_diff(
                target, ex, binance, fx_rate)
            premium = (symbol, price_diff, price_diff_percent)
            return premium
        except Exception as e:
            print(e)
            return None

    premiums = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(
            calc_premium_for_symbol, symbol, ex, fx_rate): symbol for symbol in currencies}
        for future in concurrent.futures.as_completed(futures):
            symbol = futures[future]
            try:
                premium = future.result()
                if premium:
                    premiums.append(premium)
            except Exception as e:
                print(f"Error processing {symbol}: {e}")

    return sorted(premiums, key=lambda x: x[2], reverse=True)


def fetch_supported_networks(exchange, currency):
    """
    Fetches the supported networks for a given currency from the specified exchange.

    :param exchange: The exchange object (e.g., ccxt.binance()).
    :param currency: The currency to check (e.g., 'USDT').
    :return: A list of supported networks for the specified currency.
    """
    try:
        # Fetch detailed information about all currencies
        currencies_info = exchange.fetch_currencies()

        # Check if the specified currency is available
        if currency in currencies_info:
            currency_info = currencies_info[currency]
            # print(currency_info)

            # Extract and return the available networks
            networks = currency_info.get('networks', {})
            return list(networks.keys())
        else:
            print(f"Currency {currency} is not available on this exchange.")
            return []
    except ccxt.BaseError as e:
        print(f"An error occurred: {e}")
        return []


def fetch_available_networks(exchange, currency):
    """
    Extracts available networks for a given currency from the exchange.

    :param exchange: The ccxt exchange instance.
    :param currency: The currency to fetch network information for (e.g., 'TRX').
    :return: A list of tuples containing the network dictionary key and the network name.
    """
    try:
        # Fetch currency information
        currencies = exchange.fetch_currencies()
        if currency in currencies and 'networks' in currencies[currency]:
            networks = [(key, net_info['info']['network'])
                        for key, net_info in currencies[currency]['networks'].items()]
            return networks
        else:
            print(
                f"Currency {currency} not found or no network information available.")
            return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def is_currency_depositable(currency):
    """
    Checks if a given currency is depositable on Coinone.

    :param currency: The currency to check (e.g., 'BTC').
    :return: True if the currency is depositable, False otherwise.
    """
    try:
        # API endpoint for Coinone currency info
        url = f'https://api.coinone.co.kr/public/v2/currencies/{currency}'

        # Make the request
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            # Check the deposit status for the currency
            deposit_status = data['currencies'][0]['deposit_status']
            return deposit_status != 'suspended'
        else:
            print(
                f"Failed to fetch data for {currency}. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def fetch_deposit_address(exchange, target, is_fetch=True):
    """
    Fetches the deposit address and any associated tag or memo for a given currency from the specified exchange or CSV file.

    :param exchange: The exchange object (e.g., ccxt.binance()).
    :param target: The target currency to fetch the deposit address for (e.g., 'XLM').
    :param is_fetch: Boolean flag to decide whether to fetch from exchange (True) or CSV file (False).
    :return: A tuple containing the address, tag, and network, or None if an error occurs.
    """
    if is_fetch:
        try:
            # Fetch the deposit address and any associated tag or memo from the exchange
            deposit_info = exchange.fetch_deposit_address(target)

            # Extract the address, tag, and memo
            address = deposit_info.get('address', None)
            tag = deposit_info.get('tag', None)  # Also known as memo
            memo = deposit_info.get('memo', None)

            # Return a tuple containing the address, tag, and memo
            return address, tag, memo
        except ccxt.BaseError as e:
            print(f"An error occurred: {e}")
            return None, None, None
    else:
        # Fetch the address and tag from the CSV file
        return get_address_from_csv('address.csv', target)


def check_coinone_deposit_suspended(currency):
    """
    Checks if the deposit for a given currency is suspended on Coinone.

    :param currency: The currency to check (e.g., 'CHZ').
    :return: True if the deposit is suspended, False otherwise.
    """
    try:
        # Construct the URL
        url = f'https://api.coinone.co.kr/public/v2/currencies/{currency}'

        # Make the custom request
        response = coinone.fetch(url)

        # Debug: Print the response to understand its structure
        # print(response['currencies'][0])

        # Check if the deposit status is suspended
        if response['currencies'][0]['deposit_status'] == 'suspended':
            return True
        else:
            return False

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_withdraw_integer_multiple(exchange, currency, network):
    currencies = exchange.fetch_currencies()
    if currency in currencies:
        for net in currencies[currency]['info']['networkList']:
            if net['network'] == network:
                return Decimal(net['withdrawIntegerMultiple'])
    return None


fx_rate = None


def update_fx_rate():
    """
    Periodically updates the FX rate by fetching the latest rate every 10 minutes.
    """
    global fx_rate

    while True:
        fx_rate = fetch_fx_rate()
        time.sleep(600)  # Sleep for 10 minutes before updating again


def cycle():
    """
    Executes a cycle of finding the highest premium and printing the results if FX rate is available.
    """
    if fx_rate:
        premiums = conc_find_highest_premium(fx_rate)
    else:
        return

    print(premiums)


def go():
    """
    Starts the FX rate update thread and continuously executes the cycle function.
    """
    # Start the FX rate update thread
    fx_rate_thread = threading.Thread(target=update_fx_rate)
    fx_rate_thread.daemon = True
    fx_rate_thread.start()

    # Continuously execute the cycle function
    while True:
        cycle()


if __name__ == "__main__":
    # Run the main function
    # binance.create_market_sell_order_with_cost
    # go()
    # print(fetch_deposit_address(coinone, "XLM"))
    fx_rate = fetch_fx_rate()
    # print(fx_rate)
    # print(conc_calc_transfer_loss(fx_rate))
    print(conc_find_highest_premium(fx_rate))
    # print(calc_price_diff("XRP"))
    pass
    # print(fetch_deposit_address(coinone, 'IQ'))
    # print(check_coinone_deposit_suspended("CHZ"))
    # fetch_supported_networks(binance, 'IQ')

    # find_highest_premium(fx_rate)

    # print("Synchronous run Start")

    # start_time = time.time()
    # # print(fetch_upbit_price() / fx_rate)
    # for i in range(10):
    #     print("run " + str(i+1))
    #     find_highest_premium(fx_rate)
    # end_time = time.time()

    # time_1 = (end_time - start_time) / 10

    # print("Concurrent run Start")

    # start_time = time.time()
    # # print(fetch_upbit_price() / fx_rate)
    # for i in range(10):
    #     print("run " + str(i+1))
    #     conc_find_highest_premium(fx_rate)
    # end_time = time.time()

    # time_2 = (end_time - start_time) / 10
    # print(time_1, time_2)
