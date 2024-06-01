import ccxt
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
binance_api_key = os.getenv('BINANCE_API_KEY')
binance_secret_key = os.getenv('BINANCE_SECRET_KEY')
bybit_api_key = os.getenv('BYBIT_API_KEY')
bybit_secret_key = os.getenv('BYBIT_SECRET_KEY')

# Initialize exchanges with API keys
binance = ccxt.binance({
    'apiKey': binance_api_key,
    'secret': binance_secret_key,
    'enableRateLimit': True,
})

bybit = ccxt.bybit({
    'apiKey': bybit_api_key,
    'secret': bybit_secret_key,
    'enableRateLimit': True,
})

upbit = ccxt.upbit()


# Define the symbol and timeframe
symbol = 'BTC/USDT'
timeframe = '1h'  # 4-hour intervals


# Fetch historical data from exchange


def fetch_historical_data(exchange: str, symbol: str = 'BTC/USDT', timeframe: str = '4h', limit: int = 1000):
    if exchange == "binance":
        return fetch_binance_data(symbol, timeframe, limit)
    elif exchange == "bybit":
        return fetch_bybit_data(symbol, timeframe, limit)
    elif exchange == "upbit":
        return fetch_upbit_data(symbol, timeframe, limit)
    else:
        return None


# Fetch historical data from Binance


def fetch_binance_data(symbol: str = 'BTC/USDT', timeframe: str = '4h', limit: int = 1000):
    ohlcv = binance.fetch_ohlcv(symbol, timeframe, limit=limit)
    binance_data = pd.DataFrame(
        ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    binance_data['timestamp'] = pd.to_datetime(
        binance_data['timestamp'], unit='ms')
    return binance_data


# Fetch historical data from Bybit


def fetch_bybit_data(symbol: str = 'BTC/USDT', timeframe: str = '4h', limit: int = 1000):
    ohlcv = bybit.fetch_ohlcv(symbol, timeframe, limit=limit)
    bybit_data = pd.DataFrame(
        ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    bybit_data['timestamp'] = pd.to_datetime(
        bybit_data['timestamp'], unit='ms')
    return bybit_data


# Fetch historical data from Upbit


def fetch_upbit_data(symbol: str = 'BTC/USDT', timeframe: str = '4h', limit: int = 1000):
    ohlcv = upbit.fetch_ohlcv(symbol, timeframe, limit=limit)
    upbit_data = pd.DataFrame(
        ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    upbit_data['timestamp'] = pd.to_datetime(
        upbit_data['timestamp'], unit='ms')
    return upbit_data
