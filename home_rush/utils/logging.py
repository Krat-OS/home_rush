import logging

from colorama import Fore, Style, init

init(autoreset=True)


class ColoredFormatter(logging.Formatter):
  """Custom logging formatter with colored output."""

  LOG_COLORS = {
    logging.INFO: Fore.GREEN,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
  }

  def format(self, record):
    log_level_color = self.LOG_COLORS.get(record.levelno, Fore.WHITE)
    log_level_name = log_level_color + record.levelname + Style.RESET_ALL

    log_message = super().format(record)
    return f"{self.formatTime(record, '%H:%M:%S')} | {log_level_name} | {log_message}"


def setup_logging() -> logging.Logger:
  """Set up logging with a custom formatter."""
  logger = logging.getLogger(__name__)
  logger.setLevel(logging.INFO)

  console_handler = logging.StreamHandler()
  console_handler.setLevel(logging.INFO)

  formatter = ColoredFormatter("%(message)s")
  console_handler.setFormatter(formatter)

  logger.addHandler(console_handler)

  return logger
