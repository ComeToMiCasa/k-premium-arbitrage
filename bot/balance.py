import time


def fetch_balance(exchange, currency):
    """
    Check the balance of a specified currency on the given exchange.

    :param exchange: The ccxt exchange instance.
    :param currency: The currency to check balance for (e.g., 'BTC', 'KRW').
    :return: The balance of the specified currency.
    """
    try:
        # Load the balances from the exchange
        balance = exchange.fetch_balance()

        # Check if the specified currency is in the balance
        if currency in balance['total']:
            return balance['total'][currency]
        else:
            print(
                f"Error: Currency {currency} is not available in the balance.")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def fetch_all_balances(exchange):
    """
    Fetches all available balances for the currencies owned on the specified exchange.

    :param exchange: The exchange instance (e.g., ccxt.binance()).
    :return: A dictionary with currencies and their respective balances.
    """
    try:
        # Fetch all balances
        balance = exchange.fetch_balance()

        # Filter out only the non-zero balances
        non_zero_balances = {currency: balance['total'][currency]
                             for currency in balance['total'] if balance['total'][currency] > 0}

        return non_zero_balances
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


def transfer_usdt(exchange, from_account, to_account, amount):
    """
    Transfers USDT between Binance Spot and Futures accounts.

    :param exchange: The exchange instance (e.g., ccxt.binance()).
    :param from_account: The account to transfer from ('spot' or 'future').
    :param to_account: The account to transfer to ('spot' or 'future').
    :param amount: The amount to transfer.
    """
    if from_account == 'spot' and to_account == 'future':
        exchange.sapi_post_futures_transfer({
            'asset': 'USDT',
            'amount': amount,
            'type': 1  # 1: transfer from spot to futures
        })
    elif from_account == 'future' and to_account == 'spot':
        exchange.sapi_post_futures_transfer({
            'asset': 'USDT',
            'amount': amount,
            'type': 2  # 2: transfer from futures to spot
        })


def adjust_balances_to_leverage(spot_exchange, futures_exchange, leverage):
    """
    Adjusts the USDT balances between Binance Spot and Futures accounts
    so that the spot balance is `leverage` times the futures balance.

    :param spot_exchange: The exchange instance for spot trading (e.g., ccxt.binance()).
    :param futures_exchange: The exchange instance for futures trading (e.g., ccxt.binance()).
    :param leverage: The leverage ratio to maintain.
    """
    spot_balance = fetch_balance(spot_exchange, 'USDT')
    futures_balance = fetch_balance(futures_exchange, 'USDT')

    required_futures_balance = spot_balance / leverage

    if required_futures_balance > futures_balance:
        transfer_amount = required_futures_balance - futures_balance
        transfer_usdt(spot_exchange, 'spot', 'future', transfer_amount)
        print(f"Transferred {transfer_amount} USDT from Spot to Futures.")
    elif required_futures_balance < futures_balance:
        transfer_amount = futures_balance - required_futures_balance
        transfer_usdt(spot_exchange, 'future', 'spot', transfer_amount)
        print(f"Transferred {transfer_amount} USDT from Futures to Spot.")
    else:
        print("No transfer needed. Balances are already in the desired ratio.")


def withdraw(exchange, currency, percentage, address, tag=None):
    """
    Withdraws a specified percentage of a currency to a given address.

    :param exchange: The ccxt exchange instance.
    :param currency: The currency to withdraw (e.g., 'BTC').
    :param percentage: The percentage of the balance to withdraw.
    :param address: The address to withdraw to.
    :param tag: An optional tag or memo for the withdrawal.
    :return: The withdrawal details if successful, None otherwise.
    """
    try:
        # Fetch the balance
        balance = fetch_balance(exchange, currency)
        print(f"Balance: {balance} {currency}")

        # Calculate the amount to withdraw based on the specified percentage of the balance
        amount = balance * percentage / 100

        # Withdraw funds
        if tag:
            withdrawal = exchange.withdraw(currency, amount, address, tag)
        else:
            withdrawal = exchange.withdraw(currency, amount, address)

        print(f"Withdrawal request successful: {withdrawal}")
        return withdrawal
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def fetch_withdrawal_status(exchange, currency, withdrawal_id):
    """
    Fetch the status of a specific withdrawal.

    :param exchange: The ccxt exchange instance.
    :param currency: The currency of the withdrawal (e.g., 'BTC').
    :param withdrawal_id: The ID of the withdrawal to check.
    :return: The withdrawal details if available, None otherwise.
    """
    try:
        withdrawals = exchange.fetch_withdrawals(currency)
        for withdrawal in withdrawals:
            if withdrawal['id'] == withdrawal_id:
                return withdrawal
        print("Withdrawal not found.")
        return None
    except Exception as e:
        print(f"An error occurred while checking the withdrawal status: {e}")
        return None


def fetch_deposit_status(exchange, currency, txid):
    """
    Fetch the status of a specific deposit.

    :param exchange: The ccxt exchange instance.
    :param currency: The currency of the deposit (e.g., 'BTC').
    :param txid: The transaction ID of the deposit to check.
    :return: The deposit details if available, None otherwise.
    """
    try:
        deposits = exchange.fetch_deposits(currency)
        for deposit in deposits:
            if deposit['txid'] == txid:
                return deposit
        print("Deposit not found.")
        return None
    except Exception as e:
        print(f"An error occurred while checking the deposit status: {e}")
        return None


def wait_for_withdrawal_completion(from_exchange, to_exchange, currency, withdrawal_id, polling_interval=10):
    """
    Waits for a withdrawal to be completed on one exchange and the corresponding deposit to be credited on another exchange.

    :param from_exchange: The exchange from which the withdrawal is made.
    :param to_exchange: The exchange to which the deposit is made.
    :param currency: The currency of the withdrawal and deposit (e.g., 'BTC').
    :param withdrawal_id: The ID of the withdrawal to check.
    :param polling_interval: The interval (in seconds) between status checks.
    """
    while True:
        # Check withdrawal status on the source exchange
        withdrawal_status = fetch_withdrawal_status(
            from_exchange, currency, withdrawal_id)
        if withdrawal_status:
            status = withdrawal_status['status']
            print(f"Current withdrawal status: {status}")
            if status in ['ok', 'completed']:
                print("The withdrawal has been completed.")
                txid = withdrawal_status['txid']

                # Check deposit status on the destination exchange
                while True:
                    deposit_status = fetch_deposit_status(
                        to_exchange, currency, txid)
                    if deposit_status:
                        deposit_status_str = deposit_status['status']
                        print(f"Current deposit status: {deposit_status_str}")
                        if deposit_status_str == 'ok':
                            print("The deposit has been credited to your account.")
                            return
                    else:
                        print("Failed to retrieve deposit status.")

                    time.sleep(polling_interval)

                break
            elif status == 'canceled':
                print("The withdrawal has been canceled.")
                break
        else:
            print("Failed to retrieve withdrawal status.")

        time.sleep(polling_interval)
