import csv
from fetch_data import *


def fetch_deposit_address(exchange, target):
    """
    Fetches the deposit address and any associated tag or memo for a given currency from the specified exchange.

    :param exchange: The exchange object (e.g., ccxt.binance()).
    :param target: The target currency to fetch the deposit address for (e.g., 'XLM').
    :return: A tuple containing the address and tag (or memo), or None if an error occurs.
    """
    try:
        # Fetch the deposit address and any associated tag or memo
        deposit_info = exchange.fetch_deposit_address(target)

        # Extract the address, tag, and memo
        address = deposit_info.get('address', None)
        tag = deposit_info.get('tag', None)  # Also known as memo
        memo = deposit_info.get('memo', None)

        # Return a tuple containing the address, tag, and memo
        return address, tag
    except ccxt.BaseError as e:
        print(f"An error occurred: {e}")
        return None, None


def fetch_all_tradable_pairs(exchange):
    """
    Fetches all tradable pairs from the given exchange.

    :param exchange: The exchange instance (e.g., ccxt.coinone()).
    :return: A list of tradable pairs.
    """
    markets = exchange.load_markets()
    tradable_pairs = [
        symbol for symbol in markets]
    # print(tradable_pairs)
    return tradable_pairs


def check_usdt_pair_tradable(exchange, currency):
    """
    Checks if the /USDT pair for the given currency is tradable on the exchange.

    :param exchange: The exchange instance (e.g., ccxt.binance()).
    :param currency: The currency to check (e.g., 'BTC').
    :return: Tuple containing a boolean indicating if the pair is tradable and the market ID if tradable.
    """
    symbol = currency + "/USDT"
    markets = exchange.load_markets()
    if symbol in markets and markets[symbol]['active']:
        return True, markets[symbol]['id']
    return False, None


def create_matching_currencies_csv(spot_exchange, futures_exchange, filename='address.csv'):
    """
    Creates a CSV file listing the currencies that have tradable /USDT pairs on both spot and futures exchanges.

    :param spot_exchange: The spot exchange instance (e.g., ccxt.binance()).
    :param futures_exchange: The futures exchange instance (e.g., ccxt.binance_futures()).
    :param filename: The name of the CSV file to create.
    """
    # Fetch all tradable pairs from Coinone
    coinone_pairs = fetch_all_tradable_pairs(spot_exchange)

    # Extract unique currencies from Coinone pairs
    coinone_currencies = set(pair.split('/')[0] for pair in coinone_pairs)

    # Prepare CSV file
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Currency', 'Market ID', 'Deposit Address', 'Tag'])

        # Check each currency for tradable /USDT pairs on both spot and futures exchanges
        for currency in coinone_currencies:
            spot_tradable, _ = check_usdt_pair_tradable(
                binance, currency)
            futures_tradable, market_id = check_usdt_pair_tradable(
                futures_exchange, currency)

            if spot_tradable and futures_tradable:
                # Fetch deposit address and tag
                address, tag = fetch_deposit_address(spot_exchange, currency)
                # Fetch supported networks
                supported_networks = fetch_supported_networks(
                    binance, currency)
                networks_str = ', '.join(supported_networks)

                writer.writerow(
                    [currency, market_id, address, tag, networks_str])
                print(
                    f"Currency {currency} is tradable on both spot and futures markets.")


if __name__ == '__main__':
    create_matching_currencies_csv(coinone, binance_futures_test)
    pass
