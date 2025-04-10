import logging

logger = logging.getLogger("semanticpy")

logger.addHandler(logging.StreamHandler())

logger.propagate = False
