import copy
import json

from semanticpy.logging import logger


class readonlydict(dict):
    """A subclass of the standard library dictionary that is read-only"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, name: str, value: object):
        raise RuntimeError(
            "This dictionary is read-only, cannot set item '%s'!" % (name)
        )
