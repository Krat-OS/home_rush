import logging

from typing import Any, Dict

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def login(config: Dict[str, Any], logger: logging.Logger) -> webdriver.Chrome:
  """Log in to the website and return the authenticated driver.

  Args:
    config (dict): Configuration dictionary containing login URL, username, password, and Selenium settings.

  Returns:
    webdriver.Chrome: Authenticated WebDriver instance.

  Raises:
    Exception: If login fails due to element not found or not interactable.

  """
  options = webdriver.ChromeOptions()
  if config["selenium"]["headless"]:
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-extensions")

  driver = webdriver.Chrome(options=options)

  try:
    driver.get(config["login"]["url"])

    # Step 1: Accept cookies if the banner is present
    try:
      accept_cookies_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
          (By.CSS_SELECTOR, "button#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
        )
      )
      accept_cookies_button.click()
    except TimeoutException:
      logger.warning("Cookies banner not found or already accepted.")

    # Step 2: Click the login button
    try:
      login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
          (
            By.XPATH,
            "//zds-navigation-link[contains(@class, 'hydrated')]//span[contains(text(), 'Login')] | //zds-navigation-link[contains(@class, 'hydrated')]//zds-icon[@name='person_outline']",
          )
        )
      )
      login_button.click()
    except TimeoutException:
      logger.error("Login button not found or not interactable.")
      raise

    # Step 3: Fill in the username
    try:
      username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
      )
      username_field.send_keys(config["login"]["username"])
    except TimeoutException:
      logger.error("Username field not found.")
      raise

    # Step 4: Fill in the password
    try:
      password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "password"))
      )
      password_field.send_keys(config["login"]["password"])
    except TimeoutException:
      logger.error("Password field not found.")
      raise

    # Step 5: Submit the form
    try:
      submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
      )
      submit_button.click()
    except TimeoutException:
      logger.error("Submit button not found.")
      raise

    # Step 6: Wait for login to complete
    try:
      WebDriverWait(driver, 10).until(EC.url_changes(config["login"]["url"]))
      logger.info("Logged in successfully!")
    except TimeoutException:
      logger.warning("Login might have failed. Check the page after submission.")
      raise

    return driver

  except Exception as e:
    logger.error(f"Login failed: {e}")
    driver.quit()
    raise
