from semanticpy.logging import logger

logger = logger.getChild(__name__)


class SemanticPyError(RuntimeError):
    def __init__(self, message: str = "SemanticPy Error"):
        self.message = message

        super().__init__(self.message)

        # logger.error(self.message)
