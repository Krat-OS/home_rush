from concurrent.futures import ThreadPoolExecutor
from logging import Logger, getLogger
from typing import Any, Dict, Type

import yaml

from home_rush.bots.abstract_bot import AbstractHousingBot
from home_rush.bots.holland2stay_bot import Holland2StayBot
from home_rush.bots.plaza_bot import PlazaBot
from home_rush.utils.logging import setup_logging


def _run_bot(bot_class: Type[AbstractHousingBot], config: Dict[str, Any], logger: Logger) -> None:
  bot = bot_class(config, logger)
  try:
    bot.monitor_and_reply()
  except Exception as e:
    logger.exception("An error occurred", exc_info=e)
  finally:
    del bot


def _execute_bots_in_parallel(config: Dict[str, Any], logger: Logger) -> None:
  with ThreadPoolExecutor() as executor:
    futures = []
    if config.get("plaza"):
      futures.append(executor.submit(_run_bot, PlazaBot, config, logger))
    if config.get("holland2stay"):
      futures.append(executor.submit(_run_bot, Holland2StayBot, config, logger))
    if not futures:
      raise ValueError("No bot configured")
    for future in futures:
      future.result()


def load_config() -> Dict[str, Any]:
  """Load configuration from config.yaml."""
  with open("config.yaml", encoding="utf-8") as file:
    return yaml.safe_load(file)


def main() -> None:
  """Main entry point of the bot."""
  setup_logging()
  logger: Logger = getLogger(__name__)
  config: Dict[str, Any] = load_config()
  _execute_bots_in_parallel(config, logger)


if __name__ == "__main__":
  main()
