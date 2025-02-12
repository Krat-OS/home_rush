import logging

from typing import Any, Dict

import yaml

from plaza_bot.logging import setup_logging
from plaza_bot.login import login
from plaza_bot.monitor_and_reply import monitor_and_reply

setup_logging()
logger: logging.Logger = logging.getLogger(__name__)


def load_config() -> Dict[str, Any]:
  """Load configuration from config.yaml."""
  with open("config.yaml", encoding="utf-8") as file:
    return yaml.safe_load(file)


def main() -> None:
  """Main entry point of the bot.
  """
  config: Dict[str, Any] = load_config()
  driver = login(config, logger)

  try:
    monitor_and_reply(config, driver, logger)
  except Exception as e:
    logger.error(f"An error occurred: {e}")
  finally:
    driver.quit()


if __name__ == "__main__":
  main()
