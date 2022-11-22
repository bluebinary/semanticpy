import logging

logger = logging.getLogger("semanticpy")
logger.addHandler(logging.StreamHandler())
logger.setLevel(level=logging.WARN)
logger.propagate = False
