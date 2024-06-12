import csv
from exchanges import binance, binance_futures, coinone


coinone_tradeable_symbols = ['TNSR/KRW', 'APP/KRW', 'STRK/KRW', 'STG/KRW', 'ALGO/KRW', 'ANKR/KRW', 'APT/KRW', 'DODO/KRW', 'AI/KRW', 'WLD/KRW', 'GLM/KRW', 'NEST/KRW', 'FIS/KRW', 'DVI/KRW', 'VIC/KRW', 'APE/KRW', 'BAT/KRW', 'BLUR/KRW', 'PIXEL/KRW', 'PRIME/KRW', 'ASTR/KRW', 'BAND/KRW', 'KSM/KRW', 'EGG/KRW', 'PENDLE/KRW', 'CAKE/KRW', 'FIL/KRW', 'PYTH/KRW', 'KSP/KRW', 'BAL/KRW', 'QTCON/KRW', 'WEMIX/KRW', 'MANA/KRW', 'MINA/KRW', 'FRONT/KRW', 'XLM/KRW', 'IOTA/KRW', 'BTT/KRW', 'HPO/KRW', 'CVX/KRW', 'JTO/KRW', 'CFG/KRW', 'WAVES/KRW', 'STORJ/KRW', 'ONG/KRW', 'ALEX/KRW', 'ARB/KRW', 'BTC/KRW', 'SEI/KRW', 'TWT/KRW', 'SHIB/KRW', 'BTG/KRW', 'IOTX/KRW', 'NEAR/KRW', 'STPT/KRW', 'SUI/KRW', 'ZRX/KRW', 'BCH/KRW', 'BSV/KRW', 'JST/KRW', 'SUN/KRW', 'MAVIA/KRW', 'QTUM/KRW', 'GMT/KRW', 'CEP/KRW', 'HOT/KRW', 'LINK/KRW', 'STX/KRW', 'IOST/KRW', 'VOLT/KRW', 'AAVE/KRW', 'REZ/KRW', 'ZETA/KRW', 'MLK/KRW', 'SXP/KRW', 'MKR/KRW', 'LIT/KRW', 'ICP/KRW', 'MASK/KRW', 'LZM/KRW', 'MYRO/KRW', 'ICX/KRW', 'ADA/KRW', 'BAAS/KRW', 'ISK/KRW', 'WIKEN/KRW', 'ACH/KRW', 'JUP/KRW', 'TIA/KRW', 'BEL/KRW', 'ONT/KRW', 'SPURS/KRW', 'W/KRW', 'T/KRW', 'TOKAMAK/KRW', 'CFX/KRW', 'ASM/KRW', 'BONK/KRW', 'ZTX/KRW', 'BIGTIME/KRW', 'DIA/KRW', 'LQTY/KRW', 'SIX/KRW', 'ENS/KRW', 'GRT/KRW', 'GAL/KRW', 'ALPHA/KRW', 'PCI/KRW', 'PAXG/KRW', 'HBAR/KRW', 'DOGE/KRW', 'GAS/KRW', 'ENA/KRW', 'ORB/KRW', 'ONDO/KRW', 'PEPE/KRW', 'WBTC/KRW', 'CLBK/KRW', 'SKLAY/KRW', 'MATIC/KRW', 'AUCTION/KRW', 'UMA/KRW',
                             'XRP/KRW', 'NTRN/KRW', 'KAVA/KRW', 'CTSI/KRW', 'CHZ/KRW', 'SAND/KRW', 'ATOM/KRW', 'ARKM/KRW', 'IQ/KRW', 'KLAY/KRW', 'FORTH/KRW', 'CLV/KRW', 'SKL/KRW', 'XEC/KRW', 'CELO/KRW', 'PROM/KRW', 'HVH/KRW', 'ZIL/KRW', '1INCH/KRW', 'UOS/KRW', 'AXS/KRW', 'MEME/KRW', 'WAXL/KRW', 'EOS/KRW', 'FNCY/KRW', 'BORA/KRW', 'RUNE/KRW', 'UNI/KRW', 'MNR/KRW', 'NPT/KRW', 'MNT/KRW', 'MANTA/KRW', 'CKB/KRW', 'XTZ/KRW', 'ONIT/KRW', 'HIBS/KRW', 'ERN/KRW', 'KNC/KRW', 'FNSA/KRW', 'MAV/KRW', 'EVER/KRW', 'PHA/KRW', 'CETUS/KRW', 'TON/KRW', 'MAP/KRW', 'FLOW/KRW', 'AVAX/KRW', 'FTM/KRW', 'TEMCO/KRW', 'NEXT/KRW', 'DOT/KRW', 'SLN/KRW', 'ZEUS/KRW', 'HFT/KRW', 'COMP/KRW', 'SPA/KRW', 'MTL/KRW', 'VET/KRW', 'NEON/KRW', 'AGIX/KRW', 'ALT/KRW', 'BNT/KRW', 'DAO/KRW', 'OGN/KRW', 'ARPA/KRW', 'GRND/KRW', 'SOL/KRW', 'BNB/KRW', 'FET/KRW', 'DRC/KRW', 'ETC/KRW', 'SEILOR/KRW', 'DYDX/KRW', 'ETH/KRW', 'FLUX/KRW', 'NEO/KRW', 'PRCL/KRW', 'SUSHI/KRW', 'NAVX/KRW', 'COS/KRW', 'DAD/KRW', 'MBX/KRW', 'PIB/KRW', 'TIDE/KRW', 'AEVO/KRW', 'MBL/KRW', 'CYBER/KRW', 'SNX/KRW', 'RNDR/KRW', 'GALA/KRW', 'SNT/KRW', 'HUNT/KRW', 'FXS/KRW', 'OP/KRW', 'CRO/KRW', 'USDC/KRW', 'CRV/KRW', 'CRU/KRW', 'INJ/KRW', 'RPL/KRW', 'DMAIL/KRW', 'CBK/KRW', 'KAI/KRW', 'HIGH/KRW', 'RON/KRW', 'USDT/KRW', 'IMX/KRW', 'MEV/KRW', 'DATA/KRW', 'KAS/KRW', 'MVC/KRW', 'BEAM/KRW', 'AMO/KRW', 'WNCG/KRW', 'ORBS/KRW', 'AMP/KRW', 'RDNT/KRW', 'ILV/KRW', 'LBL/KRW', 'EDU/KRW', 'ORCA/KRW', 'HIFI/KRW', 'NFT/KRW', 'NFP/KRW', 'TRX/KRW', 'LBR/KRW']


# def is_futures_tradable(exchange, target_currency):
#     """
#     Check if a target currency is tradable in the Binance Futures market with a /USDT pair.

#     :param exchange: The exchange instance (e.g., ccxt.binance()) configured for futures trading.
#     :param target_currency: The target currency to check (e.g., 'BTC').
#     :return: True if the /USDT pair for the target currency is tradable, False otherwise.
#     """
#     try:
#         # Fetch the list of futures markets
#         markets = exchange.load_markets()

#         # Construct the trading pair symbol for futures market
#         symbol = target_currency + "/USDT"

#         # Check if the symbol is available in the futures markets
#         if symbol in markets:
#             return True
#         else:
#             return False
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return False


def fetch_tradable_pairs(exchange):
    """
    Fetches all tradable pairs from the given exchange.

    :param exchange: The exchange instance (e.g., ccxt.coinone()).
    :return: A list of tradable pairs.
    """
    markets = exchange.load_markets()
    return list(markets.keys())


def is_futures_tradable(target_currency):
    """
    Checks if the target currency's /USDT pair is tradable on both Binance Spot and Futures markets.

    :param binance_spot: The exchange instance (e.g., ccxt.binance()) configured for spot trading.
    :param binance_futures: The exchange instance (e.g., ccxt.binance()) configured for futures trading.
    :param target_currency: The target currency to check (e.g., 'BTC').
    :return: A tuple with boolean indicating if tradable and the market ID if tradable.
    """
    pair = target_currency + '/USDT'
    try:
        # Load spot markets
        spot_markets = binance.load_markets()
        # Load futures markets
        futures_markets = binance_futures.load_markets()

        print(futures_markets[pair]['future'])

        # Check if the pair is tradable on both spot and futures markets
        is_spot_tradable = pair in spot_markets and spot_markets[
            pair]['active'] and spot_markets[pair]['spot']
        is_futures_tradable = pair in futures_markets and futures_markets[pair]['future']
        market_id = futures_markets[pair]['id'] if is_futures_tradable else None

        return is_spot_tradable and is_futures_tradable, market_id
    except Exception as e:
        print(f"An error occurred: {e}")
        return False, None


def main():
    # Fetch all tradable pairs from Coinone
    coinone_pairs = fetch_tradable_pairs(coinone)

    # Extract the unique target currencies from Coinone pairs
    target_currencies = set(pair.split('/')[0] for pair in coinone_pairs)

    # Check if each target currency is tradable on Binance Spot and Futures
    matching_currencies = []
    for currency in target_currencies:
        tradable, market_id = is_futures_tradable(binance_futures, currency)
        if tradable:
            matching_currencies.append((currency, market_id))

    # Write the matching currencies to a CSV file
    with open('matching_currencies.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Currency', 'Futures Market ID'])  # Write header
        for currency, market_id in matching_currencies:
            csv_writer.writerow([currency, market_id])

    print("Matching currencies have been written to matching_currencies.csv")


if __name__ == "__main__":
    main()
