import logging
from pymongo import MongoClient
from datetime import datetime
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

try:
    logger.info("Connecting to MongoDB...")
    client = MongoClient(os.getenv("mongo_url"))
    db = client.trading_simulator

    logger.info("Fetching points tally...")
    points_collection = db.points_tally
    points_data = list(points_collection.find())

    logger.info("Fetching algorithm holdings...")
    holdings_collection = db.algorithm_holdings
    holdings_data = list(holdings_collection.find())

    logger.info("Fetching rankings...")
    rank_collection = db.rank
    rank_data = list(rank_collection.find())

    logging.info("\nStrategy Points:")
    logging.info("-" * 80)
    for strategy in sorted(points_data, key=lambda x: x["total_points"], reverse=True):
        last_updated = strategy.get("last_updated", datetime.now())
        logging.info(
            f"{strategy['strategy']:<40} {strategy['total_points']:>10.2f} points  (Updated: {last_updated})"
        )

    logging.info("\nStrategy Rankings:")
    logging.info("-" * 80)
    sorted_strategies = sorted(
        points_data, key=lambda x: x["total_points"], reverse=True
    )
    for i, strategy in enumerate(sorted_strategies, 1):
        logging.info(f"Rank {i}: {strategy['strategy']}")

    logging.info("\nSummary Statistics:")
    logging.info("-" * 80)
    total_portfolio_value = sum(s.get("portfolio_value", 0) for s in holdings_data)
    total_cash = sum(s["amount_cash"] for s in holdings_data)
    total_trades = sum(s["total_trades"] for s in holdings_data)
    total_successful = sum(s["successful_trades"] for s in holdings_data)
    total_failed = sum(s.get("failed_trades", 0) for s in holdings_data)
    total_neutral = sum(s.get("neutral_trades", 0) for s in holdings_data)

    logging.info(f"Total Portfolio Value: ${total_portfolio_value:,.2f}")
    logging.info(f"Total Cash: ${total_cash:,.2f}")
    logging.info(f"Total Trades: {total_trades}")
    logging.info(f"Total Successful Trades: {total_successful}")
    logging.info(f"Total Failed Trades: {total_failed}")
    logging.info(f"Total Neutral Trades: {total_neutral}")
    if total_trades > 0:
        success_rate = (total_successful / total_trades) * 100
        logging.info(f"Overall Success Rate: {success_rate:.1f}%")

except Exception as e:
    logger.error(f"Error: {str(e)}")
finally:
    client.close()
