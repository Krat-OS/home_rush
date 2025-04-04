"""Abstract class for housing bots."""

from logging import Logger
from typing import Any, Dict

from selenium.webdriver.remote.webelement import WebElement

from home_rush.data.models import HousingOffer
from home_rush.utils.web_driver_adapter import WebDriverAdapter


class AbstractHousingBot:
  """Abstract class for housing bots."""

  def __init__(self, bot_name: str, config: Dict[str, Any], logger: Logger) -> None:
    """Initialize the bot with a configuration and a logger.

    Args:
      config (Dict[str, Any]): The configuration for the bot.
      logger (Logger): The logger for the bot.

    """
    self.driver = WebDriverAdapter(config["selenium"])
    self.config = config[bot_name]
    self.logger = logger

  def __del__(self) -> None:
    """Destructor for the bot."""
    self.driver.quit()

  def _serialize_str_to_housing_offer(self, input: str) -> HousingOffer:
    """Serialize a string to a HousingOffer object.

    Args:
      input (str): The string to serialize.

    Returns:
      HousingOffer: The serialized HousingOffer object.

    """
    raise NotImplementedError

  def _login(self) -> None:
    """Login to the website.

    Returns:
      None

    """
    raise NotImplementedError

  def _reply(self, item: WebElement) -> bool:
    """Reply to an item.

    Args:
      item (WebElement): The item to reply to.

    Returns:
      bool: True if the reply was successful, False otherwise.

    """
    raise NotImplementedError

  def _monitor_and_reply(self) -> None:
    """Monitor the website and reply to new items.

    Returns:
      None

    """
    raise NotImplementedError

  def run_bot(self) -> None:
    """Run the bot."""
    raise NotImplementedError
