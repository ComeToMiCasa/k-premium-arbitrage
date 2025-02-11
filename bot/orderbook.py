from coinone_api import *


def fetch_coinone_orderbook(quote, target):

    res = call_coinone_api(
        url=f"https://api.coinone.co.kr/public/v2/orderbook/{quote}/{target}",
        method="GET",
        data={}
    )

    return res


def will_market_sell_be_profitable(holdings_qty, avg_buy_price, order_book):
    """
    Determines if selling the entire crypto holding at market price is profitable.

    Parameters:
      holdings_qty (float): The amount of crypto you hold.
      avg_buy_price (float): Your average purchase price.
      order_book (dict): Order book data containing the bids.

    Returns:
      tuple: (is_profitable (bool), profit (float), total_sale_value (float), avg_sale_price (float))
             where:
               - is_profitable is True if total_sale_value exceeds cost basis,
               - profit is the difference between total_sale_value and cost basis,
               - total_sale_value is the cumulative proceeds from selling,
               - avg_sale_price is the weighted average price obtained.

    Note:
      This function assumes that bids are ordered from highest to lowest price.
      It also assumes that if there isn't enough liquidity in the order book
      to cover your entire holdings, you only sell what the book supports.
    """

    bids = order_book.get("bids", [])
    remaining_qty = holdings_qty
    total_sale_value = 0.0

    # Walk through the bids until we've sold the entire holding.
    for bid in bids:
        bid_price = float(bid["price"])
        bid_qty = float(bid["qty"])

        # If the current bid can fill the remaining order:
        if remaining_qty <= bid_qty:
            total_sale_value += remaining_qty * bid_price
            remaining_qty = 0
            break
        else:
            # Sell the full bid_qty at bid_price
            total_sale_value += bid_qty * bid_price
            remaining_qty -= bid_qty

    if remaining_qty > 0:
        # Not enough liquidity in the order book to sell the entire amount.
        print("Warning: Order book liquidity is insufficient to sell all holdings.")
        # Depending on your needs, you might decide to:
        #  - Sell only the available amount (already computed), or
        #  - Assume you get the last bid price for the remaining quantity.
        # Here, we leave total_sale_value as is (only for the amount that can be sold).

    # Compute weighted average sale price based on total holdings (if fully sold).
    # Note: If not fully sold, avg_sale_price is computed over the portion sold.
    avg_sale_price = total_sale_value / \
        (holdings_qty - remaining_qty) if (holdings_qty - remaining_qty) > 0 else 0

    cost_basis = holdings_qty * avg_buy_price
    profit = total_sale_value - cost_basis
    is_profitable = profit > 0

    return is_profitable, profit, total_sale_value, avg_sale_price


if __name__ == "__main__":
    # Example usage with your provided order book:
    order_book = {
        "result": "success",
        "error_code": "0",
        "timestamp": 1644488410702,
        "id": "1644488410702001",
        "quote_currency": "KRW",
        "target_currency": "BTC",
        "order_book_unit": "1000.0",
        "bids": [
            {"price": "75862000", "qty": "0.5"},
            {"price": "75860000", "qty": "0.5"},
            {"price": "75859000", "qty": "0.5"},
            {"price": "75857000", "qty": "0.5"},
            {"price": "75855000", "qty": "0.5"}
        ],
        "asks": [
            {"price": "75863000", "qty": "22.5"},
            {"price": "75865000", "qty": "22"},
            {"price": "75867000", "qty": "11"},
            {"price": "75869000", "qty": "23"},
            {"price": "75871000", "qty": "24"}
        ]
    }

    # Suppose you hold 1 BTC with an average buy price of 75,900,000 KRW.
    holdings_qty = 1.0
    avg_buy_price = 75900000

    profitable, profit, sale_value, avg_sale_price = will_market_sell_be_profitable(
        holdings_qty, avg_buy_price, order_book)

    print(f"Profitable? {profitable}")
    print(f"Total sale value: {sale_value:.2f} KRW")
    print(f"Weighted average sale price: {avg_sale_price:.2f} KRW")
    print(f"Profit (or loss if negative): {profit:.2f} KRW")
