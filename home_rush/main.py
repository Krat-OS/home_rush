from concurrent.futures import Future, ThreadPoolExecutor
from logging import Logger
from typing import Any, Dict, List

import yaml

from home_rush.bots.holland2stay_bot import Holland2StayBot
from home_rush.bots.plaza_bot import PlazaBot
from home_rush.utils.logging import setup_logging


def load_config() -> Dict[str, Any]:
  """Load configuration from config.yaml."""
  with open("config.yaml", encoding="utf-8") as file:
    return yaml.safe_load(file)


def main() -> None:
  """Main entry point of the bot."""
  logger: Logger = setup_logging()
  config: Dict[str, Any] = load_config()
  with ThreadPoolExecutor() as executor:
    futures: List[Future[None]] = []
    if config.get("plaza"):
      futures.append(executor.submit(PlazaBot(config, logger).run_bot))
    if config.get("holland2stay"):
      futures.append(executor.submit(Holland2StayBot(config, logger).run_bot))
    if not futures:
      raise ValueError("No bot configured")
    for future in futures:
      future.result()


if __name__ == "__main__":
  main()
