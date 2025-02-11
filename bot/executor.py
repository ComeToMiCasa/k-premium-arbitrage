from main import *
from orderbook import *


def execute():
    # fx_rate = 1300
    # csv_file_data = read_address_network_csv("address_network.csv")
    # # state = None
    # # cycle(state, csv_file_data)
    # target = "PHA"

    # # Fetch all necessary data before the loop
    # coinone_markets = coinone.load_markets()
    # binance_markets = binance_master.load_markets()
    # binance_futures_markets = binanceusdm.load_markets()
    # binance_currencies = binance_master.fetch_currencies()
    # coinone_currencies = coinone.fetch_currencies()

    # comprehensive_currency_check(target,
    #                              csv_file_data[target],
    #                              coinone_markets, binance_markets,
    #                              binance_futures_markets,
    #                              binance_currencies,
    #                              coinone_currencies,)
    order_book = fetch_coinone_orderbook("KRW", "BTC")

    profitable, profit, sale_value, avg_sale_price = will_market_sell_be_profitable(
        1, 145100000, order_book)

    print(f"Profitable? {profitable}")
    print(f"Total sale value: {sale_value:.2f} KRW")
    print(f"Weighted average sale price: {avg_sale_price:.2f} KRW")
    print(f"Profit (or loss if negative): {profit:.2f} KRW")

    # # print(binance_currencies[target])
    # print(coinone_currencies[target])
    # # print(csv_file_data[target])
    # print(fetch_balance(binance, "USDT"))


if __name__ == "__main__":
    execute()
