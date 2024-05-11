# logger_config.py
import logging


# Create and configure the shared logger
def setup_logger() -> logging.Logger:
    """Set up and return a singleton logger instance."""
    # Check if the logger already exists
    logger = logging.getLogger("shared_logger")
    if not logger.hasHandlers():  # To prevent duplicate handlers
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Create a file handler
        file_handler = logging.FileHandler("app.log")
        file_handler.setFormatter(formatter)

        # Create a console handler (optional)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# Initialize the shared logger
shared_logger = setup_logger()
