from dotenv import load_dotenv
import os
import ccxt


load_dotenv()


# Get API keys from environment variables
binance_api_key = os.getenv('BINANCE_API_KEY')
binance_api_secret = os.getenv('BINANCE_API_SECRET')
binance_master_api_key = os.getenv('BINANCE_MASTER_API_KEY')
binance_master_api_secret = os.getenv('BINANCE_MASTER_API_SECRET')
binance_test_api_key = os.getenv('BINANCE_TEST_API_KEY')
binance_test_api_secret = os.getenv('BINANCE_TEST_API_SECRET')
binance_futures_test_api_key = os.getenv('BINANCE_FUTURES_TEST_API_KEY')
binance_futures_test_api_secret = os.getenv('BINANCE_FUTURES_TEST_API_SECRET')
upbit_api_key = os.getenv('UPBIT_API_KEY')
upbit_api_secret = os.getenv('UPBIT_API_SECRET')
coinone_api_key = os.getenv('COINONE_API_KEY')
coinone_api_secret = os.getenv('COINONE_API_SECRET')

alphavantage_api_key = os.getenv('ALPHAVNTAGE_API_KEY')

transfer_mediums = ['XRP', 'XLM', 'TRX', 'ALGO', 'EOS', 'DOGE']

# Initialize exchanges with API keys
binance = ccxt.binance({
    'apiKey': binance_api_key,
    'secret': binance_api_secret,
    'enableRateLimit': True,
})


# Initialize the Binance Futures exchange using the same API key
binance_futures = ccxt.binance({
    'apiKey': binance_api_key,
    'secret': binance_api_secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
    }
})

binance_master = ccxt.binance({
    'apiKey': binance_master_api_key,
    'secret': binance_master_api_secret,
    'enableRateLimit': True,
})

binance_test = ccxt.binance({
    'apiKey': binance_test_api_key,
    'secret': binance_test_api_secret,
    'enableRateLimit': True,
})

binance_test.set_sandbox_mode(True)

binance_futures_test = ccxt.binance({
    'apiKey': binance_futures_test_api_key,
    'secret': binance_futures_test_api_secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
    },
})

binance_futures_test.set_sandbox_mode(True)

upbit = ccxt.upbit({
    'apiKey': upbit_api_key,
    'secret': upbit_api_secret,
    'enableRateLimit': True,
})

coinone = ccxt.coinone({
    'apiKey': coinone_api_key,
    'secret': coinone_api_secret,
    'enableRateLimit': True,
})

binance.options['adjustForTimeDifference'] = True
binance_futures.options['adjustForTimeDifference'] = True
binance_test.options['adjustForTimeDifference'] = True
upbit.options['adjustForTimeDifference'] = True
coinone.options['adjustForTimeDifference'] = True
