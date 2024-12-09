# utils/logger.py
import logging
from config import LOG_FILE, LOG_LEVEL

logger = logging.getLogger("IntelligentAggregator")
logger.setLevel(LOG_LEVEL)
fh = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.propagate = False
