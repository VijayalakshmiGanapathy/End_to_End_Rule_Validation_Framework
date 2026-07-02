import logging

logger = logging.getLogger(__name__)

def info(message):
    logger.info(message)

def success(message):
    logger.info(f"SUCCESS | {message}")

def warning(message):
    logger.warning(message)

def error(message):
    logger.error(message)