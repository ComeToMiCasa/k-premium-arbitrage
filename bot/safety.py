import ccxt
import concurrent.futures
import requests
from exchanges import *


def is_futures_tradable(target_currency):
    """
    Checks if the target currency's /USDT pair is tradable on both Binance Spot and Futures markets.

    :param binance_spot: The exchange instance (e.g., ccxt.binance()) configured for spot trading.
    :param binance_futures: The exchange instance (e.g., ccxt.binance()) configured for futures trading.
    :param target_currency: The target currency to check (e.g., 'BTC').
    :return: A tuple with boolean indicating if tradable and the market ID if tradable.
    """
    pair = target_currency + "/USDT"
    try:
        # Load spot markets
        spot_markets = binance.load_markets()
        # Load futures markets
        futures_markets = binance_futures.load_markets()

        print(futures_markets[pair]["future"])

        # Check if the pair is tradable on both spot and futures markets
        is_spot_tradable = (
            pair in spot_markets
            and spot_markets[pair]["active"]
            and spot_markets[pair]["spot"]
        )
        is_futures_tradable = (
            pair in futures_markets and futures_markets[pair]["future"]
        )
        market_id = futures_markets[pair]["id"] if is_futures_tradable else None

        return is_spot_tradable and is_futures_tradable, market_id
    except Exception as e:
        print(f"An error occurred: {e}")
        return False, None


def is_currency_depositable(currencies_info, currency):
    """
    Checks if a given currency is depositable based on provided currency information.

    :param currencies_info: A dictionary containing currency information.
    :param currency: The currency to check (e.g., 'BTC').
    :return: True if the currency is depositable, False otherwise.
    """
    if currency in currencies_info:
        return currencies_info[currency]["deposit"]
    else:
        print(f"Currency {currency} is not available in the provided information.")
        return False


def is_trade_suspended_coinone(exchange, currency):
    """
    Checks if the trade for a given currency is suspended on Coinone.

    :param exchange: The ccxt exchange instance for Coinone.
    :param currency: The currency to check (e.g., 'BTC').
    :return: True if trade is suspended, False otherwise.
    """
    try:
        markets = exchange.fetch_markets()
        for market in markets:
            if market["symbol"] == currency + "/KRW" and market["active"] is False:
                return True
        return False
    except ccxt.BaseError as e:
        print(f"An error occurred: {e}")
        return False


def is_withdrawal_suspended_binance(exchange, currency):
    """
    Checks if the withdrawal for a given currency is suspended on Binance.

    :param exchange: The ccxt exchange instance for Binance.
    :param currency: The currency to check (e.g., 'BTC').
    :return: True if withdrawal is suspended, False otherwise.
    """
    try:
        currencies_info = exchange.fetch_currencies()
        if currency in currencies_info:
            return not currencies_info[currency]["withdraw"]
        else:
            print(f"Currency {currency} is not available on this exchange.")
            return True
    except ccxt.BaseError as e:
        print(f"An error occurred: {e}")
        return True


def safety_check(target, network_data):
    """
    Checks if the target trade, withdrawal, and deposit are not suspended.

    :param target: The target currency to check (e.g., 'BTC').
    :return: True if all checks pass, False otherwise.
    """

    if network_data[target]["Unavailable"] == "*":
        print(f"Deposit for {target} is suspicious")
        return False

    if not network_data[target]["Deposit Address"]:
        print(f"Deposit address for {target} unspecified")
        return False

    # Assuming coinone and binance are already initialized ccxt exchange instances
    if is_trade_suspended_coinone(coinone, target):
        print(f"Trade for {target} is suspended on Coinone.")
        return False

    if is_withdrawal_suspended_binance(binance_master, target):
        print(f"Withdrawal for {target} is suspended on Binance.")
        return False

    if not is_currency_depositable(coinone, target):
        print(f"Deposit for {target} is suspended on Coinone.")
        return False

    return True


def comprehensive_currency_check(
    currency,
    coinone_markets,
    binance_spot_markets,
    binance_futures_markets,
    binance_currencies,
    coinone_currencies,
):
    """
    Checks if a currency is tradable on Coinone, Binance Spot, Binance Futures,
    withdrawable on Binance, and depositable on Coinone using pre-fetched market and currency data.

    :param coinone: The ccxt exchange instance for Coinone.
    :param binance_spot: The ccxt exchange instance for Binance configured for spot trading.
    :param binance_futures: The ccxt exchange instance for Binance configured for futures trading.
    :param currency: The currency to check (e.g., 'BTC').
    :param coinone_markets: Pre-fetched markets data for Coinone.
    :param binance_spot_markets: Pre-fetched markets data for Binance Spot.
    :param binance_futures_markets: Pre-fetched markets data for Binance Futures.
    :param binance_currencies: Pre-fetched currencies data for Binance.
    :param coinone_currencies: Pre-fetched currencies data for Coinone.
    :return: True if all conditions are met, False otherwise.
    """
    try:
        # Check if currency is tradable on Coinone
        coinone_tradable = (
            currency + "/KRW" in coinone_markets
            and coinone_markets[currency + "/KRW"]["spot"]
        )

        # Check if currency is tradable on Binance Spot
        binance_spot_tradable = (
            currency + "/USDT" in binance_spot_markets
            and binance_spot_markets[currency + "/USDT"]["active"]
            and binance_spot_markets[currency + "/USDT"]["spot"]
        )

        # Check if currency is tradable on Binance Futures
        binance_futures_tradable = (
            currency + "/USDT:USDT"
            in binance_futures_markets
            # and binance_futures_markets[currency + "/USDT:USDT"]["future"]
        )

        # Check if currency is withdrawable on Binance
        binance_withdrawable = (
            currency in binance_currencies and binance_currencies[currency]["withdraw"]
        )

        # Check if currency is depositable on Coinone
        coinone_depositable = (
            currency in coinone_currencies and coinone_currencies[currency]["deposit"]
        )

        if not coinone_tradable:
            print(f"{currency} is not tradable on Coinone.")
        if not binance_spot_tradable:
            print(f"{currency} is not tradable on Binance Spot.")
        if not binance_futures_tradable:
            print(f"{currency} is not tradable on Binance Futures.")
        if not binance_withdrawable:
            print(f"{currency} is not withdrawable on Binance.")
        if not coinone_depositable:
            print(f"{currency} is not depositable on Coinone.")

        # Return True if all conditions are met
        return all(
            [
                coinone_tradable,
                binance_spot_tradable,
                binance_futures_tradable,
                binance_withdrawable,
                coinone_depositable,
            ]
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
