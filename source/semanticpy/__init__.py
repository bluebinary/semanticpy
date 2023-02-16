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
                    "The specified profile (%s) does not contain a valid context property!"
                    % (profile),
                )

        if not isinstance(entities := cls._profile.get("entities"), dict):
            raise SemanticPyError(
                "The specified profile (%s) does not contain a valid entities property!"
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
    def entities(cls, name: str) -> Node | None:
        """Helper method to return the named entity type from the model"""

        if name in cls._entities:
            return cls._entities[name]

    def __new__(cls, **kwargs):
        cls._special += ["_hidden"]

        return super().__new__(cls)

    def __init__(
        self,
        ident: str = None,
        label: str = None,
        data: dict = None,
        **kwargs,
    ):
        super().__init__(data=data)

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
        elif name == "xsd:string":
            return str
        elif name == "xsd:dateTime":
            return (str, datetime.datetime)
        else:
            raise RuntimeError(f"Cannot find a match for the '{name}' range type!")

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
            raise KeyError(
                "Cannot set property `%s` on %s as it is not in the list of accepted properties (%s)!"
                % (
                    name,
                    self.__class__.__name__,
                    sorted([key for key in self._properties.keys()]),
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
                        types += (typed, )

                if len(types) == 0:
                    raise RuntimeError(
                        "Unable to find associated types for any of the specified ranges!"
                    )

                if not isinstance(value, types):
                    raise TypeError(
                        "Cannot set value of type '%s' on `%s`; must be of type %s!"
                        % (type(value), name, (", ".join(["'%s'" % (x) for x in types])))
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

    def properties(self, sorting: list[str] | dict[str, int] = None):
        properties = super().properties(sorting=sorting) or {}

        # If a context has been specified, prepend the @context property
        if context := (self._context or self._profile.get("context")):
            properties = {**{"@context": context}, **properties}

        return properties

    @property
    def name(self):
        return self.__class__.__name__
