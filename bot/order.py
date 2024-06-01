import time
from fetch_data import *
from balance import *


def buy(exchange, target, quote, percentage):
    """
    Buy cryptocurrency using a specified percentage of the quote currency balance at market price.

    :param exchange: The exchange object (e.g., ccxt.binance()).
    :param target: The target currency to trade (e.g., 'BTC').
    :param quote: The quote currency to trade against (e.g., 'USDT').
    :param percentage: The percentage of the quote currency balance to use.
    :return: A dictionary with order details including average price, quantity, total cost, and fee if successful, None otherwise.
    """
    try:
        # Fetch the current balance of the quote currency
        balance = fetch_balance(exchange, quote)

        # Calculate the cost based on the specified percentage of the balance
        cost = balance * percentage / 100

        # Construct the trading pair symbol
        symbol = target + "/" + quote

        # Load markets to ensure the symbol is available
        markets = exchange.load_markets()

        # Check if the symbol is available
        if symbol not in markets:
            print(f"Error: Symbol {symbol} is not available on the exchange.")
            return None

        # Create a market buy order with the calculated cost
        order = exchange.create_market_buy_order_with_cost(symbol, cost)
        print(f"Market buy order created: {order['id']}")

        # Extract order details
        # average_price = order.get('average', None)
        # quantity = order.get('filled', None)
        # total_cost = order.get('cost', None)
        # fee = order.get('fee', {}).get('cost', None)

        average_price = order['average']
        quantity = order['filled']
        total_cost = order['cost']
        fee = order['fees']

        return {
            'order': order,
            'average_price': average_price,
            'quantity': quantity,
            'total_cost': total_cost,
            'fee': fee
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def sell(exchange, target, quote, percentage):
    """
    Sell cryptocurrency at market price.

    :param exchange: The exchange object (e.g., ccxt.coinone()).
    :param target: The target currency to sell (e.g., 'BTC').
    :param quote: The quote currency to receive (e.g., 'KRW').
    :param percentage: The percentage of the target currency balance to sell.
    :return: A dictionary with order details including average price, quantity, total cost, and fee if successful, None otherwise.
    """
    try:
        # Fetch the current balance of the target currency
        balance = fetch_balance(exchange, target)

        # Calculate the amount to sell based on the specified percentage of the balance
        amount = balance * percentage / 100

        # Construct the trading pair symbol
        symbol = target + "/" + quote

        # Load markets to ensure the symbol is available
        markets = exchange.load_markets()

        # Check if the symbol is available
        if symbol not in markets:
            print(f"Error: Symbol {symbol} is not available on the exchange.")
            return None

        # Create a market sell order
        order = exchange.create_market_sell_order_with_cost(symbol, amount)
        print(f"Market sell order created: {order}")

        # Extract order details
        average_price = order.get('average', None)
        quantity = order.get('filled', None)
        total_cost = order.get('cost', None)
        fee = order.get('fee', {}).get('cost', None)

        return {
            'order': order,
            'average_price': average_price,
            'quantity': quantity,
            'total_cost': total_cost,
            'fee': fee
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def short(exchange, target, percentage, leverage):
    """
    Place a market short order with the cost as a percentage of the current USDT balance.

    :param exchange: The exchange instance (e.g., ccxt.binance()).
    :param target: The target currency to short (e.g., 'BTC').
    :param percentage: The percentage of the USDT balance to use.
    :param leverage: The leverage rate to use.
    :return: A dictionary with order details if successful, None otherwise.
    """
    try:
        # Fetch the current USDT balance
        usdt_balance = fetch_balance(exchange, 'USDT')
        if usdt_balance is None:
            return None

        # Calculate the cost based on the specified percentage of the USDT balance
        cost = usdt_balance * percentage / 100

        # Construct the trading pair symbol
        symbol = target + "/USDT"

        # Load markets to ensure the symbol is available
        markets = exchange.load_markets()
        if symbol not in markets:
            print(
                f"Error: Symbol {symbol} is not available on the exchange.")
            return None

        # Set leverage for the target symbol
        exchange.fapiPrivate_post_leverage({
            'symbol': markets[symbol]['id'],
            'leverage': leverage
        })

        # Create a market sell order with the calculated cost
        order = exchange.create_market_sell_order_with_cost(
            symbol, cost)
        print(f"Market short order created: {order['id']}")

        return {
            'order': order,
            'average_price': order['average'],
            'quantity': order['filled'],
            'total_cost': order['cost'],
            'fee': order['fees']
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def fetch_order_status(exchange, order_id, symbol):
    """
    Fetch the status of a specific order.

    :param exchange: The exchange object (e.g., ccxt.binance()).
    :param order_id: The ID of the order to check.
    :param symbol: The trading pair symbol (e.g., 'BTC/USDT').
    :return: The order details if available, None otherwise.
    """
    try:
        order = exchange.fetch_order(order_id, symbol)
        return order
    except Exception as e:
        print(f"An error occurred while checking the order status: {e}")
        return None


def wait_for_order_fulfillment(exchange, order_id, symbol, polling_interval=0.1):
    """
    Waits for an order to be fulfilled or canceled by periodically checking its status.

    :param exchange: The exchange object (e.g., ccxt.binance()).
    :param order_id: The ID of the order to check.
    :param symbol: The trading pair symbol (e.g., 'BTC/USDT').
    :param polling_interval: The interval (in seconds) between status checks.
    :return: A dictionary with order details including average price, quantity, total cost, and fee if fulfilled, None otherwise.
    """
    while True:
        order_status = fetch_order_status(exchange, order_id, symbol)
        if order_status:
            status = order_status['status']
            print(f"Current order status: {status}")
            if status == 'closed':
                print("The order has been fully fulfilled.")
                return {
                    'average_price': order_status.get('average', None),
                    'quantity': order_status.get('filled', None),
                    'total_cost': order_status.get('cost', None),
                    'fee': order_status.get('fee', {}).get('cost', None)
                }
            elif status == 'canceled':
                print("The order has been canceled.")
                return None
        else:
            print("Failed to retrieve order status.")

        time.sleep(polling_interval)


def close_short(exchange, target, quote):
    """
    Closes a short position by buying back the same amount of the target currency.

    :param exchange: The exchange instance (e.g., ccxt.binance()) configured for futures trading.
    :param target: The target currency to cover (e.g., 'BTC').
    :param quote: The quote currency to trade against (e.g., 'USDT').
    :return: A dictionary with order details if successful, None otherwise.
    """
    try:
        # Fetch the current position size
        positions = exchange.fapiPrivate_get_positionrisk()
        symbol = target + "/" + quote
        position = next(
            (pos for pos in positions if pos['symbol'] == exchange.markets[symbol]['id']), None)

        if not position:
            print(f"No position found for {symbol}")
            return None

        # Calculate the amount to buy back (cover the short position)
        amount_to_buy = float(position['positionAmt'])

        if amount_to_buy <= 0:
            print(f"No short position to close for {symbol}")
            return None

        # Place a market buy order to cover the short position
        order = exchange.create_market_buy_order(symbol, abs(amount_to_buy))
        print(
            f"Market buy order created to close short position: {order['id']}")

        return {
            'order': order,
            'average_price': order['average'],
            'quantity': order['filled'],
            'total_cost': order['cost'],
            'fee': order['fees']
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
