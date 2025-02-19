import logging
import math
import os

from pymongo import MongoClient
from datetime import datetime
from alpaca.trading.client import TradingClient
from concurrent.futures import ThreadPoolExecutor


from trading import trading_client_main
from ranking import ranking_client_main
from helper_files.client_helper import get_latest_price
from helper_files.client_helper import strategies

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


# Configure logging
LOG_FILE = "system.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)

# Suppress logs from requests and pandas
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("pandas").setLevel(logging.WARNING)


indicator_periods = {
    "BBANDS_indicator": "1y",
    "DEMA_indicator": "1mo",
    "EMA_indicator": "1mo",
    "HT_TRENDLINE_indicator": "6mo",
    "KAMA_indicator": "1mo",
    "MA_indicator": "3mo",
    "MAMA_indicator": "6mo",
    "MAVP_indicator": "3mo",
    "MIDPOINT_indicator": "1mo",
    "MIDPRICE_indicator": "1mo",
    "SAR_indicator": "6mo",
    "SAREXT_indicator": "6mo",
    "SMA_indicator": "1mo",
    "T3_indicator": "1mo",
    "TEMA_indicator": "1mo",
    "TRIMA_indicator": "1mo",
    "WMA_indicator": "1mo",
    "ADX_indicator": "3mo",
    "ADXR_indicator": "3mo",
    "APO_indicator": "1mo",
    "AROON_indicator": "3mo",
    "AROONOSC_indicator": "3mo",
    "BOP_indicator": "1mo",
    "CCI_indicator": "1mo",
    "CMO_indicator": "1mo",
    "DX_indicator": "1mo",
    "MACD_indicator": "3mo",
    "MACDEXT_indicator": "3mo",
    "MACDFIX_indicator": "3mo",
    "MFI_indicator": "1mo",
    "MINUS_DI_indicator": "1mo",
    "MINUS_DM_indicator": "1mo",
    "MOM_indicator": "1mo",
    "PLUS_DI_indicator": "1mo",
    "PLUS_DM_indicator": "1mo",
    "PPO_indicator": "1mo",
    "ROC_indicator": "1mo",
    "ROCP_indicator": "1mo",
    "ROCR_indicator": "1mo",
    "ROCR100_indicator": "1mo",
    "RSI_indicator": "1mo",
    "STOCH_indicator": "1mo",
    "STOCHF_indicator": "1mo",
    "STOCHRSI_indicator": "1mo",
    "TRIX_indicator": "1mo",
    "ULTOSC_indicator": "6mo",
    "WILLR_indicator": "1mo",
    "AD_indicator": "1mo",
    "ADOSC_indicator": "1mo",
    "OBV_indicator": "1mo",
    "HT_DCPERIOD_indicator": "2y",
    "HT_DCPHASE_indicator": "2y",
    "HT_PHASOR_indicator": "2y",
    "HT_SINE_indicator": "2y",
    "HT_TRENDMODE_indicator": "2y",
    "AVGPRICE_indicator": "1mo",
    "MEDPRICE_indicator": "1mo",
    "TYPPRICE_indicator": "1mo",
    "WCLPRICE_indicator": "1mo",
    "ATR_indicator": "3mo",
    "NATR_indicator": "3mo",
    "TRANGE_indicator": "3mo",
    "CDL2CROWS_indicator": "1mo",
    "CDL3BLACKCROWS_indicator": "1mo",
    "CDL3INSIDE_indicator": "1mo",
    "CDL3LINESTRIKE_indicator": "1mo",
    "CDL3OUTSIDE_indicator": "1mo",
    "CDL3STARSINSOUTH_indicator": "1mo",
    "CDL3WHITESOLDIERS_indicator": "1mo",
    "CDLABANDONEDBABY_indicator": "1mo",
    "CDLADVANCEBLOCK_indicator": "1mo",
    "CDLBELTHOLD_indicator": "1mo",
    "CDLBREAKAWAY_indicator": "1mo",
    "CDLCLOSINGMARUBOZU_indicator": "1mo",
    "CDLCONCEALBABYSWALL_indicator": "1mo",
    "CDLCOUNTERATTACK_indicator": "1mo",
    "CDLDARKCLOUDCOVER_indicator": "1mo",
    "CDLDOJI_indicator": "1mo",
    "CDLDOJISTAR_indicator": "1mo",
    "CDLDRAGONFLYDOJI_indicator": "1mo",
    "CDLENGULFING_indicator": "1mo",
    "CDLEVENINGDOJISTAR_indicator": "1mo",
    "CDLEVENINGSTAR_indicator": "1mo",
    "CDLGAPSIDESIDEWHITE_indicator": "1mo",
    "CDLGRAVESTONEDOJI_indicator": "1mo",
    "CDLHAMMER_indicator": "1mo",
    "CDLHANGINGMAN_indicator": "1mo",
    "CDLHARAMI_indicator": "1mo",
    "CDLHARAMICROSS_indicator": "1mo",
    "CDLHIGHWAVE_indicator": "1mo",
    "CDLHIKKAKE_indicator": "1mo",
    "CDLHIKKAKEMOD_indicator": "1mo",
    "CDLHOMINGPIGEON_indicator": "1mo",
    "CDLIDENTICAL3CROWS_indicator": "1mo",
    "CDLINNECK_indicator": "1mo",
    "CDLINVERTEDHAMMER_indicator": "1mo",
    "CDLKICKING_indicator": "1mo",
    "CDLKICKINGBYLENGTH_indicator": "1mo",
    "CDLLADDERBOTTOM_indicator": "1mo",
    "CDLLONGLEGGEDDOJI_indicator": "1mo",
    "CDLLONGLINE_indicator": "1mo",
    "CDLMARUBOZU_indicator": "1mo",
    "CDLMATCHINGLOW_indicator": "1mo",
    "CDLMATHOLD_indicator": "1mo",
    "CDLMORNINGDOJISTAR_indicator": "1mo",
    "CDLMORNINGSTAR_indicator": "1mo",
    "CDLONNECK_indicator": "1mo",
    "CDLPIERCING_indicator": "1mo",
    "CDLRICKSHAWMAN_indicator": "1mo",
    "CDLRISEFALL3METHODS_indicator": "1mo",
    "CDLSEPARATINGLINES_indicator": "1mo",
    "CDLSHOOTINGSTAR_indicator": "1mo",
    "CDLSHORTLINE_indicator": "1mo",
    "CDLSPINNINGTOP_indicator": "1mo",
    "CDLSTALLEDPATTERN_indicator": "1mo",
    "CDLSTICKSANDWICH_indicator": "1mo",
    "CDLTAKURI_indicator": "1mo",
    "CDLTASUKIGAP_indicator": "1mo",
    "CDLTHRUSTING_indicator": "1mo",
    "CDLTRISTAR_indicator": "1mo",
    "CDLUNIQUE3RIVER_indicator": "1mo",
    "CDLUPSIDEGAP2CROWS_indicator": "1mo",
    "CDLXSIDEGAP3METHODS_indicator": "1mo",
    "BETA_indicator": "1y",
    "CORREL_indicator": "1y",
    "LINEARREG_indicator": "2y",
    "LINEARREG_ANGLE_indicator": "2y",
    "LINEARREG_INTERCEPT_indicator": "2y",
    "LINEARREG_SLOPE_indicator": "2y",
    "STDDEV_indicator": "1mo",
    "TSF_indicator": "2y",
    "VAR_indicator": "2y",
}


def insert_rank_to_coefficient(i):
    try:
        client = MongoClient(os.getenv("mongo_url"))
        db = client.trading_simulator
        collections = db.rank_to_coefficient
        """
        clear all collections entry first and then insert from 1 to i
        """
        collections.delete_many({})
        for i in range(1, i + 1):
            e = math.e
            rate = (e**e) / (e**2) - 1
            coefficient = rate ** (2 * i)
            collections.insert_one({"rank": i, "coefficient": coefficient})
        client.close()
        logging.info("Successfully inserted rank to coefficient")
    except Exception as exception:
        logging.error(exception)


def initialize_rank():
    try:
        client = MongoClient(os.getenv("mongo_url"))

        some_db = client["test"]
        collection = some_db["my_collection"]
        collection.insert_one({"name": "John Doe"})

        db = client.trading_simulator
        collections = db.algorithm_holdings

        initialization_date = datetime.now()

        for strategy in strategies:
            strategy_name = strategy.__name__

            collections = db.algorithm_holdings

            if not collections.find_one({"strategy": strategy_name}):
                collections.insert_one(
                    {
                        "strategy": strategy_name,
                        "holdings": {},
                        "amount_cash": 50000,
                        "initialized_date": initialization_date,
                        "total_trades": 0,
                        "successful_trades": 0,
                        "neutral_trades": 0,
                        "failed_trades": 0,
                        "last_updated": initialization_date,
                        "portfolio_value": 50000,
                    }
                )

                collections = db.points_tally
                collections.insert_one(
                    {
                        "strategy": strategy_name,
                        "total_points": 0,
                        "initialized_date": initialization_date,
                        "last_updated": initialization_date,
                    }
                )

        client.close()
        logging.info("Successfully initialized rank")
    except Exception as exception:
        logging.error(exception)


def initialize_time_delta():
    try:
        client = MongoClient(os.getenv("mongo_url"))
        db = client.trading_simulator
        collection = db.time_delta
        collection.insert_one({"time_delta": 0.01})
        client.close()
        logging.info("Successfully initialized time delta")
    except Exception as exception:
        logging.error(exception)


def initialize_market_setup():
    try:
        client = MongoClient(os.getenv("mongo_url"))
        db = client.market_data
        collection = db.market_status
        collection.insert_one({"market_status": "closed"})
        client.close()
        logging.info("Successfully initialized market setup")
    except Exception as exception:
        logging.error(exception)


def initialize_portfolio_percentages():
    try:
        client = MongoClient(os.getenv("mongo_url"))
        trading_client = TradingClient(os.getenv("API_KEY"), os.getenv("API_SECRET"))
        account = trading_client.get_account()
        db = client.trades
        collection = db.portfolio_values
        portfolio_value = float(account.portfolio_value)
        collection.insert_one(
            {
                "name": "portfolio_percentage",
                "portfolio_value": (portfolio_value - 50000) / 50000,
            }
        )
        collection.insert_one(
            {
                "name": "ndaq_percentage",
                "portfolio_value": (get_latest_price("QQQ") - 503.17) / 503.17,
            }
        )
        collection.insert_one(
            {
                "name": "spy_percentage",
                "portfolio_value": (get_latest_price("SPY") - 590.50) / 590.50,
            }
        )
        client.close()
        logging.info("Successfully initialized portfolio percentages")
    except Exception as exception:
        logging.error(exception)


def initialize_indicator_setup():
    try:
        client = MongoClient(os.getenv("mongo_url"))
        db = client["IndicatorsDatabase"]
        collection = db["Indicators"]

        # Insert indicators into the collection
        for indicator, period in indicator_periods.items():
            collection.insert_one({"indicator": indicator, "ideal_period": period})

        logging.info(
            "Indicators and their ideal periods have been inserted into MongoDB."
        )
    except Exception as e:
        logging.error(e)
        return


def initialize_historical_database_cache():
    try:
        client = MongoClient(os.getenv("mongo_url"))
        db = client["HistoricalDatabase"]
        collection = db["HistoricalDatabase"]
    except Exception as e:
        logging.error(f"Error initializing historical database cache: {e}")
        return


if __name__ == "__main__":
    logging.info("Running main.py")

    insert_rank_to_coefficient(200)

    initialize_rank()

    initialize_time_delta()

    initialize_market_setup()

    initialize_portfolio_percentages()

    initialize_indicator_setup()

    initialize_historical_database_cache()

    with ThreadPoolExecutor() as executor:
        future1 = executor.submit(trading_client_main)
        future2 = executor.submit(ranking_client_main)

        # Optionally, wait for the functions to complete
        future1.result()
        future2.result()
    # async def run_coroutines():
    #     await trading_client_main()
    #     await ranking_client_main()

    # if __name__ == "__main__":
    #     asyncio.run(run_coroutines())
