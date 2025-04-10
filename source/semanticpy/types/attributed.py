import copy
import json

from semanticpy.logging import logger


class Attributed(object):
    """Container data type class supporting both dictionary and attribute assignment
    and retrieval of values"""

    def __init__(self, *args, **kwargs):
        self._special: list[str] = [
            attr for attr in dir(self) if not attr.startswith("_")
        ]

        self._items: dict[str, object] = dict(*args, **kwargs)

    def __getitem__(self, key: str) -> object:
        try:
            return self.__getattr__(key)
        except AttributeError as exception:
            raise KeyError("The '%s' key does not exist!" % (key)) from exception

    def __setitem__(self, key: str, value: object) -> None:
        return self.__setattr__(key, value)

    def __delitem__(self, key: str) -> None:
        return self.__delattr__(key)

    def __getattr__(self, key: str) -> object:
        if key.startswith("_") or key in self._special:
            return object.__getattr__(self, key)
        elif key in self._items:
            return self._items[key]
        else:
            raise AttributeError("The '%s' attribute does not exist!" % (key))

    def __setattr__(self, key: str, value: object) -> None:
        if key.startswith("_") or key in self._special:
            super().__setattr__(key, value)
        else:
            self._items[key] = value

    def __delattr__(self, key: str) -> None:
        if key.startswith("_") or key in self._special:
            super().__delattr__(key)
        elif key in self._items:
            del self._items[key]

    def __iter__(self):
        for key, value in self._items.items():
            yield key, value

    def __contains__(self, name: str) -> bool:
        return name in self._items

    def __len__(self) -> int:
        return len(self._items)

    def items(self) -> list[tuple[str, object]]:
        return self._items.items()

    def get(self, key: object, default: object = None) -> object | None:
        try:
            return self.__getattr__(key)
        except AttributeError as exception:
            return default
