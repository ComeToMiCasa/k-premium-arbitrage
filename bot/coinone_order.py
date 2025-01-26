from coinone_api import *
from balance import fetch_balance
from exchanges import coinone


def coinone_sell(target, quote, percentage):

    balance = fetch_balance(coinone, target)

    amount = balance * percentage / 100

    res = call_coinone_api(
        url="https://api.coinone.co.kr/v2.1/order",
        method="POST",
        data={
            "side": "SELL",
            "quote_currency": quote,
            "target_currency": target,
            "type": "MARKET",
            "qty": amount,
        },
    )

    # print(res)
    # return res

    return {
        "order": res,
        # "average_price": order["average"],
        # "quantity": order["filled"],
        # "total_cost": order["cost"],
        # "fee": order["fees"],
    }
