import logging
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_logger():
    return logging.getLogger()

logger = get_logger()
