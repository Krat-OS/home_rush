from logging import Logger
from typing import List
import urllib.parse

from plaza_bot.models import HousingOffer

def generate_location_url(location: tuple[str, str], logger: Logger) -> str:
  """Generate a formatted URL based on a given location tuple (city, province).
  
  Args:
    location (tuple[str, str]): A tuple containing the city and province (e.g., ("Delft", "Zuid-Holland")).
    logger (Logger): Logger instance for recording log messages.
  
  Returns:
    str: The formatted URL as a string.
  """
  city, province = location
  formatted_location = f"{city}-Nederland%2B-%2B{province}"
  url = f"https://plaza.newnewnew.space/en/availables-places/living-place#?gesorteerd-op=zoekprofiel&locatie={formatted_location}"
  logger.info(f"Generated URL for location '{city}, {province}': {url}")
  return url


def serialize_str_to_housing_offer(input: str, logger: Logger) -> HousingOffer:
  """Convert a text string into a structured HousingOffer object.
  This function parses a string representation of a housing offer and extracts
  relevant information such as price, address, property type, size, etc.

  Args:
    input (str): The raw text string containing housing offer information
    logger (Logger): Logger object for recording errors during parsing
  Returns:
    HousingOffer: A structured object containing the parsed housing information

  """
  housing_offer = HousingOffer()
  text: str = input.strip().replace("\n", " | ").replace("| |", "|")
  parts: List[str] = text.split(" | ")
  
  print(parts)

  for index, part in enumerate(parts):
    stripped = part.strip()

    if "€" in stripped and "p.m" in stripped:
      try:
        price_str = stripped.replace("€", "").replace("p.m", "").replace(",", "").strip()
        housing_offer.monthly_price = float(price_str)
      except ValueError:
        logger.error(f"Failed to convert monthly price to float: {stripped}")
    elif "Total rental price:" in stripped:
      try:
        price_str = stripped.replace("Total rental price:", "").replace("€", "").replace(",", "").strip()
        housing_offer.total_price = float(price_str)
      except ValueError:
        logger.error(f"Failed to convert total price to float: {stripped}")

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
            floor_number = ''.join(filter(str.isdigit, floor_text))
            if floor_number:
              housing_offer.address.floor = int(floor_number)
          except ValueError:
            logger.error(f"Failed to convert floor to int: {segment}")

    elif "m²" in stripped:
      try:
        housing_offer.property_profile.size = float(stripped.replace("m²", "").strip())
      except ValueError:
        logger.error(f"Failed to convert size to float: {stripped}")

    elif "responded" in stripped.lower():
      housing_offer.responded = True

  return housing_offer
