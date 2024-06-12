from order import *
from fetch_data import *
from logger import *
from safety import *


class State:
    def __init__(self, krw_balance, usdt_balance):
        """
        Initialize the state with balances in KRW and USDT.

        :param krw_balance: The balance in Korean Won (KRW).
        :param usdt_balance: The balance in USDT.
        """
        self.krw_balance = krw_balance
        self.usdt_balance = usdt_balance

    def fetch_balance(self):
        """
        Fetches the latest balances for KRW and USDT from Coinone and Binance respectively.
        """
        self.krw_balance = fetch_balance(coinone, "KRW")
        self.usdt_balance = fetch_balance(binance, "USDT")

    def calc_tot_balance_krw(self, fx_rate):
        """
        Calculates the total balance in KRW.

        :param fx_rate: The exchange rate from USDT to KRW.
        :return: Total balance in KRW.
        """
        return self.krw_balance + self.usdt_balance * fx_rate

    def calc_tot_balance_usdt(self, fx_rate):
        """
        Calculates the total balance in USDT.

        :param fx_rate: The exchange rate from KRW to USDT.
        :return: Total balance in USDT.
        """
        return self.krw_balance / fx_rate + self.usdt_balance


fx_rate = 1300

BUY_PERCENTAGE = 100


def determine_target(fx_rate: float, network_data):
    """
    Finds the cryptocurrency with the highest K-premium that is also depositable.

    :param fx_rate: The exchange rate from USDT to KRW.
    :return: The target currency with the highest premium that is depositable.
    """
    # Calculate premiums for all tradable pairs in Coinone.
    # Returns an array sorted in descending order by premium percentage.
    premiums = conc_find_highest_premium(fx_rate, list(network_data.keys()))

    # Iterate through the sorted premiums to find the first depositable currency
    for premium in premiums:
        if safety_check(premium[0].split("/")[0], network_data):
            return premium

    # If no depositable currency is found, return None or raise an exception
    print("No depositable currency found with a premium.")
    return None


def try_target_buy(target: str, exchange):
    """
    Places and confirms a market buy order for the target currency on Binance.

    :param target: The target currency to buy (e.g., 'BTC').
    :return: A dictionary with order details including average price, quantity, total cost, and fee if successful, None otherwise.
    """
    try:
        # Place market buy order for the target currency.
        # BUY_PERCENTAGE is the percentage of the USDT balance to use.
        order_details = buy(exchange, target, "USDT", BUY_PERCENTAGE)
        if not order_details:
            return None

        target_buy_order = order_details['order']
        target_buy_order_id = target_buy_order['id']

        # Wait until the order is fulfilled (or cancelled).
        # fulfilled_order_details = wait_for_order_fulfillment(
        #     binance, target_buy_order_id, target + "/USDT")

        # return fulfilled_order_details

        return order_details
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def try_medium_buy(medium: str):
    """
    Places and confirms a market buy order for the medium currency on Coinone.

    :param medium: The medium currency to buy (e.g., 'BTC').
    :return: A dictionary with order details including average price, quantity, total cost, and fee if successful, None otherwise.
    """
    try:
        # Place market buy order for the medium currency.
        # BUY_PERCENTAGE is the percentage of the KRW balance to use.
        order_details = buy(coinone, medium, "KRW", BUY_PERCENTAGE)
        if not order_details:
            return None

        medium_buy_order = order_details['order']
        medium_buy_order_id = medium_buy_order['id']

        # Wait until the order is fulfilled (or cancelled).
        # fulfilled_order_details = wait_for_order_fulfillment(
        #     coinone, medium_buy_order_id, medium + "/KRW")

        # return fulfilled_order_details
        return order_details
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def try_target_short(exchange, target: str, leverage: int):
    """
    Places and confirms a market short order for the target currency on Binance Futures.

    :param target: The target currency to short (e.g., 'BTC').
    :param leverage: The leverage to use for the short position.
    :return: A dictionary with order details including average price, quantity, total cost, and fee if successful, None otherwise.
    """
    try:
        # Place market short order for the target currency with 100% of the USDT balance
        order_details = short(exchange, target, 100, leverage)
        if not order_details:
            return None

        return order_details
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# def try_target_withdraw(target: str):
#     """
#     Places and confirms a withdraw request for the target currency from Binance to Coinone.

#     :param target: The target currency to withdraw (e.g., 'BTC').
#     :return: True if the withdrawal is successful, False otherwise.
#     """
#     try:
#         # Fetch withdraw address and (optionally) tag from Coinone.
#         # TODO: need to add checking sending network.
#         target_withdraw_address, target_withdraw_tag, target_withdraw_network = fetch_deposit_address(
#             coinone, target, False)

#         # Make the withdraw request.
#         target_withdrawal = withdraw(
#             binance, target, 100, target_withdraw_address, target_withdraw_tag, target_withdraw_network)

#         # Return the withdrawal status.
#         if target_withdrawal is None:
#             return False

#         target_withdrawal_id = target_withdrawal['id']

#         # Wait until the withdrawal is complete.
#         wait_for_withdrawal_completion(
#             binance, coinone, target, target_withdrawal_id)

#         return True
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return False

def try_target_withdraw(target: str):
    """
    Places and confirms a withdraw request for the target currency from Binance to Coinone.
    If the currency is not depositable on Coinone, sells the currency on Binance.

    :param target: The target currency to withdraw or sell (e.g., 'BTC').
    :return: True if the withdrawal or sell is successful, False otherwise.
    """
    try:
        # Check if the currency is depositable on Coinone
        if is_currency_depositable(target):
            # Fetch withdraw address and (optionally) tag from Coinone
            target_withdraw_address, target_withdraw_tag, network = fetch_deposit_address(
                coinone, target, is_fetch=False)

            # Make the withdraw request
            target_withdrawal = withdraw(
                binance, target, 100, target_withdraw_address, tag=target_withdraw_tag, network=network)

            # Return the withdrawal status
            if target_withdrawal is None:
                return False

            target_withdrawal_id = target_withdrawal['id']

            # Wait until the withdrawal is complete
            wait_for_withdrawal_completion(
                binance, coinone, target, target_withdrawal_id)

            return True
        else:
            # If the currency is not depositable, sell it on Binance
            sell_order_details = sell(binance, target, "USDT", 100)
            if sell_order_details is None:
                return False
            return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def try_target_sell(target: str):
    """
    Places and confirms a market sell order for the target currency on Coinone.

    :param target: The target currency to sell (e.g., 'BTC').
    :return: A dictionary with order details including average price, quantity, total cost, and fee if successful, None otherwise.
    """
    try:
        # Place market sell order for the target currency.
        order_details = sell(coinone, target, "KRW", 100)
        if not order_details:
            return None

        target_sell_order = order_details['order']
        target_sell_order_id = target_sell_order['id']

        # Wait until the order is fulfilled (or cancelled).
        # fulfilled_order_details = wait_for_order_fulfillment(
        #     coinone, target_sell_order_id, target + "/KRW")

        # return fulfilled_order_details

        return order_details
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def try_medium_sell(medium: str):
    """
    Places and confirms a market sell order for the medium currency on Binance.

    :param medium: The medium currency to sell (e.g., 'BTC').
    :return: A dictionary with order details including average price, quantity, total cost, and fee if successful, None otherwise.
    """
    try:
        # Place market sell order for the medium currency.
        order_details = sell(binance, medium, "USDT", 100)
        if not order_details:
            return None

        medium_sell_order = order_details['order']
        medium_sell_order_id = medium_sell_order['id']

        # Wait until the order is fulfilled (or cancelled).
        # fulfilled_order_details = wait_for_order_fulfillment(
        #     binance, medium_sell_order_id, medium + "/USDT")

        # return fulfilled_order_details

        return order_details
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def determine_medium():
    """
    Determines the cryptocurrency with the least transfer loss based on the current FX rate.

    :return: The currency with the least transfer loss.
    """
    # Calculate transfer losses for all possible transfer mediums.
    transfers = conc_calc_transfer_loss(fx_rate)

    # Take the currency with the least transfer loss.
    medium = transfers[0][0]

    return medium


def try_medium_withdraw(medium: str):
    """
    Places and confirms a WITHDRAW request for the medium currency from Coinone to Binance.

    :param medium: The medium currency to withdraw (e.g., 'BTC').
    :return: True if the withdrawal is successful, False otherwise.
    """
    try:
        # Fetch withdraw address and (optionally) tag from Binance.
        medium_withdraw_address, medium_withdraw_tag = fetch_deposit_address(
            binance, medium)

        # Make the withdraw request.
        medium_withdrawal = withdraw(
            coinone, medium, 100, medium_withdraw_address, medium_withdraw_tag)

        # Return the withdrawal status.
        if medium_withdrawal is None:
            return False

        medium_withdrawal_id = medium_withdrawal['id']

        # Wait until the withdrawal is complete.
        wait_for_withdrawal_completion(
            coinone, binance, medium, medium_withdrawal_id)

        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def adjust_and_hedge(target, leverage):
    """
    Adjusts the parameters by the leverage value and concurrently buys the target with 100% of the spot balance
    and places a short position with 100% of the futures balance, using the specified leverage rate.

    :param target: The target currency to trade (e.g., 'BTC').
    :param leverage: The leverage ratio to maintain and use for the short position.
    :return: A tuple containing spot buy order details and futures short order details.
    """
    # Adjust balances to maintain the specified leverage ratio
    adjust_balances_to_leverage(binance, binance_futures, leverage)

    buy_details = None
    short_details = None

    def buy_spot():
        """
        Buy the target currency with 100% of the spot balance.
        """
        nonlocal buy_details
        try:
            # Place market buy order for the target currency with 100% of the spot USDT balance
            buy_details = try_target_buy(target, binance)
            if buy_details:
                print("Spot buy order details:", buy_details)
            else:
                print("Failed to place the spot buy order.")
        except Exception as e:
            print(f"An error occurred during spot buy: {e}")

    def short_futures():
        """
        Place a short position with 100% of the futures balance, using the specified leverage rate.
        """
        nonlocal short_details
        try:
            # Place market short order for the target currency with 100% of the futures USDT balance
            short_details = try_target_short(binance_futures, target, leverage)
            if short_details:
                print("Futures short order details:", short_details)
            else:
                print("Failed to place the futures short order.")
        except Exception as e:
            print(f"An error occurred during futures short: {e}")

    # Create threads for buying and shorting
    buy_thread = threading.Thread(target=buy_spot)
    short_thread = threading.Thread(target=short_futures)

    # Start threads
    buy_thread.start()
    short_thread.start()

    # Wait for both threads to finish
    buy_thread.join()
    short_thread.join()

    print("Completed spot buy and futures short operations.")
    return buy_details, short_details


def sell_and_close(target):
    """
    Queries for the target balance in Coinone and uses two threads to concurrently sell all the target balance
    in Coinone and close 100% of the target short position in Binance Futures.

    :param target: The target currency to trade (e.g., 'BTC').
    :return: A tuple containing Coinone sell order details and Binance Futures close short order details.
    """
    sell_details = None
    close_details = None

    def sell_target_in_coinone():
        """
        Sells all the target balance in Coinone.
        """
        nonlocal sell_details
        try:
            sell_details = try_target_sell(target)
            if sell_details:
                print("Coinone sell order details:", sell_details)
            else:
                print("Failed to place the sell order in Coinone.")
        except Exception as e:
            print(f"An error occurred during Coinone sell: {e}")

    def close_short_in_binance():
        """
        Closes 100% of the target short position in Binance Futures.
        """
        nonlocal close_details
        try:
            close_details = close_short(binance_futures, target, 'USDT')
            if close_details:
                print("Binance Futures close short order details:", close_details)
            else:
                print("Failed to close the short position in Binance Futures.")
        except Exception as e:
            print(f"An error occurred during Binance Futures close short: {e}")

    # Create threads for selling and closing the short position
    sell_thread = threading.Thread(target=sell_target_in_coinone)
    close_thread = threading.Thread(target=close_short_in_binance)

    # Start threads
    sell_thread.start()
    close_thread.start()

    # Wait for both threads to finish
    sell_thread.join()
    close_thread.join()

    print("Completed Coinone sell and Binance Futures short position close operations.")
    return sell_details, close_details


def read_address_network_csv(file_path):
    """
    Reads the address_network.csv file and returns a dictionary of relevant information for each currency.

    :param file_path: The path to the address_network.csv file.
    :return: A dictionary where the keys are currencies and values are dictionaries of their corresponding details.
    """
    address_network_info = {}
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            currency = row['Currency']
            address_network_info[currency] = {
                'Market ID': row['Market ID'],
                'Deposit Address': row['Deposit Address'],
                'Tag': row['Tag'],
                'Withdraw Network': row['Withdraw Network'],
                'Deposit Network': row['Deposit Network'],
                'Unavailable': row['Unavailable'],
                'Deposit Network ID': row['Deposit Network ID']
            }
    return address_network_info


leverage = 5


def cycle(state: State, csv_file_data):
    """
    Executes a full trading cycle including buying, withdrawing, and selling target and medium currencies.

    :param state: The current state of balances in KRW and USDT.
    :return: A dictionary with the order details for target buy, target sell, medium buy, and medium sell.
    """
    if fx_rate is None:
        return None

    # Determine the target currency with the highest premium.
    target_data = determine_target(fx_rate, csv_file_data)
    target = target_data[0]

    print(target_data)
    return

    # Try to buy, withdraw, and sell the target currency.
    # target_buy_details = try_target_buy(target, binance)

    # Hedge the position
    target_buy_details, target_hedge_details = adjust_and_hedge(
        target, leverage)
    target_withdraw_success = try_target_withdraw(target)
    # target_sell_details = try_target_sell(target)
    # Sell and close positions
    target_sell_details, target_close_details = sell_and_close(target)

    # Determine the medium currency with the least transfer loss.
    medium = determine_medium()

    # TODO: Maybe change to using just USDT or USDC?

    # Try to buy, withdraw, and sell the medium currency.
    medium_buy_details = try_medium_buy(medium)
    medium_withdraw_success = try_medium_withdraw(medium)
    medium_sell_details = try_medium_sell(medium)

    return {
        'target_buy': target_buy_details,
        'target_hedge': target_hedge_details,
        'target_sell': target_sell_details,
        'target_close': target_close_details,
        'medium_buy': medium_buy_details,
        'medium_sell': medium_sell_details
    }


def go():
    fx_rate_thread = threading.Thread(target=update_fx_rate)
    fx_rate_thread.daemon = True
    fx_rate_thread.start()

    state = State(krw_balance=0, usdt_balance=0)

    with read_address_network_csv("address_network.csv") as csv_file_data:

        while True:
            state.fetch_balance()
            order_details = cycle(state, csv_file_data)
            if order_details:
                log_order_details_to_csv(order_details)
            # Add a sleep interval to control the frequency of cycles
            time.sleep(1)


if __name__ == "__main__":
    # print(fetch_deposit_address(coinone, "BTC", False))
    # print(is_currency_depositable("ABL"))
    print(determine_target(1300))
