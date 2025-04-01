from logging import Logger
from typing import Any, Dict

from selenium.webdriver.remote.webelement import WebElement

from home_rush.bots.abstract_bot import AbstractHousingBot


class Holland2StayBot(AbstractHousingBot):
  def __init__(self, config: Dict[str, Any], logger: Logger):
    super().__init__("holland2stay", config, logger)

  def __del__(self):
    super().__del__()

  def _login(self) -> None:
    pass

  def _reply(self, item: WebElement) -> bool:
    pass

  def monitor_and_reply(self) -> None:
    pass
