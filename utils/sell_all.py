from alpaca.trading.client import TradingClient
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def sell_all_positions():
    trading_client = TradingClient(os.getenv("API_KEY"), os.getenv("API_SECRET"))

    try:
        positions = trading_client.get_all_positions()

        if not positions:
            logging.info("No open positions found.")
            return

        for position in positions:
            try:
                logging.info(
                    f"Closing position for {position.symbol} (Quantity: {position.qty})"
                )
                trading_client.close_position(position.symbol)
                logging.info(f"Successfully closed position for {position.symbol}")
            except Exception as e:
                logging.error(f"Error closing position for {position.symbol}: {e}")

        logging.info("All positions have been closed.")

    except Exception as e:
        logging.error(f"Error getting positions: {e}")


if __name__ == "__main__":
    sell_all_positions()
