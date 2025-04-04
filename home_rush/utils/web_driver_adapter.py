from typing import Any, Dict, List

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class WebDriverAdapter:
  """A wrapper class for Selenium WebDriver to provide additional utility methods
  and manage browser interactions based on a given configuration.

  Attributes:
    driver (webdriver.Chrome): The Selenium WebDriver instance used for browser automation.

  """

  def __init__(self, config: Dict[str, Any]):
    """Initialize the WebDriverAdapter with a configuration dictionary.

    Args:
      config (Dict[str, Any]): A dictionary containing configuration settings for Selenium WebDriver.

    Sets up the Chrome WebDriver with specified options based on the configuration.

    """
    options = webdriver.ChromeOptions()
    if config["headless"]:
      options.add_argument("--headless")
      options.add_argument("--no-sandbox")
      options.add_argument("--disable-dev-shm-usage")
      options.add_argument("--disable-gpu")
      options.add_argument("--remote-debugging-port=9222")
      options.add_argument("--disable-setuid-sandbox")
      options.add_argument("--disable-software-rasterizer")
      options.add_argument("--disable-extensions")

    self.driver = webdriver.Chrome(options=options)

  def get(self, url: str) -> None:
    """Navigate to a specified URL using the WebDriver.

    Args:
      url (str): The URL to navigate to.

    """
    self.driver.get(url)

  def find_element(self, by: By, value: str) -> WebElement:
    """Find a single web element on the page.

    Args:
      by (By): The method to locate the element (e.g., By.ID, By.XPATH).
      value (str): The value to search for using the specified method.

    Returns:
      WebElement: The located web element.

    """
    return self.driver.find_element(by, value)

  def find_elements(self, by: By, value: str) -> List[WebElement]:
    """Find multiple web elements on the page.

    Args:
      by (By): The method to locate the elements (e.g., By.CLASS_NAME, By.CSS_SELECTOR).
      value (str): The value to search for using the specified method.

    Returns:
      List[WebElement]: A list of located web elements.

    """
    return self.driver.find_elements(by, value)

  def wait_for_url_change(self, url: str) -> None:
    """Wait until the current URL changes from the specified URL.

    Args:
      url (str): The URL to wait for a change from.

    """
    WebDriverWait(self.driver, 10).until(EC.url_changes(url))

  def wait_for_element_to_be_visible(self, by: By, value: str) -> WebElement:
    """Wait until a web element is visible.

    Args:
      by (By): The method to locate the element (e.g., By.ID, By.XPATH).
      value (str): The value to search for using the specified method.

    Returns:
      WebElement: The web element once it is visible.

    """
    return WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((by, value)))

  def is_element_on_screen(self, by: By, value: str) -> bool:
    """Check if a web element is on the screen.

    Args:
      by (By): The method to locate the element (e.g., By.ID, By.XPATH).
      value (str): The value to search for using the specified method.

    Returns:
      bool: True if the element is on the screen, False otherwise.

    """
    try:
      WebDriverWait(self.driver, 2).until(EC.visibility_of_element_located((by, value)))
      return True
    except TimeoutException:
      return False

  def wait_for_element_to_be_clickable(self, by: By, value: str) -> WebElement:
    """Wait until a web element is clickable.

    Args:
      by (By): The method to locate the element (e.g., By.LINK_TEXT, By.TAG_NAME).
      value (str): The value to search for using the specified method.

    Returns:
      WebElement: The web element once it is clickable.

    """
    return WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((by, value)))

  def scroll_into_view(self, element: WebElement) -> None:
    """Scroll the browser window to bring the specified element into view.

    Args:
      element (WebElement): The web element to scroll into view.

    """
    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

  def back(self) -> None:
    """Navigate back to the previous page in the browser history."""
    self.driver.back()

  def quit(self) -> None:
    """Quit the WebDriver and close all associated browser windows."""
    self.driver.quit()

  def refresh(self) -> None:
    """Refresh the current page in the browser."""
    self.driver.refresh()
