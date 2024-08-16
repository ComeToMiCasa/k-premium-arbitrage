from dotenv import load_dotenv
import os
import ccxt


load_dotenv()


# Get API keys from environment variables
binance_api_key = os.getenv("BINANCE_API_KEY")
binance_api_secret = os.getenv("BINANCE_API_SECRET")
binance_master_api_key = os.getenv("BINANCE_MASTER_API_KEY")
binance_master_api_secret = os.getenv("BINANCE_MASTER_API_SECRET")
binance_test_api_key = os.getenv("BINANCE_TEST_API_KEY")
binance_test_api_secret = os.getenv("BINANCE_TEST_API_SECRET")
binance_futures_test_api_key = os.getenv("BINANCE_FUTURES_TEST_API_KEY")
binance_futures_test_api_secret = os.getenv("BINANCE_FUTURES_TEST_API_SECRET")
upbit_api_key = os.getenv("UPBIT_API_KEY")
upbit_api_secret = os.getenv("UPBIT_API_SECRET")
coinone_api_key = os.getenv("COINONE_API_KEY")
coinone_api_secret = os.getenv("COINONE_API_SECRET")

alphavantage_api_key = os.getenv("ALPHAVNTAGE_API_KEY")

# transfer_mediums = ["XRP", "XLM", "TRX", "ALGO", "EOS", "DOGE"]

transfer_mediums = {
    "XRP": {
        "network": "XRP",
        "address": "rNxp4h8apvRis6mJf9Sh8C6iRxfrDWN7AV",
        "tag": "395631049",
    },
    "XLM": {
        "network": "XLM",
        "address": "GABFQIK63R2NETJM7T673EAMZN4RJLLGP3OFUEJU5SZVTGWUKULZJNL6",
        "tag": "351017843",
    },
    "TRX": {"network": "", "address": "", "tag": ""},
    "ALGO": {
        "network": "ALGO",
        "address": "BBB7YXRCCWJL7IKJCSQO3MZKIKEAHB4JOTR4TQKAHDNX6G3K3GXJ5H5EPY",
        "tag": "",
    },
    "EOS": {"network": "EOS", "address": "eosbndeposit", "tag": "102464986"},
    "VET": {
        "network": "VET",
        "address": "0xbc9fe644ffa9acca2259c0d9e850027039eea7e0",
        "tag": "",
    },
    "HBAR": {"network": "HBAR", "address": "0.0.1873771", "tag": "101923666"},
    # "IOTA": {
    #     "network": "IOTA",
    #     "address": "iota1qpc6jdgmcuezuv3ca25r28qwmzsjayyme7rwlyajw30yqahrrph7q8qepfe",
    #     "tag": "",
    # },
    "WAVES": {
        "network": "WAVES",
        "address": "3P8ac9LqudVdmSXthj8m5sh2GN8NeVQ4KdH",
        "tag": "",
    },
    "ZIL": {
        "network": "ZIL",
        "address": "zil19en24ze0mp6l3ytsxdvzvqklkfksdjxsd2fscv",
        "tag": "",
    },
    "DOT": {
        "network": "DOT",
        "address": "15hfzP21zMhTxzWyxu1VKCYjuQua4ypWzPaFP3gKCxcGVfSK",
        "tag": "",
    },
}

# binance, binance_futures is subaccount
# binance_master is the master account used for withdrawal

# Initialize exchanges with API keys
binance = ccxt.binance(
    {
        "apiKey": binance_api_key,
        "secret": binance_api_secret,
        "enableRateLimit": True,
    }
)


# Initialize the Binance Futures exchange using the same API key
binance_futures = ccxt.binance(
    {
        "apiKey": binance_api_key,
        "secret": binance_api_secret,
        "enableRateLimit": True,
        "options": {
            "defaultType": "future",
        },
    }
)

# Initialize the Binance USD-M futures market read-only.
binanceusdm = ccxt.binanceusdm({})

binance_master = ccxt.binance(
    {
        "apiKey": binance_master_api_key,
        "secret": binance_master_api_secret,
        "enableRateLimit": True,
    }
)

binance_test = ccxt.binance(
    {
        "apiKey": binance_test_api_key,
        "secret": binance_test_api_secret,
        "enableRateLimit": True,
    }
)

binance_test.set_sandbox_mode(True)

binance_futures_test = ccxt.binance(
    {
        "apiKey": binance_futures_test_api_key,
        "secret": binance_futures_test_api_secret,
        "enableRateLimit": True,
        "options": {
            "defaultType": "future",
        },
    }
)

binance_futures_test.set_sandbox_mode(True)

upbit = ccxt.upbit(
    {
        "apiKey": upbit_api_key,
        "secret": upbit_api_secret,
        "enableRateLimit": True,
    }
)

coinone = ccxt.coinone(
    {
        "apiKey": coinone_api_key,
        "secret": coinone_api_secret,
        "enableRateLimit": True,
    }
)

binance.options["adjustForTimeDifference"] = True
binance_futures.options["adjustForTimeDifference"] = True
binance_test.options["adjustForTimeDifference"] = True
upbit.options["adjustForTimeDifference"] = True
coinone.options["adjustForTimeDifference"] = True
