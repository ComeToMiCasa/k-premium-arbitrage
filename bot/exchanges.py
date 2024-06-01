from dotenv import load_dotenv
import os
import ccxt

# Get API keys from environment variables
binance_api_key = os.getenv('BINANCE_API_KEY')
binance_secret_key = os.getenv('BINANCE_API_SECRET')
binance_test_api_key = os.getenv('BINANCE_TEST_API_KEY')
binance_test_secret_key = os.getenv('BINANCE_TEST_API_SECRET')
upbit_api_key = os.getenv('UPBIT_API_KEY')
upbit_secret_key = os.getenv('UPBIT_API_SECRET')
coinone_api_key = os.getenv('COINONE_API_KEY')
coinone_secret_key = os.getenv('COINONE_API_SECRET')

alphavantage_api_key = os.getenv('ALPHAVNTAGE_API_KEY')

transfer_mediums = ['XRP', 'XLM', 'TRX', 'ALGO', 'EOS', 'DOGE']

# Initialize exchanges with API keys
binance = ccxt.binance({
    'apiKey': binance_api_key,
    'secret': binance_secret_key,
    'enableRateLimit': True,
})

# Initialize the Binance Futures exchange using the same API key
binance_futures = ccxt.binance({
    'apiKey': binance_api_key,
    'secret': binance_secret_key,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
    }
})

binance_test = ccxt.binance({
    'apiKey': binance_test_api_key,
    'secret': binance_test_secret_key,
    'enableRateLimit': True,
})

binance_test.set_sandbox_mode(True)

upbit = ccxt.upbit({
    'apiKey': upbit_api_key,
    'secret': upbit_secret_key,
    'enableRateLimit': True,
})

coinone = ccxt.coinone({
    'apiKey': coinone_api_key,
    'secret': coinone_secret_key,
    'enableRateLimit': True,
})

binance.options['adjustForTimeDifference'] = True
binance_futures.options['adjustForTimeDifference'] = True
binance_test.options['adjustForTimeDifference'] = True
upbit.options['adjustForTimeDifference'] = True
coinone.options['adjustForTimeDifference'] = True
