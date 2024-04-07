from __future__ import annotations
import json
import os
import copy
import datetime

from semanticpy.logging import logger
from semanticpy.errors import SemanticPyError
from semanticpy.node import Node


logger.debug("semanticpy library imported from: %s" % (__file__))


class Model(Node):
    """SemanticPy Base Model Class"""

    _profile = None
    _context = None
    _entities = {}
    _properties = {}
    _hidden = []
    _globals = globals()

    @classmethod
    def factory(cls, profile: str, context: str = None, globals: dict = None):
        if not (isinstance(profile, str) and len(profile := profile.strip()) > 0):
            raise SemanticPyError(
                "The 'profile' argument must be assigned a string containing a valid profile name!"
            )

        if not (
            context is None
            or (isinstance(context, str) and len(context := context.strip()) > 0)
        ):
            raise TypeError(
                "The 'context' argument must be None or a string containing the URL for a valid JSON-LD context!"
            )

        if not (globals is None or isinstance(globals, dict)):
            raise TypeError(
                "The 'globals' argument must be None or reference a dictionary!"
            )

        glo = globals if globals else cls._globals

        if not os.path.exists(profile):
            if not profile.endswith(".json"):
                profile += ".json"

            profile = os.path.join(os.path.dirname(__file__), "profiles", profile)

        if not os.path.exists(profile):
            raise SemanticPyError(
                "The specified profile (%s) does not exist!" % (profile)
            )

        with open(profile, "r") as handle:
            if contents := handle.read():
                try:
                    cls._profile = json.loads(contents)
                except json.decoder.JSONDecodeError as e:
                    raise SemanticPyError(
                        "The specified profile (%s) is invalid or incomplete (%s)!"
                        % (
                            profile,
                            str(e),
                        ),
                    )

        if not isinstance(cls._profile, dict):
            raise SemanticPyError(
                "The specified profile (%s) is invalid or incomplete!" % (profile)
            )

        if context is None:
            if not isinstance(context := cls._profile.get("context"), str):
                raise SemanticPyError(
                    "The specified profile (%s) does not contain a valid 'context' property!"
                    % (profile),
                )
        elif not (isinstance(context, str) and len(context := context.strip()) > 0):
            raise SemanticPyError(
                "The 'context' argument must contain a URL for a valid JSON-LD context document!"
            )
        elif not (context.startswith("http://") or context.startswith("https://")):
            raise SemanticPyError(
                "The 'context' argument must contain a URL for a valid JSON-LD context document!"
            )

        if not isinstance(entities := cls._profile.get("entities"), dict):
            raise SemanticPyError(
                "The specified profile (%s) does not contain a valid 'entities' property!"
                % (profile),
            )

        def _class_factory(name: str) -> type:
            nonlocal glo, entities, cls

            # If the named class already exists, return immediately
            if class_type := glo.get(name):
                return class_type

            if not (entity := entities.get(name)):
                raise SemanticPyError(
                    "The specified entity type (%s) has not been defined in the profile!"
                    % (name)
                )

            bases = ()
            properties = {}

            for prop, props in (cls._profile.get("properties") or {}).items():
                properties[prop] = cls._validate_properties(props)

            if superclasses := entity.get("superclasses"):
                if isinstance(superclasses, str):
                    superclasses = [superclasses]

                for superclass_name in superclasses:
                    if superclass := _class_factory(superclass_name):
                        bases += (superclass,)

                        for prop, props in (superclass._properties or {}).items():
                            properties[prop] = cls._validate_properties(props)
                    else:
                        raise SemanticPyError(
                            "Failed to find or create (base) superclass: %s!"
                            % (superclass_name),
                        )

            if self_properties := entity.get("properties"):
                for prop, props in self_properties.items():
                    properties[prop] = cls._validate_properties(props)

            if len(bases) == 0:
                bases += (cls,)

            accepted = False
            multiple = []
            hidden = []
            sorting = {}

            # properties_sorted = {}
            # for key in sorted(properties.keys()):
            #     properties_sorted[key] = properties[key]
            # properties = properties_sorted

            for prop, props in properties.items():
                # determine if at least one property on the model is marked as accepted
                if props.get("accepted", True) is True:
                    accepted = True

                # assemble the list of properties on the model that accept multiple values
                if props.get("individual", False) is False:
                    if not prop in multiple:
                        multiple.append(prop)

                # assemble the list of properties on the model that are hidden
                if props.get("hidden", False) is True:
                    if not prop in hidden:
                        hidden.append(prop)

                sorting[prop] = props.get("sorting") or 10000

            if accepted is False:
                raise SemanticPyError(
                    "No accepted properties have been defined in the %s profile for %s!"
                    % (
                        profile,
                        name,
                    ),
                )

            attributes = {
                "_context": context,
                "_type": entity.get("type"),
                "_name": entity.get("id"),
                "_multiple": multiple,
                "_sorting": sorting,
                "_hidden": hidden,
                "_properties": properties,
            }

            if class_type := type(name, bases, attributes):
                # Add the class to global namespace so that it can be accessed elsewhere
                glo[name] = class_type

                # If the class has a synonym, map it into the global namespace too; this
                # is useful for supporting backwards compatibility if classes are renamed
                # allowing existing code to produce output compliant with the latest model
                if synonym := entities.get(name).get("synonym"):
                    if isinstance(synonym, list):
                        _synonyms = synonym
                    elif isinstance(synonym, str):
                        _synonyms = [synonym]
                    else:
                        raise TypeError(
                            "The `synonym` must be provided as a list of strings or a string!"
                        )

                    for _synonym in _synonyms:
                        class_type._synonym = synonym
                        glo[synonym] = class_type

                return class_type

        for name in entities:
            if class_type := _class_factory(name):
                cls._entities[name] = class_type
            else:
                raise SemanticPyError("Failed to create entity type '%s'!" % (name))

    @classmethod
    def _validate_properties(cls, props: dict) -> dict:
        """Helper method to validate property specification dictionaries"""

        if not isinstance(props, dict):
            raise TypeError("The passed properties are not a valid dictionary!")

        if not "accepted" in props:
            props["accepted"] = True

        if not "individual" in props:
            props["individual"] = False

        if not "sorting" in props:
            props["sorting"] = 10000

        return props

    @classmethod
    def extend(cls, subclass, properties: dict = None, typed: bool = True):
        """Class method to support extending the factory-generated model with additional
        model subclasses, and optionally, additional model-wide properties"""

        if not issubclass(subclass, Model):
            raise TypeError(
                "The `subclass` property must reference a subclass of Model!"
            )

        # If any model-wide properties have been defined, apply them to each model entity
        if not properties is None:
            if not isinstance(properties, dict):
                raise TypeError("The `properties` property must be a dictionary!")

            for prop, props in properties.items():
                props = cls._validate_properties(props)

                for class_name, entity in cls._entities.items():
                    entity._properties[prop] = cls._validate_properties(props)

                    # If a property supports being specified via an alias, map that here
                    if alias := props.get("alias"):
                        entity._properties[alias] = {**props, **{"alias": prop}}

                    if sorting := props.get("sorting"):
                        entity._sorting[prop] = sorting

        # If any subclass-level properties have been defined, apply them to the subclass
        if hasattr(subclass, "_properties"):
            if not isinstance(subclass._properties, dict):
                raise TypeError("The `_properties` attribute must be a dictionary!")

            for prop, props in subclass._properties.items():
                props = cls._validate_properties(props)

                if props.get("hidden") is True:
                    subclass._hidden.append(prop)

                if sorting := props.get("sorting"):
                    subclass._sorting[prop] = sorting
        else:
            subclass._properties = {}

        # If this class is a special case that will be serialized without a "type", mark
        # its "type" property as hidden, so when serialized, "type" will be skipped
        if typed is False:
            subclass._hidden.append("type")

        # Merge any superclass properties into the subclass's property list
        for superclass in subclass.__bases__:
            for prop, props in superclass._properties.items():
                if not prop in subclass._properties:
                    subclass._properties[prop] = props

    @classmethod
    def entity(cls, name: str) -> Model | None:
        """Helper method to return the named entity type from the model"""

        if name in cls._entities:
            return cls._entities[name]

    def __new__(cls, **kwargs):
        cls._special += [
            attr
            for attr in [
                "_hidden",
                "_reference",
                "_referenced",
                "_cloned",
            ]
            if attr not in cls._special
        ]  # defined in the base class

        return super().__new__(cls)

    def __init__(
        self,
        ident: str = None,
        label: str = None,
        data: dict = None,
        **kwargs,
    ):
        super().__init__(data=data)

        self._annotations = {}

        # Ensure support for essential properties
        for prop in ["id", "type", "_label"]:
            if not prop in self._properties:
                self._properties[prop] = {
                    "accepted": True,
                    "individual": True,
                    "range": "xsd:string",
                }

        self.id = ident or None

        self.type = self.__class__.__name__

        self._label = label or None

        for kwarg in kwargs:
            self.__setattr__(kwarg, kwargs[kwarg])

    def __getstate__(self):
        """Support serializing deep copies of instances of this class"""
        state = self.__dict__.copy()

        return state

    def __setstate__(self, state):
        """Support restoring from deep copies of instances of this class"""
        self.__dict__.update(state)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"{self.__class__.__name__}(ident = {self.id}, label = {self._label})"

    def _find_type(self, name: str, prop: str = None) -> type | tuple[type]:
        for key, entity in self._entities.items():
            if entity._name == name:
                return entity

        if name == "rdfs:Literal":
            return (str, int, float)
        elif name == "rdfs:Class":
            return str
        elif name == "xsd:string":
            return str
        elif name == "xsd:dateTime":
            return (str, datetime.datetime)
        else:
            raise RuntimeError(f"Cannot find a match for the '{name}' range type!")

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def ident(self):
        return self.id

    @property
    def label(self):
        return self._label

    def __setattr__(self, name, value):
        # logger.debug("%s.%s(name: %s, value: %s) called" % (self.__class__.__name__, self.__setattr__.__name__, name, value))

        prop = self._properties.get(name) or {}

        if alias := prop.get("alias"):
            name = alias

        if not (
            name.startswith("@")
            or name in self._special
            or prop.get("accepted") is True
        ):
            raise AttributeError(
                "Cannot set property '%s' on %s as it is not in the list of accepted properties: '%s'!"
                % (
                    name,
                    self.__class__.__name__,
                    "', '".join(
                        sorted(
                            [
                                name
                                for name, prop in self._properties.items()
                                if prop.get("accepted") is True
                            ]
                        )
                    ),
                ),
            )

        if value is None:
            return super().__delattr__(name)
        else:
            if range := prop.get("range"):
                types = ()

                if isinstance(range, str):
                    ranges = [range]
                elif isinstance(range, list):
                    ranges = range

                for range in ranges:
                    if typed := self._find_type(range, name):
                        types += (typed,)

                if len(types) == 0:
                    raise RuntimeError(
                        "Unable to find associated types for any of the specified ranges!"
                    )

                if not isinstance(value, types):
                    raise TypeError(
                        "Cannot set value of type '%s' on '%s'; must be of type %s!"
                        % (
                            type(value),
                            name,
                            (", ".join(["'%s'" % (x) for x in types])),
                        )
                    )

            if domain := prop.get("domain"):
                pass

        return super().__setattr__(name, value)

    def _serialize(self, variable=None, sorting: list[str] | dict[str, int] = None):
        data = super()._serialize(variable=variable, sorting=sorting)

        if self._hidden and isinstance(data, dict):
            for prop in self._hidden:
                if prop in data:
                    del data[prop]

        return data

    @property
    def is_blank(self) -> bool:
        """Determine if a node is a blank node (i.e. that it does not have an id)"""
        return self.id is None

    def clone(self, properties: bool = True, reference: bool = False) -> Model:
        cloned = self.__class__(ident=self.id, label=self._label)

        special = ["ident", "label", "data", "name", "type"]

        for prop in dir(self):
            if prop.startswith("_") or properties is False:
                continue

            if attr := getattr(self, prop):
                if not callable(attr) and not prop in special:
                    setattr(cloned, prop, attr)

        # if not "_cloned" in self._special: self._special.append("_cloned")

        if reference is False:
            cloned._cloned = self

        return cloned

    @property
    def is_cloned(self) -> bool:
        """Determine if a node has been cloned"""
        return hasattr(self, "_cloned") and isinstance(self._cloned, Model)

    def reference(self) -> Model:
        cloned = self.clone(properties=False, reference=True)

        # Create a reference to the current node for later access
        cloned._reference = self

        # Note that the current node has been referenced by another node at least once
        self._referenced = True

        # Copy any annotations across to the cloned reference entity
        if annotations := self.annotations():
            for name, value in annotations.items():
                cloned.annotate(name, value)

        return cloned

    @property
    def is_reference(self) -> bool:
        """Determine if a node is reference to another node"""
        return hasattr(self, "_reference") and isinstance(self._reference, Model)

    @property
    def was_referenced(self) -> bool:
        """Determine if a node was referenced by another node at least once"""
        return self._referenced is True

    def properties(
        self,
        sorting: list[str] | dict[str, int] = None,
        callback: callable = None,
        attribute: str | int = None,
    ):
        properties = (
            super().properties(
                sorting=sorting,
                callback=callback,
                attribute=attribute,
            )
            or {}
        )

        # If a context has been specified, prepend the @context property
        if context := (self._context or self._profile.get("context")):
            properties = {**{"@context": context}, **properties}

        return properties

    def property(self, name: str = None) -> dict | None:
        if name is None:
            return copy.copy(self._properties)
        elif info := self._properties.get(name):
            return copy.copy(info)

    def documents(
        self,
        blank: bool = True,
        embedded: bool = True,
        referenced: bool = True,
        filter: callable = None,
    ) -> list[Model]:
        """Support assembling a list of documents from the current node structure"""

        def _nodes(
            node: Model, nodes: list, parent: Model, ancestor: Model = None
        ) -> list[Model]:
            """Recursive method to support filtering and assembling a list of nodes"""

            if node.is_cloned is True:
                node = parent = node._cloned
            elif node.is_reference is True:
                node = node._reference

            if not isinstance(node, Model):
                logger.debug(">>> node is invalid: %s" % (type(node)))
                return nodes

            if node in nodes:  # node seen before, so return, preventing an endless loop
                logger.debug(">>> node seen before: %s" % (node))
                return nodes

            logger.debug("> node:           %s" % (node))
            logger.debug("> id:             %s" % (node.id))
            logger.debug("> is_parent:      %s" % (node is parent))
            logger.debug("> is_blank:       %s" % (node.is_blank))
            logger.debug("> is_clone:       %s" % (node.is_cloned))
            logger.debug("> is_reference:   %s" % (node.is_reference))
            logger.debug("> was_referenced: %s" % (node.was_referenced))

            included = True

            if node is parent and not self is parent:
                logger.debug(">>> node is parent: %s" % (node.id))
                included = False

            if included is True and blank is False:
                if node.is_blank is True:
                    logger.debug(">>> node is blank: %s" % (node))
                    included = False

            if included is True and embedded is False:
                if node.id and parent.id:
                    if len(node.id) > len(parent.id) and node.id.startswith(parent.id):
                        logger.debug(
                            ">>> node is embedded (starts with parent.id): %s"
                            % (node.id)
                        )
                        included = False

            if included is True and referenced is False:
                if node.was_referenced is True:
                    logger.debug(
                        ">>> node was referenced by another node: %s" % (node.id)
                    )
                    included = False

            if included is True and callable(filter):
                if filter(node, self) is False:
                    logger.debug(
                        ">>> node was filtered out by custom filter callback logic: %s"
                        % (node.id)
                    )
                    included = False

            if included is True:
                logger.debug(">>> node was included: %s" % (node.id))
                nodes += [node]
            else:
                logger.debug(">>> node not included: %s" % (node.id))

            for key, value in node.data.items():
                if isinstance(value, Model):
                    _nodes(value, nodes, parent=parent, ancestor=node)
                elif isinstance(value, list):
                    for _index, _value in enumerate(value):
                        if isinstance(_value, Model):
                            _nodes(_value, nodes, parent=parent, ancestor=node)
                elif isinstance(value, dict):
                    for _key, _value in value.items():
                        if isinstance(_value, Model):
                            _nodes(_value, nodes, parent=parent, ancestor=node)

            return nodes

        nodes = _nodes(self, nodes=[], parent=self)

        return nodes
