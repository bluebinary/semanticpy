from semanticpy.logging import logger


class SemanticPyError(RuntimeError):
    def __init__(self, message="SemanticPy Error"):
        self.message = message
        super().__init__(self.message)
        # logger.error(self.message)
