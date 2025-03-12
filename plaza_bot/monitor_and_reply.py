import time

from logging import Logger
from typing import Any, Dict, List

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from plaza_bot.models import HousingOffer
from plaza_bot.utils import serialize_str_to_housing_offer, generate_location_url


def reply(driver: Chrome, item, logger: Logger) -> bool:
  """Clicks on the item, clicks the "Reply" button, and returns to the original page.

  Args:
    driver (Chrome): The Selenium WebDriver instance.
    item: The web element representing the item to reply to.
    logger (Logger): The logger instance for logging messages.

  Returns:
    bool: True if the reply was successful, False otherwise.

  """
  try:
    driver.execute_script("arguments[0].scrollIntoView(true);", item)
    time.sleep(1)
    item.click()

    reply_button = WebDriverWait(driver, 10).until(
      EC.element_to_be_clickable((By.CSS_SELECTOR, "input.reageer-button[value='Reply']"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", reply_button)
    time.sleep(1)
    reply_button.click()

    time.sleep(2)

    driver.back()
    return True

  except TimeoutException:
    logger.error("Failed to find or click the 'Reply' button")
  except Exception as e:
    logger.error(f"An error occurred while replying: {e}")

  driver.back()
  return False


def monitor_and_reply(config: Dict[str, Any], driver: Chrome, logger: Logger) -> None:
  """Monitors the target URL for new items and replies to them.

  Args:
    config (Dict[str, Any]): Configuration dictionary containing target URL and poll interval.
    driver (Chrome): The Selenium WebDriver instance.
    logger (.Logger): The logger instance for logging messages.

  """
  location_url: str = generate_location_url(config["target"]["city"], logger)
  desired_complexes: List[str] = config["target"]["complexes"]
  poll_interval: int = config["selenium"]["poll_interval"]

  driver.get(location_url)

  while True:
    try:
      list_container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.object-list-items-container"))
      )

      WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "section.list-item"))
      )
      raw_items: Any = list_container.find_elements(By.CSS_SELECTOR, "section.list-item")

      new_housing_offers: List[tuple[HousingOffer, Any]] = list(filter(
        lambda pair: pair[1].address.street in desired_complexes and not pair[1].responded,
        [(raw_item, serialize_str_to_housing_offer(raw_item.text, logger)) for raw_item in raw_items]
      ))

      if not new_housing_offers:
        logger.info("No new offers found")
      else:
        logger.info(f"Found {len(new_housing_offers)} new offers")
        for raw_item, offer in new_housing_offers:
          if reply(driver, raw_item, logger):
            offer.responded = True
            logger.info(f"Replied to offer: {offer}")
          else:
            logger.error(f"Failed to reply to offer: {offer}")

    except TimeoutException:
      logger.warning("List container or items not found on the page")
    except NoSuchElementException:
      logger.warning("List container or items not found on the page")

    time.sleep(poll_interval)
    driver.refresh()
    logger.info("Page refreshed")
