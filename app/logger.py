import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger():
    # Create a custom logger
    logger = logging.getLogger('app')
    logger.setLevel(logging.DEBUG)  # Set the logging level

    # Create handlers
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler('app.log', maxBytes=2000, backupCount=10)
    file_handler.setLevel(logging.ERROR)

    # Create formatters and add them to handlers
    console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# Initialize the logger
logger = setup_logger()
