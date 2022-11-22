import copy
import json

from semanticpy.logging import logger


class Node(object):
    """Generic Data Node"""

    _type = None
    _name = None
    _data = None
    _settings = {}
    _multiple = []
    _sorting = {}
    _special = ["_type", "_name", "_data", "_settings", "_multiple", "_sorting"]

    def __init__(self, data: dict = None, **kwargs):
        # logger.debug("%s.__init__(data: %s)" % (self.__class__.__name__, data))

        if data is None:
            self._data = {}
        elif isinstance(data, dict):
            self._data = data
        else:
            raise TypeError("The `data` property must be provided as a dictionary!")

        if not self._multiple:
            self._multiple = self._settings.get("properties", {}).get("multiple") or []

        if not self._sorting:
            self._sorting = self._settings.get("properties", {}).get("sorting") or {}

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name

    @property
    def data(self):
        return copy.copy(self._data)

    @data.setter
    def data(self, data):
        if not isinstance(data, dict):
            raise RuntimeError("The data must be defined as a dictionary!")

        self._data = data

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, settings):
        if not isinstace(settings, dict):
            raise RuntimeError("The settings must be defined as a dictionary!")

        self._settings = settings

    def __getattr__(self, name):
        value = None

        if name.startswith("_") and name in self._special:
            if name in self.__dict__:
                value = self.__dict__[name]
        else:
            if name in self._data:
                value = self._data[name]

        # logger.debug("%s.__getattr__(name: %s) called => %s" % (self.__class__.__name__, name, value))

        return value

    def __setattr__(self, name, value):
        logger.debug(
            "%s.__setattr__(name: %s, value: %s)"
            % (self.__class__.__name__, name, value)
        )

        if name.startswith("_") and name in self._special:
            return super().__setattr__(name, value)

        if name in self._data:
            if name in self._multiple:
                self._data[name].append(value)
            else:
                self._data[name] = value
        else:
            if name in self._multiple:
                self._data[name] = [value]
            else:
                self._data[name] = value

    def __delattr__(self, name):
        logger.debug(
            "%s.__delattr__(name: %s) called" % (self.__class__.__name__, name)
        )

        if name in self._data:
            del self._data[name]

    def __getitem__(self, name):
        return self.__getattr(name)

    def __setitem__(self, name, value):
        return self.__setattr__(name, value)

    def _serialize(self, variable=None, sorting: list[str] | dict[str, int] = None):
        data = None

        if variable is None:
            variable = self

        if isinstance(variable, Node):
            data = variable._serialize(variable.data, sorting=sorting)

            if isinstance(data, dict):
                data = variable._sort(data, sorting=sorting)
        elif isinstance(variable, dict):
            data = {}

            for key in variable:
                value = variable[key]

                if value is None:
                    continue

                data[key] = self._serialize(value, sorting=sorting)

            data = self._sort(data, sorting=sorting) if data else data
        elif isinstance(variable, list):
            data = []

            for index, value in enumerate(variable):
                if value is None:
                    continue

                data.append(self._serialize(value, sorting=sorting))
        else:
            data = variable

        return data

    def _sort(self, dictionary: dict, sorting: list[str] | dict[str, int] = None):
        if sorting is None:
            sorting = self._sorting

        if isinstance(sorting, list):
            keys = {key: index for (index, key) in enumerate(sorting, start=0)}
        elif isinstance(sorting, dict):
            keys = sorting
        else:
            raise TypeError(
                "The `sorting` parameter must be provided as a list or dictionary!"
            )

        sort = {}

        for key, value in sorted(dictionary.items(), key=lambda x: keys.get(x[0], -1)):
            sort[key] = value

        return sort

    def properties(
        self,
        prepend: dict = None,
        append: dict = None,
        sorting: list[str] | dict[str, int] = None,
    ):
        if properties := self._serialize(self.data, sorting=sorting):
            if prepend:
                properties = {**prepend, **properties}

            if append:
                properties = {**properties, **append}

            return properties

    def json(
        self,
        compact: bool = False,
        indent: int = 4,
        sorting: list[str] | dict[str, int] = None,
    ):
        logger.debug(
            "%s.json(compact: %s, indent: %d, sorting: %s) called"
            % (self.__class__.__name__, compact, indent, sorting)
        )

        data = self.properties(sorting=sorting) or {}

        return json.dumps(
            data,
            indent=indent if compact is False else None,
            sort_keys=False,
            ensure_ascii=False,
        )
