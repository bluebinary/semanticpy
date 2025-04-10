import copy
import json

from semanticpy.logging import logger


class Node(object):
    """Node data type class supporting the creation of node tree structures"""

    _type = None
    _name = None
    _data = None
    _settings = {}
    _multiple = []
    _sorting = {}
    _special = [
        "_type",
        "_name",
        "_data",
        "_settings",
        "_multiple",
        "_sorting",
        "_annotations",
    ]

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

        self._annotations = {}

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

    def annotate(self, name: str, value):
        """Support adding arbitrary named 'annotations' to a node for later retrieval"""
        self._annotations[name] = value

    def annotation(self, name: str, default=None):
        """Support retrieving a named annotation if available or returning the default"""
        if name in self._annotations:
            return self._annotations[name]
        return default

    def annotations(self) -> dict:
        """Support retrieving a copy of all named annotations associated with the node"""
        return dict(self._annotations)

    def __getattr__(self, name: str) -> object | None:
        value = None

        if isinstance(name, str) and name.startswith("_") and name in self._special:
            if name in self.__dict__:
                value = self.__dict__[name]
        else:
            if name in self._data:
                value = self._data[name]

        # logger.debug("%s.__getattr__(name: %s) called => %s" % (self.__class__.__name__, name, value))

        return value

    def __setattr__(self, name: str, value: object):
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

    def __delattr__(self, name: str):
        logger.debug(
            "%s.__delattr__(name: %s) called" % (self.__class__.__name__, name)
        )

        if name in self._data:
            del self._data[name]

    def __getitem__(self, name: str) -> object | None:
        return self.__getattr__(name)

    def __setitem__(self, name: str, value: object):
        return self.__setattr__(name, value)

    def _serialize(self, source=None, sorting: list[str] | dict[str, int] = None):
        data = None

        if source is None:
            source = self

        if isinstance(source, Node):
            data = source._serialize(source.data, sorting=sorting)

            if isinstance(data, dict):
                data = source._sort(data, sorting=sorting)
        elif isinstance(source, dict):
            data = {}

            for key in source:
                value = source[key]

                if value is None:
                    continue

                data[key] = self._serialize(value, sorting=sorting)

            data = self._sort(data, sorting=sorting) if data else data
        elif isinstance(source, list):
            data = []

            for index, value in enumerate(source):
                if value is None:
                    continue

                data.append(self._serialize(value, sorting=sorting))
        else:
            data = source

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
        callback: callable = None,
        attribute: str = None,
    ):
        if properties := self._serialize(self.data, sorting=sorting):
            if prepend:
                properties = {**prepend, **properties}

            if append:
                properties = {**properties, **append}

            if callable(callback):
                properties = self.walkthrough(
                    callback=callback,
                    attribute=attribute,
                    container=properties,
                )

            return properties

    def walkthrough(
        self,
        callback: callable,
        attribute: str = None,
        container: dict | list = None,
    ):
        """Perform a recursive walkthrough of a dictionary/list calling the callback
        for any matched attribute"""

        if container is None:
            container = dict(self.properties())

        if not isinstance(container, (dict, list)):
            raise RuntimeError("The 'container' argument must be a dictionary or list!")

        if not (
            attribute is None or (isinstance(attribute, str) and len(attribute) > 0)
        ):
            raise RuntimeError(
                "If provided, the 'attribute' parameter must be a non-empty string!"
            )

        if isinstance(container, dict):
            for key in container:
                value = container[key]

                if attribute is None or attribute == key:
                    value = callback(
                        key=key,
                        value=value,
                        container=container,
                    )

                if isinstance(value, (dict, list, tuple, set)):
                    value = self.walkthrough(
                        callback=callback,
                        attribute=attribute,
                        container=value,
                    )

                container[key] = value
        elif isinstance(container, (list, tuple, set)):
            for key, value in enumerate(container):
                if attribute is None or attribute == key:
                    value = callback(
                        key=key,
                        value=value,
                        container=container,
                    )

                if isinstance(value, (dict, list, tuple, set)):
                    value = self.walkthrough(
                        callback=callback,
                        attribute=attribute,
                        container=value,
                    )

                container[key] = value

        return container

    def json(
        self,
        compact: bool = False,
        indent: int = 4,
        sorting: list[str] | dict[str, int] = None,
        callback: callable = None,
        attribute: str = None,
    ) -> str:
        logger.debug(
            "%s.json(compact: %s, indent: %d, sorting: %s, callback: %s, attribute: %s)"
            % (self.__class__.__name__, compact, indent, sorting, callback, attribute)
        )

        if compact is True:
            indent = None

        properties = (
            self.properties(
                sorting=sorting,
                callback=callback,
                attribute=attribute,
            )
            or {}
        )

        return json.dumps(
            properties, indent=indent, ensure_ascii=False, sort_keys=False
        )

    def print(self):
        if properties := self.properties():

            def _print(
                value,
                name: str,
                key: str | int = None,
                indent: int = 0,
                position: int = 0,
            ):
                if position > 0:
                    prefix = (" " * indent) + " |-(\033[1;32m%d\033[0m)->" % (position)
                else:
                    prefix = (" " * indent) + " |-(0)->"

                if isinstance(value, (int, float, bool, str)):
                    if key:
                        print(
                            "%s \033[1;33m%s.%s\033[0m => %s"
                            % (prefix, name, key, value)
                        )
                    else:
                        print("%s \033[1;33m%s\033[0m => %s" % (prefix, name, value))
                elif isinstance(value, list):
                    print("%s \033[1;33m%s\033[0m =>" % (prefix, name))

                    for index, val in enumerate(value, start=1):
                        _print(val, name, indent=indent + 1, position=index)
                elif isinstance(value, dict):
                    print("%s \033[1;33m%s\033[0m =>" % (prefix, name))

                    for prop, attr in value.items():
                        _print(attr, value.get("type"), prop, indent=indent + 1)

            print(self)
            for name, value in properties.items():
                _print(value, name)
            print()
