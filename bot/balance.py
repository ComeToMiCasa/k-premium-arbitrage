import base64
import hashlib
import hmac
import time
from decimal import Decimal, ROUND_DOWN
import uuid
import math

from fetch_data import *
from coinone_api import *
from binance_api import *


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
        if currency in balance["total"]:
            return balance["total"][currency]
        else:
            print(f"Error: Currency {currency} is not available in the balance.")
            return None
    except Exception as e:
        print(f"An error occurred in fetch_balance: {e}")
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
        non_zero_balances = {
            currency: balance["total"][currency]
            for currency in balance["total"]
            if balance["total"][currency] > 0
        }

        return non_zero_balances
    except Exception as e:
        print(f"An error occurred in fetch_all_balances: {e}")
        return {}


def transfer_usdt(exchange, from_account, to_account, amount):
    """
    Transfers USDT between Binance Spot and Futures accounts.

    :param exchange: The exchange instance (e.g., ccxt.binance()).
    :param from_account: The account to transfer from ('spot' or 'future').
    :param to_account: The account to transfer to ('spot' or 'future').
    :param amount: The amount to transfer.
    """
    if from_account == "spot" and to_account == "future":
        exchange.sapi_post_futures_transfer(
            {
                "asset": "USDT",
                "amount": amount,
                "type": 1,  # 1: transfer from spot to futures
            }
        )
    elif from_account == "future" and to_account == "spot":
        exchange.sapi_post_futures_transfer(
            {
                "asset": "USDT",
                "amount": amount,
                "type": 2,  # 2: transfer from futures to spot
            }
        )


def adjust_balances_to_leverage(spot_exchange, futures_exchange, leverage):
    """
    Adjusts the USDT balances between Binance Spot and Futures accounts
    so that the spot balance is `leverage` times the futures balance.

    :param spot_exchange: The exchange instance for spot trading (e.g., ccxt.binance()).
    :param futures_exchange: The exchange instance for futures trading (e.g., ccxt.binance()).
    :param leverage: The leverage ratio to maintain.
    """
    spot_balance = fetch_balance(spot_exchange, "USDT")
    futures_balance = fetch_balance(futures_exchange, "USDT")

    print(spot_balance, futures_balance)

    required_futures_balance = (spot_balance + futures_balance) / (leverage + 1)
    required_futures_balance = math.floor(required_futures_balance * 10**8) / 10**8

    if required_futures_balance > futures_balance:
        transfer_amount = required_futures_balance - futures_balance
        transfer_amount = math.floor(transfer_amount * 10**8) / 10**8
        transfer_usdt(spot_exchange, "spot", "future", transfer_amount)
        print(f"Transferred {transfer_amount} USDT from Spot to Futures.")
    elif required_futures_balance < futures_balance:
        transfer_amount = futures_balance - required_futures_balance
        transfer_amount = math.floor(transfer_amount * 10**8) / 10**8
        transfer_usdt(spot_exchange, "future", "spot", transfer_amount)
        print(f"Transferred {transfer_amount} USDT from Futures to Spot.")
    else:
        print("No transfer needed. Balances are already in the desired ratio.")


def transfer_to_master(exchange, master_exchange, currency, amount):
    """
    Transfer funds from a sub-account to the master account.

    :param exchange: The ccxt exchange instance of the sub-account.
    :param currency: The currency to transfer (e.g., 'BTC').
    :param amount: The amount to transfer.
    :return: The transfer details if successful, None otherwise.
    """
    try:
        transfer = exchange.sapiPostSubAccountTransferSubToMaster(
            {"asset": currency, "amount": float(amount)}
        )
        print(f"Transfer to master account successful: {transfer}")
        return transfer
    except Exception as e:
        print(f"An error occurred during transfer_to_master: {e}")
        return None


def withdraw(
    exchange, master_exchange, currency, percentage, address, tag=None, network=None
):
    """
    Withdraws a specified percentage of a currency to a given address, optionally specifying a network.

    :param exchange: The ccxt exchange instance of the sub-account.
    :param currency: The currency to withdraw (e.g., 'BTC').
    :param percentage: The percentage of the balance to withdraw.
    :param address: The address to withdraw to.
    :param tag: An optional tag or memo for the withdrawal.
    :param network: An optional network to specify for the withdrawal.
    :return: The withdrawal details if successful, None otherwise.
    """
    try:
        # Fetch the balance from the sub-account
        balance = fetch_balance(exchange, currency)
        if balance is None:
            print("Error: Unable to fetch balance.")
            return None
        print(f"Sub-account Balance: {balance} {currency}")

        # Calculate the amount to withdraw based on the specified percentage of the balance
        amount = Decimal(balance) * Decimal(percentage) / Decimal(100)

        # Fetch the withdraw integer multiple for the currency and network
        withdraw_integer_multiple = get_withdraw_integer_multiple(
            exchange, currency, network
        )
        if withdraw_integer_multiple is None:
            print(
                f"Error: Unable to fetch withdraw integer multiple for currency {currency} on network {network}."
            )
            return None

        print(withdraw_integer_multiple)
        print("amount", float(amount))

        # Ensure the amount is rounded to the required precision
        amount = (amount // withdraw_integer_multiple) * withdraw_integer_multiple

        print("amount", float(amount))

        # Transfer the amount to the master account
        transfer_result = transfer_to_master(
            exchange, master_exchange, currency, amount
        )
        if not transfer_result:
            print("Error: Transfer to master account failed.")
            return None

        # Withdraw the funds from the master account
        params = {}
        if network:
            params["network"] = network

        if tag:
            withdrawal = master_exchange.withdraw(
                currency, float(amount), address, tag, params=params
            )
        else:
            withdrawal = master_exchange.withdraw(
                currency, float(amount), address, params=params
            )

        print(f"Withdrawal request successful: {withdrawal}")
        return withdrawal
    except Exception as e:
        print(f"An error occurred in withdraw: {e}")
        return None


def check_withdrawal_limit_from_coinone(currency):
    """
    Checks the withdrawal limit for a specified currency on Coinone.

    :param currency: The currency to check the withdrawal limit for (e.g., 'BTC').
    """
    # Prepare the data for the API call
    data = {"currency": currency}

    # Define the URL for the withdrawal limit endpoint
    url = "https://api.coinone.co.kr/v2.1/transaction/coin/withdrawal/limit"

    # Use the generic API call function
    result = call_coinone_api(url, "POST", data)

    # Check for errors in the response
    if result is None:
        print("Error checking withdrawal limit.")
        return None

    # Return the withdrawal limit
    return result.get("limit")


def withdraw_from_coinone(currency, amount, address, secondary_address=None):
    """
    Withdraws a specified amount of a currency from Coinone to a specified address.

    :param currency: The currency to withdraw (e.g., 'BTC').
    :param amount: The amount of the currency to withdraw.
    :param address: The address to withdraw to.
    :param secondary_address: Optional secondary address (e.g., memo or tag for certain coins).
    """
    # Generate a nonce using UUID
    nonce = str(uuid.uuid4())

    # Prepare the payload for the request
    payload = {
        "access_token": coinone_api_key,
        "nonce": nonce,
        "currency": currency,
        "amount": str(amount),
        "address": address,
    }

    # Include secondary address if provided
    if secondary_address:
        payload["secondary_address"] = secondary_address

    # Encode the payload to base64
    encoded_payload = base64.b64encode(json.dumps(payload).encode("utf-8"))

    # Generate a signature using HMAC-SHA512
    signature = hmac.new(
        coinone_api_secret.encode("utf-8"), encoded_payload, hashlib.sha512
    ).hexdigest()

    # Set the headers for the request
    headers = {
        "Content-Type": "application/json",
        "X-COINONE-PAYLOAD": encoded_payload,
        "X-COINONE-SIGNATURE": signature,
    }

    # Define the URL for the withdrawal endpoint
    url = "https://api.coinone.co.kr/v2.1/transaction/coin/withdrawal/"

    # Make the POST request to the Coinone API
    response = requests.post(url, headers=headers, data=encoded_payload)

    # Parse the response data
    data = response.json()
    print(data)

    # Check for errors in the response
    if data.get("error_code") != "0":
        print(f"Error during withdrawal: {data.get('errorMessage')}")
        return None

    # Return the response data
    return data


def fetch_withdrawal_status(exchange, currency, withdrawal_id):
    """
    Fetch the status of a specific withdrawal.

    :param exchange: The ccxt exchange instance.
    :param currency: The currency of the withdrawal (e.g., 'BTC').
    :param withdrawal_id: The ID of the withdrawal to check.
    :return: The withdrawal details if available, None otherwise.
    """
    try:
        withdrawals = exchange.fetch_withdrawals(code=currency, limit=1)
        # print(withdrawals)
        for withdrawal in withdrawals:
            if withdrawal["id"] == withdrawal_id:
                return withdrawal
        print("Withdrawal not found.")
        return None
    except Exception as e:
        print(
            f"An error occurred while checking the withdrawal status in fetch_withdrawal_status: {e}"
        )
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
            if deposit["txid"] == txid:
                return deposit
        print("Deposit not found.")
        return None
    except Exception as e:
        print(
            f"An error occurred while checking the deposit status in fetch_deposit_status: {e}"
        )
        return None


def fetch_coinone_deposit_history(currency):
    res = call_coinone_api(
        "https://api.coinone.co.kr/v2.1/transaction/coin/history",
        method="POST",
        data={
            "currency": currency,
            "is_deposit": True,
        },
        version=2,
    )

    return res


def fetch_coinone_deposit_status(currency, txid):
    deposit_history = fetch_coinone_deposit_history(currency)["transactions"]

    for deposit in deposit_history:
        if deposit["txid"] == txid:
            return deposit
    print("Deposit not found in Coinone history.")
    return None


def fetch_coinone_deposit_status_with_id(id):
    res = call_coinone_api(
        "https://api.coinone.co.kr/v2.1/transaction/coin/history/detail/",
        method="POST",
        data={"id": "3e03e924bd4719c08c73cdb21e0ebe34ac8e84d4da39aa2768ecd3e1505c258e"},
        version=2,
    )

    return res


def fetch_binance_master_withdrawal_status(currency, withdrawal_id):
    withdrawals = call_binance_api(
        url="https://api.binance.com/sapi/v1/capital/withdraw/history",
        method="GET",
        data={
            "coin": currency,
        },
    )
    for withdrawal in withdrawals:
        if withdrawal["id"] == withdrawal_id:
            return withdrawal
    pass


def wait_for_coinone_deposit_completion(currency, withdrawal_id, polling_interval=10):
    # TODO: Complete
    print("Start")
    while True:
        print("Withdraw Cycle")
        withdrawal_status = fetch_binance_master_withdrawal_status(
            currency, withdrawal_id
        )
        # print(withdrawal_status)
        if withdrawal_status:
            status = withdrawal_status["status"]
            print(f"Current withdrawal status: {status}")
            if status == 6:
                print("The withdrawal has been completed.")
                txid = withdrawal_status["txId"]
                print("txid: " + txid)

                while True:
                    print("Deposit Cycle")

                    deposit_status = fetch_coinone_deposit_status(currency, txid)

                    if deposit_status:
                        if deposit_status["status"] == "DEPOSIT_SUCCESS":
                            print("Deposit Success")
                            # print(deposit_status)
                            return withdrawal_status, deposit_status
                        elif deposit_status["status"] == "DEPOSIT_WAIT":
                            print("Waiting for deposit confirmation.")
                            time.sleep(polling_interval)
                            continue
                        else:
                            print("Deposit Fail")
                            return withdrawal_status, deposit_status

                    else:
                        print("Failed to retrieve deposit status.")
                        time.sleep(polling_interval)
            elif status in [1, 3, 6]:
                print("Withdraw failed")
                return None
            else:
                print("Waiting for withdraw confirmation.")
                time.sleep(polling_interval)

        else:
            print("Failed to retrieve withdrawal status.")

            time.sleep(polling_interval)


def wait_for_withdrawal_completion(
    from_exchange, to_exchange, currency, withdrawal_id, polling_interval=10
):
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
            from_exchange, currency, withdrawal_id
        )
        if withdrawal_status:
            status = withdrawal_status["status"]
            print(f"Current withdrawal status: {status}")
            if status in ["ok", "completed"]:
                print("The withdrawal has been completed.")
                txid = withdrawal_status["txid"]

                # Check deposit status on the destination exchange
                while True:
                    deposit_status = fetch_deposit_status(to_exchange, currency, txid)
                    if deposit_status:
                        deposit_status_str = deposit_status["status"]
                        print(f"Current deposit status: {deposit_status_str}")
                        if deposit_status_str == "ok":
                            print("The deposit has been credited to your account.")
                            return
                    else:
                        print("Failed to retrieve deposit status.")

                    time.sleep(polling_interval)

                break
            elif status == "canceled":
                print("The withdrawal has been canceled.")
                break
        else:
            print("Failed to retrieve withdrawal status.")

        time.sleep(polling_interval)
