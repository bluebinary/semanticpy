from __future__ import annotations

import copy
import json

from semanticpy.logging import logger
from semanticpy.enumerations import OverwriteMode, AppendingMode
from semanticpy.errors import SemanticPyError


class Node(object):
    """Node data type class supporting the creation of node tree structures"""

    __iter__ = None  # Mark the class as non-iterable

    _type = None
    _name: str = None
    _data: dict[str, object] = None
    _settings: dict[str, object] = {}
    _canonical: dict[str, str] = {}
    _namespace: dict[str, str] = {}
    _multiple: list[str] = []
    _sorting: dict[str, int] = {}
    _special: list[str] = [
        "_type",
        "_name",
        "_data",
        "_settings",
        "_canonical",
        "_namespace",
        "_multiple",
        "_sorting",
        "_annotations",
    ]
    _aliases = {
        "ident": "id",
        "label": "_label",
    }
    _overwrite_mode: OverwriteMode = None
    _appending_mode: AppendingMode = None

    @classmethod
    def configure(
        cls,
        overwrite: OverwriteMode | str = None,
        appending: AppendingMode | str = None,
    ):
        """Supports configuring the Node and its subclasses with runtime options."""

        if overwrite is None:
            pass
        else:
            if isinstance(overwrite, str):
                overwrite = OverwriteMode.reconcile(name=overwrite, caselessly=True)

            if isinstance(overwrite, OverwriteMode):
                cls._overwrite_mode = overwrite
            else:
                raise TypeError(
                    "The 'overwrite' argument, if specified, must reference an OverwriteMode enumeration option or the string name of the desired option!"
                )

        if appending is None:
            pass
        else:
            if isinstance(appending, str):
                appending = AppendingMode.reconcile(name=appending, caselessly=True)

            if isinstance(appending, AppendingMode):
                cls._appending_mode = appending
            else:
                raise TypeError(
                    "The 'appending' argument, if specified, must reference an AppendingMode enumeration option or the string name of the desired option!"
                )

    def __init__(self, data: dict[str, object] = None, **kwargs):
        # logger.debug("%s.__init__(data: %s)" % (self.__class__.__name__, data))

        if data is None:
            self._data = {}
        elif isinstance(data, dict):
            self._data = dict(data)
        else:
            raise TypeError("The `data` property must be provided as a dictionary!")

        if not self._canonical:
            self._canonical = (
                self._settings.get("properties", {}).get("canonical") or {}
            )

        if not self._namespace:
            self._namespace = (
                self._settings.get("properties", {}).get("namespace") or {}
            )

        if not self._multiple:
            self._multiple = self._settings.get("properties", {}).get("multiple") or []

        if not self._sorting:
            self._sorting = self._settings.get("properties", {}).get("sorting") or {}

        self._annotations = {}

        for key, value in kwargs.items():
            self._data[key] = value

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __len__(self) -> int:
        return len(self._data)

    def __getattr__(self, name: str) -> object | None:
        value: object = None

        if isinstance(name, str) and name.startswith("_") and name in self._special:
            if name in self.__dict__:
                value = self.__dict__[name]
        else:
            if name in self._data:
                value = self._data[name]
            elif name in self._multiple:
                self._data[name] = value = Nodes()

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
                if self.__class__._appending_mode is AppendingMode.Unique:
                    if not value in self._data[name]:
                        self._data[name].append(value)
                else:
                    self._data[name].append(value)
            else:
                if self.__class__._overwrite_mode is OverwriteMode.Warning:
                    logger.warning(
                        f"The '{self.__class__.__name__}' entity's '{name}' property has already been assigned to '{self._data[name]}', and will be overwritten with the newly provided value: '{value}'!"
                    )

                    self._data[name] = value
                elif self.__class__._overwrite_mode is OverwriteMode.Prevent:
                    logger.warning(
                        f"The '{self.__class__.__name__}' entity's '{name}' property has already been assigned to '{self._data[name]}', and current library configuration prevents it from being overwritten!"
                    )
                elif self.__class__._overwrite_mode is OverwriteMode.PreventQuietly:
                    pass
                elif self.__class__._overwrite_mode is OverwriteMode.Error:
                    raise SemanticPyError(
                        f"The '{self.__class__.__name__}' entity's '{name}' property has already been assigned to '{self._data[name]}', and current library configuration does not allow singular property values to be overwritten!"
                    )
                else:
                    self._data[name] = value
        else:
            if name in self._multiple:
                self._data[name] = Nodes([value])
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

    def equals(self, other: Node, strict: bool = False) -> bool:
        """Support comparing Node instances for equality."""

        if not isinstance(other, Node):
            return NotImplemented

        equal: bool = False

        sproperties = self.properties()
        oproperties = other.properties()

        for name, value in oproperties.items():
            if name in sproperties:
                if sproperties[name] == value:
                    equal = True
                else:
                    equal = False
                    break
            elif name in self._aliases and self._aliases[name] in sproperties:
                if sproperties[self._aliases[name]] == value:
                    equal = True
                else:
                    equal = False
                    break
            elif strict is True:
                equal = False
                break

        if equal is True and strict is True:
            for name, value in sproperties.items():
                if name in oproperties:
                    if oproperties[name] == value:
                        equal = True
                    else:
                        equal = False
                        break
                elif name in self._aliases and self._aliases[name] in oproperties:
                    if oproperties[self._aliases[name]] == value:
                        equal = True
                    else:
                        equal = False
                        break
                elif strict is True:
                    equal = False
                    break

        return equal

    @property
    def type(self) -> str:
        return self.__class__.__name__

    @property
    def typed(self) -> str:
        return self._type

    @property
    def context(self) -> object:
        return self._context

    @property
    def name(self) -> str:
        return self._name

    @property
    def data(self) -> dict[str, object]:
        return copy.copy(self._data)

    @data.setter
    def data(self, data: dict[str, object]):
        if not isinstance(data, dict):
            raise TypeError("The data must be defined as a dictionary!")

        self._data = data

    @property
    def settings(self) -> dict[str, object]:
        return self._settings

    @settings.setter
    def settings(self, settings: dict[str, object]):
        if not isinstance(settings, dict):
            raise TypeError("The settings must be defined as a dictionary!")

        self._settings = settings

    def annotate(self, name: str = None, value: object = None, /, **kwargs) -> Node:
        """Support adding arbitrary named 'annotations' to a node for later retrieval"""

        annotations: dict[str, object] = {}

        if name is None:
            pass
        elif not isinstance(name, str):
            raise TypeError(
                "The 'name' argument, if specified, must have a string value!"
            )
        elif not len(name := name.strip()) > 0:
            raise ValueError(
                "The 'name' argument, if specified, must have a non-empty string value!"
            )
        else:
            annotations[name] = value

        for name, value in kwargs.items():
            annotations[name] = value

        self._annotations.update(annotations)

        return self

    def annotation(self, name: str, default: object = None):
        """Support retrieving a named annotation if available or returning the default"""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")
        elif not len(name := name.strip()) > 0:
            raise ValueError("The 'name' argument must have a non-empty string value!")

        if name in self._annotations:
            return self._annotations[name]

        return default

    def annotations(self) -> dict[str, object]:
        """Support retrieving a copy of all named annotations associated with the node"""

        return dict(self._annotations)

    def _canonicalize(self, name: str) -> str:
        """Given a property name, return the canonical version of the property name."""

        if not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")
        elif not len(name := name.strip()) > 0:
            raise ValueError("The 'name' argument must have a non-empty string value!")

        if name in self._canonical:
            if name in self._namespace:
                return self._namespace[name] + ":" + self._canonical[name]
            else:
                return self._canonical[name]
        else:
            return name

    def _serialize(
        self,
        source: object = None,
        sorting: list[str] | dict[str, int] = None,
    ) -> object:
        data: object = None

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

                data[self._canonicalize(key)] = self._serialize(value, sorting=sorting)

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

    def _sort(
        self,
        dictionary: dict,
        sorting: list[str] | dict[str, int] = None,
    ) -> dict[str, object]:
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

        keys = {self._canonicalize(key): index for key, index in keys.items()}

        sort: dict[str, object] = {}

        for key, value in sorted(dictionary.items(), key=lambda x: keys.get(x[0], -1)):
            sort[key] = value

        return sort

    def properties(
        self,
        prepend: dict[str, object] = None,
        append: dict[str, object] = None,
        sorting: list[str] | dict[str, int] = None,
        callback: callable = None,
        attribute: str = None,
        unpack: bool = False,
    ) -> dict[str, object]:
        properties: dict[str, object] = {}

        if isinstance(serialized := self._serialize(self.data, sorting=sorting), dict):
            properties = serialized

            if prepend is None:
                pass
            elif isinstance(prepend, dict) and len(prepend) > 0:
                properties = {**prepend, **properties}
            else:
                raise TypeError(
                    "The 'prepend' argument, if specified, must reference a dictionary!"
                )

            if append is None:
                pass
            elif isinstance(append, dict) and len(append) > 0:
                properties = {**properties, **append}
            else:
                raise TypeError(
                    "The 'prepend' argument, if specified, must reference a dictionary!"
                )

            if callable(callback):
                properties = self.walkthrough(
                    callback=callback,
                    attribute=attribute,
                    container=properties,
                )

        return properties.items() if unpack is True else properties

    def walkthrough(
        self,
        callback: callable,
        attribute: str = None,
        container: dict[str, object] | list[dict[str, object]] = None,
    ) -> dict[str, object]:
        """Perform a recursive walkthrough of a dictionary/list calling the callback
        for any matched attribute, returning a dictionary representation of the Node."""

        if container is None:
            container = dict(self.properties())

        if not isinstance(container, (dict, list)):
            raise TypeError("The 'container' argument must be a dictionary or list!")

        if not (
            attribute is None or (isinstance(attribute, str) and len(attribute) > 0)
        ):
            raise ValueError(
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


class Nodes(list):
    """The Nodes class holds a list of Node entities and supports filtering."""

    def __contains__(self, item: object, strict: bool = True) -> bool:
        """Determines if the list contains the specified item or not."""

        if isinstance(item, Node):
            for node in self:
                if node is item:
                    return True
                elif node.equals(item, strict=strict):
                    return True
            return False
        else:
            return super().__contains__(item)

    def unpack(self, property: str) -> Nodes[Node]:
        """Unpack a nested property into a new Nodes instance."""

        temp: Nodes[Node] = Nodes()

        if not isinstance(property, str):
            raise TypeError("The 'property' argument must have a string value!")

        if len(self) == 0:
            return temp

        for node in self:
            if isinstance(subnode := getattr(node, property, None), list):
                for node in subnode:
                    if isinstance(node, Node):
                        temp.append(node)
                    else:
                        logger.warning(
                            "All elements in the list must be Node instances!"
                        )
            elif isinstance(subnode, Node):
                temp.append(subnode)
            else:
                logger.warning("All elements in the list must be Node instances!")

        return temp

    def filter(self, **filters: dict[str, object]) -> Nodes[Node]:
        """Return a list of Node elements matching the provided filters."""

        temp: Nodes[Node] = Nodes()

        if len(self) == 0:
            return self

        if len(filters) == 0:
            return self

        for node in self:
            include: bool = False

            for name, value in filters.items():
                if isinstance(value, dict):
                    value = Node(data=value)

                if not (nodevalue := getattr(node, name, None)) is None:
                    if isinstance(valuelist := value, (list, Nodes)):
                        if isinstance(nodevalue, Nodes):
                            matches: bool = False

                            for value in valuelist:
                                if nodevalue.__contains__(value, strict=False):
                                    matches = True
                                else:
                                    matches = False
                                    break

                            if matches is True:
                                include = True
                            else:
                                include = False
                                break
                        else:
                            logger.warning(
                                "The '%s' filter is a list, but the node's matching property is not!",
                                name,
                            )
                    elif isinstance(nodevalue, Nodes):
                        if isinstance(value, (list, set, tuple)):
                            for val in value:
                                if nodevalue.__contains__(val, strict=False):
                                    include = True
                                else:
                                    include = False
                                    break
                            if not include:
                                break
                        elif nodevalue.__contains__(value, strict=False):
                            include = True
                        else:
                            include = False
                            break
                    elif nodevalue == value:
                        include = True
                    else:
                        include = False
                        break

            if include:
                temp.append(node)

        return temp

    def first(self, **filters: dict[str, object]) -> Node | None:
        """Return the first matching Node, if one is found, or None otherwise."""

        if len(self) == 0:
            return None

        if len(filters) == 0:
            return self[0]

        if len(matches := self.filter(**filters)) == 0:
            return None

        return matches[0]

    def last(self, **filters: dict[str, object]) -> Node | None:
        """Return the last matching Node, if one is found, or None otherwise."""

        if len(self) == 0:
            return None

        if len(filters) == 0:
            return self[-1]

        if len(matches := self.filter(**filters)) == 0:
            return None

        return matches[-1]
