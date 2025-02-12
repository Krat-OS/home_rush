import logging

from colorama import Fore, Style, init

init(autoreset=True)


class ColoredFormatter(logging.Formatter):
  """Custom logging formatter with colored output."""

  # Define log level colors
  LOG_COLORS = {
    logging.INFO: Fore.GREEN,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
  }

  def format(self, record):
    # Add color to the log level
    log_level_color = self.LOG_COLORS.get(record.levelno, Fore.WHITE)
    log_level_name = log_level_color + record.levelname + Style.RESET_ALL

    # Format the log message
    log_message = super().format(record)
    return f"{self.formatTime(record, '%H:%M:%S')} | {log_level_name} | {log_message}"


def setup_logging():
  """Set up logging with a custom formatter."""
  # Create a logger
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)

  # Create a console handler
  console_handler = logging.StreamHandler()
  console_handler.setLevel(logging.INFO)

  # Set the custom formatter
  formatter = ColoredFormatter("%(message)s")
  console_handler.setFormatter(formatter)

  # Add the handler to the logger
  logger.addHandler(console_handler)
