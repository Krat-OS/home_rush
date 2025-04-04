from concurrent.futures import Future, ThreadPoolExecutor
from logging import Logger
from typing import Any, Dict, List

import yaml

from home_rush.bots.abstract_bot import AbstractHousingBot
from home_rush.bots.holland2stay_bot import Holland2StayBot
from home_rush.bots.plaza_bot import PlazaBot
from home_rush.utils.logging import setup_logging


def load_config() -> Dict[str, Any]:
  """Load configuration from config.yaml."""
  with open("config.yaml", encoding="utf-8") as file:
    return yaml.safe_load(file)


def main() -> None:
  logger: Logger = setup_logging()
  config: Dict[str, Any] = load_config()

  executor: ThreadPoolExecutor = ThreadPoolExecutor()
  futures: List[Future[None]] = []
  bots: List[AbstractHousingBot] = []

  try:
    if config.get("plaza"):
      bots.append(PlazaBot(config, logger))

    if config.get("holland2stay"):
      bots.append(Holland2StayBot(config, logger))

    if not bots:
      raise ValueError("No bot configured")

    for bot in bots:
      futures.append(executor.submit(bot.run))

    for future in futures:
      future.result()

  except KeyboardInterrupt:
    logger.info("Keyboard interrupt received. Shutting down gracefully...")
    for future in futures:
      if not future.done():
        future.cancel()
  except Exception as e:
    logger.exception("An error occurred", exc_info=e)
  finally:
    logger.info("Cleaning up resources...")
    for bot in bots:
      del bot
    executor.shutdown(wait=False)
    logger.info("Shutdown complete")


if __name__ == "__main__":
  main()
