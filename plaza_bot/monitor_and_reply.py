import logging
import time

from typing import Any, Dict, Set

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def reply(driver: Chrome, item, logger: logging.Logger) -> bool:
  """Clicks on the item, clicks the "Reply" button, and returns to the original page.

  Args:
    driver (Chrome): The Selenium WebDriver instance.
    item: The web element representing the item to reply to.
    logger (logging.Logger): The logger instance for logging messages.

  Returns:
    bool: True if the reply was successful, False otherwise.
  """
  try:
    driver.execute_script("arguments[0].scrollIntoView(true);", item)
    time.sleep(1)
    item.click()
    logger.info("Clicked on the item to open details")

    reply_button = WebDriverWait(driver, 10).until(
      EC.element_to_be_clickable((By.CSS_SELECTOR, "input.reageer-button[value='Reply']"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", reply_button)
    time.sleep(1)
    reply_button.click()
    logger.info("Clicked the 'Reply' button")

    time.sleep(2)

    driver.back()
    logger.info("Returned to the original page")
    return True

  except TimeoutException:
    logger.error("Failed to find or click the 'Reply' button")
  except Exception as e:
    logger.error(f"An error occurred while replying: {e}")

  driver.back()
  logger.info("Returned to the original page after failure")
  return False  # Reply failed


def monitor_and_reply(config: Dict[str, Any], driver: Chrome, logger: logging.Logger) -> None:
  """Monitors the target URL for new items and replies to them.

  Args:
    config (Dict[str, Any]): Configuration dictionary containing target URL and poll interval.
    driver (Chrome): The Selenium WebDriver instance.
    logger (logging.Logger): The logger instance for logging messages.

  """
  target_url: str = config["target"]["url"]
  poll_interval: int = config["selenium"]["poll_interval"]
  seen_items: Set[str] = set()

  driver.get(target_url)
  logger.info(f"Navigated to {target_url}")

  while True:
    try:
      list_container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.object-list-items-container"))
      )
      logger.info("List container found")

      WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "section.list-item"))
      )
      items = list_container.find_elements(By.CSS_SELECTOR, "section.list-item")

      logger.info(f"Found {len(items)} items in the list")

      new_items = []
      for item in items:
        item_text: str = item.text.strip().replace("\n", " | ").replace("|  |", "|")
        if item_text not in seen_items:
          seen_items.add(item_text)
          new_items.append(item_text)
          logger.info(f"New list item: {item_text}")

          if not reply(driver, item, logger):
            logger.info("Reply failed, marking item as seen and skipping in the future")
          else:
            logger.info("Replied successfully")

      if not new_items:
        logger.info("No new items found")

    except TimeoutException:
      logger.warning("List container or items not found on the page")
    except NoSuchElementException:
      logger.warning("List container or items not found on the page")

    time.sleep(poll_interval)
    driver.refresh()
    logger.info("Page refreshed")
