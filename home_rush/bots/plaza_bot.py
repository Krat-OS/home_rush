import time

from logging import Logger
from typing import Any, Callable, Dict, List, Tuple

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
    url = f"https://plaza.newnewnew.space/aanbod/wonen#?gesorteerd-op=zoekprofiel&locatie={formatted_location}"
    self.logger.info("Generated URL for location '%s, %s': %s", city, province, url)
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

      if "€" in stripped and "p/m" in stripped:
        try:
          price_str: str = stripped.replace("€", "").replace("p/m", "").replace(",", ".").strip()
          housing_offer.monthly_price = float(price_str)
        except ValueError:
          self.logger.exception("Failed to convert monthly price to float", exc_info=stripped)
      elif "Totale huurprijs:" in stripped:
        try:
          price_str: str = (
            stripped.replace("Totale huurprijs:", "").replace("€", "").replace(",", ".").strip()
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
        segments: List[str] = stripped.split("•")
        for segment in segments:
          inner_segment: str = segment.strip()
          if "studio" in inner_segment.lower():
            housing_offer.property_profile.property_type = "Studio"
          elif "apartment" in inner_segment.lower():
            housing_offer.property_profile.property_type = "Apartment"
          elif "room" in inner_segment.lower():
            housing_offer.property_profile.property_type = "Room"
          elif "floor" in inner_segment.lower():
            try:
              floor_text: str = inner_segment.lower().replace("e verdieping", "").strip()
              floor_number: str = "".join(filter(str.isdigit, floor_text))
              if floor_number:
                housing_offer.address.floor = int(floor_number)
            except ValueError:
              self.logger.exception("Failed to convert floor to int", exc_info=inner_segment)

      elif "m²" in stripped:
        try:
          housing_offer.property_profile.size = float(stripped.replace("m²", "").strip())
        except ValueError:
          self.logger.exception("Failed to convert size to float", exc_info=stripped)

      elif "responded" in stripped.lower():
        housing_offer.responded = True

    return housing_offer

  def _parse_filters(self, config: Dict[str, Any]) -> Dict[str, Callable[[HousingOffer], bool]]:
    """Parse filter configurations and return a dictionary of filter functions.

    Args:
        config: The configuration dictionary containing filter specifications

    Returns:
        Dictionary of named filter functions that each take an offer and return a boolean

    """
    filters: Dict[str, Callable[[HousingOffer], bool]] = {}

    filter_config: Dict[str, Any] = config.get("target", {}).get("filters", {})

    if "complexes" in filter_config:
      complexes: List[str] = filter_config["complexes"]
      if complexes:

        def complexes_filter(offer: HousingOffer) -> bool:
          return offer.address.street in complexes

        filters["complexes"] = complexes_filter

    field_mapping = {
      "rent": "monthly_price",
      "total_rent": "total_price",
      "floor": "address.floor",
      "size": "property_profile.size",
    }

    for config_field, obj_field in field_mapping.items():
      if config_field in filter_config:
        field_config: Dict[str, Any] = filter_config[config_field]

        if "eq" in field_config:
          value: Any = field_config["eq"]

          def eq_filter(offer: HousingOffer, field_path: str = obj_field, val: Any = value) -> bool:
            if "." in field_path:
              parts = field_path.split(".")
              attr = getattr(offer, parts[0])
              return getattr(attr, parts[1]) == val
            return getattr(offer, field_path) == val

          filters[f"{config_field}_eq"] = eq_filter

        if "min" in field_config:
          min_value: Any = field_config["min"]

          def min_filter(
            offer: HousingOffer, field_path: str = obj_field, val: Any = min_value
          ) -> bool:
            if "." in field_path:
              parts = field_path.split(".")
              attr = getattr(offer, parts[0])
              return getattr(attr, parts[1]) >= val
            return getattr(offer, field_path) >= val

          filters[f"{config_field}_min"] = min_filter

        if "max" in field_config:
          max_value: Any = field_config["max"]

          def max_filter(
            offer: HousingOffer, field_path: str = obj_field, val: Any = max_value
          ) -> bool:
            if "." in field_path:
              parts = field_path.split(".")
              attr = getattr(offer, parts[0])
              return getattr(attr, parts[1]) <= val
            return getattr(offer, field_path) <= val

          filters[f"{config_field}_max"] = max_filter

    return filters

  @staticmethod
  def _apply_filters(
    items: List[Tuple[WebElement, HousingOffer]], filters: Dict[str, Callable[[HousingOffer], bool]]
  ) -> List[Tuple[WebElement, HousingOffer]]:
    """Apply the provided filters to the list of items.

    Args:
        items: List of tuples containing raw elements and their corresponding offer objects
        filters: Dictionary of filter functions to apply

    Returns:
        Filtered list of item pairs that match all criteria

    """
    result: List[Tuple[WebElement, HousingOffer]] = []

    for raw_item, offer in items:
      if offer.responded:
        continue

      matches: bool = True
      for filter_func in filters.values():
        try:
          if not filter_func(offer):
            matches = False
            break
        except (AttributeError, TypeError):
          matches = False
          break

      if matches:
        result.append((raw_item, offer))

    return result

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
          "//zds-navigation-link[contains(@class, 'hydrated')]//span[contains(text(), 'Inloggen')] | //zds-navigation-link[contains(@class, 'hydrated')]//zds-icon[@name='person_out  line']",
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

      time.sleep(1)

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

  def _reply(self, item: WebElement, offer: HousingOffer) -> None:
    """Clicks on the item, clicks the "Reply" button, and returns to the original page.

    Args:
      item (WebElement): The web element representing the item to reply to.
      offer (HousingOffer): The offer object to reply to.

    Returns:
      bool: True if the reply was successful, False otherwise.

    """
    try:
      self.driver.scroll_into_view(item)
      time.sleep(1)
      item.click()

      reply_button = self.driver.wait_for_element_to_be_clickable(
        By.CSS_SELECTOR, "input.reageer-button[value='Reageer']"
      )
      self.driver.scroll_into_view(reply_button)
      time.sleep(1)
      reply_button.click()

      self.logger.info("Replied to offer: %s", offer)

      time.sleep(2)

    except TimeoutException:
      self.logger.exception("Failed to find or click the 'Reply' button")
      raise
    finally:
      self.driver.back()

  def _monitor_and_reply(self) -> None:
    """Monitor the target URL for new items and replies to them."""
    location_url: str = self._generate_location_url(self.config["target"]["city"])
    filters: Dict[str, Callable[[HousingOffer], bool]] = self._parse_filters(self.config)
    self.logger.info("Filters: %s", ", ".join(filters.keys()))
    poll_interval: int = self.config["poll_interval"]

    self.driver.get(location_url)

    while True:
      if self.driver.is_element_on_screen(
        By.CSS_SELECTOR, "div.icon-br_sad.empty-state-icon + div.empty-state-text h2.ng-binding"
      ):
        self.logger.info("No new offers found")
      else:
        try:
          list_container = self.driver.wait_for_element_to_be_visible(
            By.CSS_SELECTOR, "div.object-list-items-container"
          )

          raw_items: List[WebElement] = list_container.find_elements(
            By.CSS_SELECTOR, "section.list-item"
          )

          item_offer_pairs: List[Tuple[WebElement, Any]] = [
            (raw_item, self._serialize_str_to_housing_offer(raw_item.text))
            for raw_item in raw_items
          ]

          new_housing_offers: List[Tuple[WebElement, Any]] = self._apply_filters(
            item_offer_pairs, filters
          )

          if not new_housing_offers:
            self.logger.info("No new offers found")
          else:
            self.logger.info("Found %d new offers", len(new_housing_offers))
            for raw_item, offer in new_housing_offers:
              try:
                self._reply(raw_item, offer)
              except TimeoutException:
                self.logger.exception("Failed to reply to offer: %s", offer)

        except TimeoutException:
          self.logger.warning("List container or items not found on the page")
        except NoSuchElementException:
          self.logger.warning("List container or items not found on the page")

      time.sleep(poll_interval)
      self.driver.get(location_url)
      self.logger.info("Page refreshed")

  def run_bot(self) -> None:
    """Run the bot."""
    try:
      self._login()
      self._monitor_and_reply()
    except Exception as e:
      self.logger.exception("An error occurred", exc_info=e)
