from fetch_data import *


def find_opportunities(ex_a: str, ex_b: str, symbol: str = 'BTC/USDT', timeframe: str = '4h', limit: int = 1000):
    # Fetch data
    ex_a_data = fetch_historical_data(ex_a, symbol, timeframe, limit)
    ex_b_data = fetch_historical_data(ex_b, symbol, timeframe, limit)

    # Merge the data on timestamp
    merged_data = pd.merge(ex_a_data, ex_b_data,
                           on='timestamp', suffixes=('_binance', '_bybit'))

    # Calculate the price difference
    merged_data['price_diff'] = merged_data['close_binance'] - \
        merged_data['close_bybit']

    # Define the arbitrage threshold
    threshold = 10  # Arbitrage threshold in USD

    # Identify arbitrage opportunities
    arbitrage_opportunities = merged_data[merged_data['price_diff'].abs(
    ) > threshold]

    # Print the arbitrage opportunities
    if not arbitrage_opportunities.empty:
        print("Arbitrage Opportunities Found:")
        print(arbitrage_opportunities[[
              'timestamp', 'close_binance', 'close_bybit', 'price_diff']])
    else:
        print("No arbitrage opportunities found.")


class ExchangeBalance:
    def __init__(self, crypto_balance, usdt_balance, fee_rate):
        self.crypto_balance = crypto_balance
        self.usdt_balance = usdt_balance
        self.fee_rate = fee_rate

    def buy_btc(self, amount, price):
        fee = amount * self.fee_rate
        self.crypto_balance += amount
        self.usdt_balance -= (amount * price + fee)

    def sell_btc(self, amount, price):
        fee = amount * self.fee_rate
        self.crypto_balance -= amount
        self.usdt_balance += (amount * price - fee)

    def set_usdt_balance(self, usdt_balance):
        self.usdt_balance = usdt_balance

    def set_crypto_balance(self, crypto_balance):
        self.crypto_balance = crypto_balance

    def set_balance(self, usdt_balance, crypto_balance):
        self.set_usdt_balance(usdt_balance)
        self.set_crypto_balance(crypto_balance)

    def __repr__(self):
        return f"BTC: {self.crypto_balance:.4f}, USDT: {self.usdt_balance:.2f}"


def balance_balances(a: ExchangeBalance, b: ExchangeBalance, usdt_fee: int, crypto_fee: int):
    usdt_balance = (a.usdt_balance + b.usdt_balance - usdt_fee) / 2
    crypto_balance = (a.crypto_balance + b.crypto_balance - crypto_fee) / 2
    a.set_balance(usdt_balance, crypto_balance)
    b.set_balance(usdt_balance, crypto_balance)


def fetch_and_prepare_data(ex_a: str, ex_b: str, symbol: str = 'BTC/USDT', timeframe: str = '4h', limit: int = 1000):
    # Fetch data

    ex_a_data = fetch_historical_data(ex_a, symbol, timeframe, limit)
    ex_b_data = fetch_historical_data(ex_b, symbol, timeframe, limit)

    # Merge the data on timestamp
    merged_data = pd.merge(ex_a_data, ex_b_data,
                           on='timestamp', suffixes=('_binance', '_bybit'))

    # Calculate the price difference
    merged_data['price_diff'] = merged_data['close_binance'] - \
        merged_data['close_bybit']
    merged_data['price_diff_percent'] = (
        merged_data['price_diff'] / merged_data[['close_binance', 'close_bybit']].mean(axis=1)) * 100

    return merged_data


def simulate_arbitrage(data, threshold=10):
    # Initial balances (arbitrary values)
    initial_crypto_balance = 10000
    initial_usdt_balance = 10000

    # Create balance objects for both exchanges
    a_balance = ExchangeBalance(
        initial_crypto_balance, initial_usdt_balance, 0.0001)
    b_balance = ExchangeBalance(
        initial_crypto_balance, initial_usdt_balance, 0.0001)

    # Simulation
    for index, row in data.iterrows():
        if abs(row['price_diff_percent']) > threshold:
            if row['price_diff'] > 0:
                # Buy on Bybit, Sell on Binance
                trade_amount = b_balance.usdt_balance / row['close_bybit']
                b_balance.buy_btc(trade_amount, row['close_bybit'])
                a_balance.sell_btc(trade_amount, row['close_binance'])
            else:
                # Buy on Binance, Sell on Bybit
                trade_amount = a_balance.usdt_balance / \
                    row['close_binance']
                a_balance.buy_btc(trade_amount, row['close_binance'])
                b_balance.sell_btc(trade_amount, row['close_bybit'])

            # Balance the balances by averaging
            balance_balances(a_balance, b_balance, 10, 10)

    # Calculate initial and final total balances in USDT
    initial_total_balance = (
        initial_crypto_balance * data.iloc[0]['close_binance']) + initial_usdt_balance
    final_total_balance = (a_balance.crypto_balance * data.iloc[-1]['close_binance']) + a_balance.usdt_balance + (
        b_balance.crypto_balance * data.iloc[-1]['close_bybit']) + b_balance.usdt_balance

    print("Initial Total Balance in USDT: ", initial_total_balance)
    print("Final Total Balance in USDT: ", final_total_balance)
    print("Binance Balance: ", a_balance)
    print("Bybit Balance: ", b_balance)


if __name__ == "__main__":

    # data = fetch_and_prepare_data('upbit', 'binance', 'XRP/USDT', '1h', 1000)
    # print(data)
    # simulate_arbitrage(data, 0.05)
    find_opportunities('binance', 'bybit')
    pass
