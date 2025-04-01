import time

from logging import Logger
from typing import Any, Dict, List

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from home_rush.bots.abstract_bot import AbstractHousingBot
from home_rush.data.models import HousingOffer


class PlazaBot(AbstractHousingBot):
  def __init__(self, config: Dict[str, Any], logger: Logger) -> None:
    super().__init__("plaza", config, logger)

  def __del__(self) -> None:
    super().__del__()

  def _generate_location_url(self, location: tuple[str, str]) -> str:
    """Generate a formatted URL based on a given location tuple (city, province).

    Args:
      location (tuple[str, str]): A tuple containing the city and province (e.g., ("Delft", "Zuid-Holland")).

    Returns:
      str: The formatted URL as a string.

    """
    city, province = location
    formatted_location = f"{city}-Nederland%2B-%2B{province}"
    url = f"https://plaza.newnewnew.space/en/availables-places/living-place#?gesorteerd-op=zoekprofiel&locatie={formatted_location}"
    self.logger.info(f"Generated URL for location '{city}, {province}': {url}")
    return url

  def _serialize_str_to_housing_offer(self, input: str) -> HousingOffer:
    """Convert a text string into a structured HousingOffer object.

    This function parses a string representation of a housing offer and extracts
    relevant information such as price, address, property type, size, etc.

    Args:
      input (str): The raw text string containing housing offer information

    Returns:
      HousingOffer: A structured object containing the parsed housing information

    """
    housing_offer = HousingOffer()
    text: str = input.strip().replace("\n", " | ").replace("| |", "|")
    parts: List[str] = text.split(" | ")

    for index, part in enumerate(parts):
      stripped = part.strip()

      if "€" in stripped and "p.m" in stripped:
        try:
          price_str = stripped.replace("€", "").replace("p.m", "").replace(",", "").strip()
          housing_offer.monthly_price = float(price_str)
        except ValueError:
          self.logger.exception("Failed to convert monthly price to float", exc_info=stripped)
      elif "Total rental price:" in stripped:
        try:
          price_str = (
            stripped.replace("Total rental price:", "").replace("€", "").replace(",", "").strip()
          )
          housing_offer.total_price = float(price_str)
        except ValueError:
          self.logger.exception("Failed to convert total price to float", exc_info=stripped)

      elif index == 3:
        address_parts = stripped.split()
        if len(address_parts) > 1:
          number_stripped = address_parts[-1]
          street_stripped = " ".join(address_parts[:-1])
          housing_offer.address.number = number_stripped
          housing_offer.address.street = street_stripped

      elif len(stripped.split()) == 1 and not any(char in stripped for char in "€•m²"):
        housing_offer.address.city = stripped

      elif "•" in stripped:
        segments = stripped.split("•")
        for segment in segments:
          segment = segment.strip()
          if "studio" in segment.lower():
            housing_offer.property_profile.property_type = "Studio"
          elif "apartment" in segment.lower():
            housing_offer.property_profile.property_type = "Apartment"
          elif "room" in segment.lower():
            housing_offer.property_profile.property_type = "Room"
          elif "floor" in segment.lower():
            try:
              floor_text = segment.lower().replace("floor", "").strip()
              floor_number = "".join(filter(str.isdigit, floor_text))
              if floor_number:
                housing_offer.address.floor = int(floor_number)
            except ValueError:
              self.logger.exception("Failed to convert floor to int", exc_info=segment)

      elif "m²" in stripped:
        try:
          housing_offer.property_profile.size = float(stripped.replace("m²", "").strip())
        except ValueError:
          self.logger.exception("Failed to convert size to float", exc_info=stripped)

      elif "responded" in stripped.lower():
        housing_offer.responded = True

    return housing_offer

  def _login(self) -> None:
    """Log in to the website and return the authenticated driver.

    Args:
      config (dict): Configuration dictionary containing login URL, username, password, and Selenium settings.
      logger (Logger): Logger instance for logging messages.

    Raises:
      Exception: If login fails due to element not found or not interactable.

    """
    try:
      self.driver.get(self.config["login"]["url"])

      # Step 1: Accept cookies if the banner is present
      try:
        accept_cookies_button = self.driver.wait_for_element_to_be_clickable(
          By.CSS_SELECTOR, "button#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"
        )
        accept_cookies_button.click()
      except TimeoutException:
        self.logger.warning("Cookies banner not found or already accepted.")

      # Step 2: Click the login button
      try:
        login_button = self.driver.wait_for_element_to_be_clickable(
          By.XPATH,
          "//zds-navigation-link[contains(@class, 'hydrated')]//span[contains(text(), 'Login')] | //zds-navigation-link[contains(@class, 'hydrated')]//zds-icon[@name='person_outline']",
        )
        login_button.click()
      except TimeoutException:
        self.logger.exception("Login button not found or not interactable.")
        raise

      # Step 3: Fill in the username
      try:
        username_field = self.driver.wait_for_element_to_be_visible(By.ID, "username")
        username_field.send_keys(self.config["login"]["username"])
      except TimeoutException:
        self.logger.exception("Username field not found.")
        raise

      # Step 4: Fill in the password
      try:
        password_field = self.driver.wait_for_element_to_be_visible(By.ID, "password")
        password_field.send_keys(self.config["login"]["password"])
      except TimeoutException:
        self.logger.exception("Password field not found.")
        raise

      # Step 5: Submit the form
      try:
        submit_button = self.driver.wait_for_element_to_be_clickable(
          By.CSS_SELECTOR, "input[type='submit']"
        )
        submit_button.click()
      except TimeoutException:
        self.logger.exception("Submit button not found.")
        raise

      # Step 6: Wait for login to complete
      try:
        self.driver.wait_for_url_change(self.config["login"]["url"])
        self.logger.info("Logged in successfully!")
      except TimeoutException:
        self.logger.warning("Login might have failed. Check the page after submission.")
        raise

    except Exception as e:
      self.logger.exception("Login failed", exc_info=e)
      self.driver.quit()
      raise

  def _reply(self, item: WebElement) -> None:
    """Clicks on the item, clicks the "Reply" button, and returns to the original page.

    Args:
      item (WebElement): The web element representing the item to reply to.

    Returns:
      bool: True if the reply was successful, False otherwise.

    """
    try:
      self.driver.scroll_into_view(item)
      time.sleep(1)
      item.click()

      reply_button = self.driver.wait_for_element_to_be_clickable(
        By.CSS_SELECTOR, "input.reageer-button[value='Reply']"
      )
      self.driver.scroll_into_view(reply_button)
      time.sleep(1)
      reply_button.click()

      time.sleep(2)

      self.driver.back()

    except TimeoutException:
      self.logger.exception("Failed to find or click the 'Reply' button")
    except Exception as e:
      self.logger.exception(f"An error occurred while replying: {e}")

    self.driver.back()

  def monitor_and_reply(self) -> None:
    """Monitors the target URL for new items and replies to them."""
    location_url: str = self._generate_location_url(self.config["target"]["city"])
    desired_complexes: List[str] = self.config["target"]["complexes"]
    poll_interval: int = self.config["poll_interval"]

    self.driver.get(location_url)

    while True:
      try:
        list_container = self.driver.wait_for_element_to_be_visible(
          By.CSS_SELECTOR, "div.object-list-items-container"
        )

        raw_items: Any = list_container.find_elements(By.CSS_SELECTOR, "section.list-item")

        new_housing_offers: List[tuple[HousingOffer, Any]] = list(
          filter(
            lambda pair: pair[1].address.street in desired_complexes and not pair[1].responded,
            [
              (raw_item, self._serialize_str_to_housing_offer(raw_item.text))
              for raw_item in raw_items
            ],
          )
        )

        if not new_housing_offers:
          self.logger.info("No new offers found")
        else:
          self.logger.info("Found %d new offers", len(new_housing_offers))
          for raw_item, offer in new_housing_offers:
            try:
              self._reply(raw_item)
              offer.responded = True
              self.logger.info("Replied to offer", exc_info=offer)
            except TimeoutException:
              self.logger.exception("Failed to reply to offer", exc_info=offer)
            except Exception as e:
              self.logger.exception("An error occurred while replying", exc_info=e)

      except TimeoutException:
        self.logger.warning("List container or items not found on the page")
      except NoSuchElementException:
        self.logger.warning("List container or items not found on the page")

      time.sleep(poll_interval)
      self.driver.refresh()
      self.logger.info("Page refreshed")
