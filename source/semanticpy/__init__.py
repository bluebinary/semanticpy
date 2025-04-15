from __future__ import annotations

import json
import os
import copy
import datetime
import requests

from semanticpy.logging import logger
from semanticpy.errors import SemanticPyError
from semanticpy.types import (
    Node,
    Namespace,
    readonlydict,
)


logger.debug("semanticpy library imported from: %s" % (__file__))


class Model(Node):
    """SemanticPy Base Model Class"""

    _profile: str = None
    _context: str = None
    _entities: Namespace[str, Model] = Namespace()
    _property: list[str] = []
    _properties: dict[str, dict] = {}
    _hidden: list[str] = []
    _globals: dict[str, object] = None

    @classmethod
    def factory(
        cls, profile: str, context: str = None, globals: dict = None
    ) -> Namespace:
        if not isinstance(cls._entities, Namespace):
            raise TypeError(
                "The %s._entities attribute must be an %s instance!"
                % (
                    cls.__name__,
                    type(Namespace),
                )
            )

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

        glo = globals if isinstance(globals, dict) else cls._globals

        if not os.path.exists(profile):
            if not profile.endswith(".json"):
                profile += ".json"

            profile = os.path.join(os.path.dirname(__file__), "profiles", profile)

        if not os.path.exists(profile):
            raise SemanticPyError(
                "The specified profile (%s) does not exist!" % (profile)
            )

        if not os.path.isfile(profile):
            raise SemanticPyError(
                "The specified profile (%s) is not a file!" % (profile)
            )

        logger.debug("%s.factory() Loading profile => %s", cls.__name__, profile)

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
            nonlocal cls, glo, entities

            # If the named class already exists, return immediately
            if isinstance(class_type := cls._entities.get(name, default=None), type):
                if issubclass(class_type, Model):
                    return class_type
                else:
                    raise TypeError(
                        "The %s.%s attribute is not a subclass of %s as expected! Ensure this attribute has not been set on the class accidentally!"
                        % (
                            cls.__name__,
                            name,
                            cls.__name__,
                        )
                    )

            if not (entity := entities.get(name)):
                raise SemanticPyError(
                    "The specified entity type (%s) has not been defined in the profile!"
                    % (name)
                )

            bases: tuple = ()
            properties: dict[str, object] = {}

            for prop, props in (cls._profile.get("properties") or {}).items():
                properties[prop] = cls._validate_properties(props, prop)

            if superclasses := entity.get("superclasses"):
                if isinstance(superclasses, str):
                    superclasses = [superclasses]

                for superclass_name in superclasses:
                    if superclass := _class_factory(superclass_name):
                        bases += (superclass,)

                        for prop, props in (superclass._properties or {}).items():
                            properties[prop] = cls._validate_properties(props, prop)
                    else:
                        raise SemanticPyError(
                            "Failed to find or create (base) superclass: %s!"
                            % (superclass_name),
                        )

            if self_properties := entity.get("properties"):
                for prop, props in self_properties.items():
                    properties[prop] = cls._validate_properties(props, prop)

            if len(bases) == 0:
                bases += (cls,)

            accepted: bool = False
            multiple: list[str] = []
            hidden: list[str] = []
            sorting: dict[str, int] = {}

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
                "_property": None,
                "_properties": properties,
            }

            if class_type := type(name, bases, attributes):
                # Add the class to the Model's namespace so that it can be accessed elsewhere

                # setattr(cls, name, class_type)
                cls._entities[name] = class_type

                if isinstance(glo, dict):
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
                        if not isinstance(_synonym, str):
                            raise TypeError(
                                "Entity class synonyms must be defined as strings!"
                            )

                        class_type._synonym = synonym

                        # setattr(cls, synonym, class_type)
                        cls._entities[synonym] = class_type

                        if isinstance(glo, dict):
                            glo[synonym] = class_type

                return class_type

        for name in entities:
            if class_type := _class_factory(name):
                cls._entities[name] = class_type

                # setattr(cls, name, class_type)

                if isinstance(glo, dict):
                    glo[name] = class_type
            else:
                raise SemanticPyError("Failed to create entity type '%s'!" % (name))

        return cls._entities

    @classmethod
    def teardown(cls, globals: dict = None):
        """This method will clear the dynamically created model classes from the globals
        dictionary, reversing the work of the factory method used during initialization.
        """

        if not (globals is None or isinstance(globals, dict)):
            raise TypeError(
                "The 'globals' argument must be None or reference a dictionary!"
            )

        glo: dict[str, object] = globals if globals else cls._globals

        removals: list[str] = []

        for key, value in cls._entities:
            removals.append(key)

        for key in removals:
            del cls._entities[key]

            if isinstance(glo, dict):
                del glo[key]

    @classmethod
    def open(cls, filepath: str) -> Model:
        """Support opening and loading model instances from stored JSON-LD files"""

        # cls.factory(profile=profile, context=context, globals=globals)

        logger.debug("%s.open(filepath: %s)", cls.__name__, filepath)

        if not (isinstance(filepath, str) and len(filepath := filepath.strip()) > 0):
            raise ValueError(
                "The 'filepath' argument must be a valid non-empty string!"
            )

        if not cls._entities:
            raise RuntimeError(
                "Please ensure that the Model.factory() method has been called to initialize the models!"
            )

        data: dict[str, object] = None

        if (
            filepath.startswith("http://")
            or filepath.startswith("https://")
            or filepath.startswith("//")
        ):
            try:
                if isinstance(response := requests.get(url), object):
                    if response.status_code == 200:
                        if not isinstance(data := response.json(), dict):
                            raise ValueError(
                                "The specified file does not contain valid JSON data!"
                            )
                    else:
                        raise ValueError(
                            "The specified file could not be loaded from its URL!"
                        )
                else:
                    raise ValueError(
                        "The specified file could not be loaded from its URL!"
                    )
            except Exception as exception:
                raise ValueError(
                    "The specified file could not be loaded (%s) from its URL!"
                    % (exception)
                )
        elif (
            filepath.startswith("/")
            or filepath.startswith("./")
            or filepath.startswith("../")
            or filepath.startswith("~/")
        ):
            if filepath.startswith("~/"):
                filepath = os.path.expanduser(filepath)

            with open(filepath, "r") as handle:
                if not isinstance(data := json.load(handle), dict):
                    raise ValueError(
                        "The specified file does not contain valid JSON data!"
                    )
        else:
            raise ValueError("The specified filepath (%s) is unsupported!" % (filepath))

        if isinstance(data, dict):
            if context := data.get("@context"):
                if typed := data.get("type"):
                    if entity := cls.entity(typed):
                        if instance := entity(data=readonlydict(data)):
                            return instance
                        else:
                            raise ValueError(
                                "The data could not be loaded into an %s model entity instance!"
                                % (entity)
                            )
                    else:
                        raise ValueError(
                            "The type (%s) does not correspond to any known model entities; ensure that SemanticPy's Model.factory() method has been called with a suitable profile!"
                            % (typed)
                        )
                else:
                    raise ValueError("The data does not contain a 'type' property!")
            else:
                raise ValueError(
                    "The filepath does not reference a valid JSON-LD file!"
                )
        else:
            raise ValueError("No data could be loaded from the specified file!")

    @classmethod
    def _validate_properties(cls, properties: dict, property: str) -> dict:
        """Helper method to validate property specification dictionaries"""

        if not isinstance(properties, dict):
            raise TypeError(
                "The 'properties' argument provided for the '%s' property must have a dictionary value!"
                % (property)
            )

        if "accepted" in properties:
            if not isinstance(properties["accepted"], bool):
                raise TypeError(
                    "The 'accepted' property for '%s' must have a boolean value!"
                    % (property)
                )
        else:
            properties["accepted"] = True

        if "individual" in properties:
            if not isinstance(properties["individual"], bool):
                raise TypeError(
                    "The 'individual' property for '%s' must have a boolean value!"
                    % (property)
                )
        else:
            properties["individual"] = False

        if "sorting" in properties:
            if isinstance(properties["sorting"], int):
                if not properties["sorting"].__class__ is int and issubclass(
                    properties["sorting"].__class__, int
                ):
                    raise TypeError(
                        "The 'sorting' property for '%s' must have an integer value, held in an `int` data type!"
                        % (property)
                    )
                elif not (0 <= properties["sorting"] <= 100000000):
                    raise ValueError(
                        "The 'sorting' property for '%s' must have a positive integer value (0 – 100,000,000), not %s!"
                        % (property, properties["sorting"])
                    )
            else:
                raise TypeError(
                    "The 'sorting' property for '%s' must have an integer value!"
                    % (property)
                )
        else:
            properties["sorting"] = 10000

        if "alias" in properties:
            if not isinstance(properties["alias"], str):
                raise TypeError("The 'alias' property must have a string value!")

        if "canonical" in properties:
            if not isinstance(properties["canonical"], str):
                raise TypeError("The 'canonical' property must have a string value!")

        return properties

    @classmethod
    def extend(
        cls,
        subclass: Model,
        properties: dict = None,
        context: str = None,
        globals: dict = None,
        typed: bool = True,
    ) -> None:
        """Class method to support extending the factory-generated model with additional
        model subclasses, and optionally, additional model-wide properties"""

        if not issubclass(subclass, Model):
            raise TypeError(
                "The 'subclass' argument must reference a subclass of Model!"
            )

        name: str = subclass.__name__

        if globals is None:
            pass
        elif not isinstance(globals, dict):
            raise TypeError(
                "The 'globals' argument must be None or reference a dictionary!"
            )

        glo: dict[str, object] = globals if globals else cls._globals

        # If any model-wide properties have been defined, apply them to each model entity
        if properties is None:
            pass
        elif not isinstance(properties, dict):
            raise TypeError("The 'properties' argument must be a dictionary!")
        else:
            # If any subclass-level properties have been defined, apply them to the subclass
            if hasattr(subclass, "_property"):
                if subclass._property is None:
                    subclass._property: list[str] = []
                elif not isinstance(subclass._property, list):
                    raise TypeError("The '_property' attribute must be a list type")
            else:
                subclass._property: list[str] = []

            for prop, props in properties.items():
                props: dict[str, object] = cls._validate_properties(props, prop)

                subclass._property.append(prop)

                if alias := props.get("alias"):
                    subclass._property.append(alias)

                if canonical := props.get("canonical"):
                    pass

                for class_name, entity in cls._entities.items():
                    entity._properties[prop] = cls._validate_properties(props, prop)

                    # If a property supports being specified via an alias, map that here
                    if alias := props.get("alias"):
                        entity._properties[alias] = {**props, **{"alias": prop}}

                    if sorting := props.get("sorting"):
                        entity._sorting[prop] = sorting

        # If any subclass-level properties have been defined, apply them to the subclass
        if hasattr(subclass, "_properties"):
            if not isinstance(subclass._properties, dict):
                raise TypeError("The '_properties' attribute must be a dictionary!")

            for prop, props in subclass._properties.items():
                props = cls._validate_properties(props, prop)

                if props.get("hidden") is True:
                    subclass._hidden.append(prop)

                if sorting := props.get("sorting"):
                    subclass._sorting[prop] = sorting
        else:
            subclass._properties = {}

        if context is None:
            pass
        elif isinstance(context, str):
            if not (
                len(context := context.strip()) > 0
                and (context.startswith("https://") or context.startswith("http://"))
            ):
                raise ValueError(
                    "The 'context' argument, if specified, must have a valid non-empty context URL string value!"
                )

            subclass._context = context
        else:
            raise TypeError(
                "The 'context' argument, if specified, must have a string value!"
            )

        # If this class is a special case that will be serialized without a "type", mark
        # its "type" property as hidden, so when serialized, "type" will be skipped
        if not isinstance(typed, bool):
            raise TypeError("The 'typed' argument must have a boolean value!")
        elif typed is False:
            subclass._hidden.append("type")

        # Merge any superclass properties into the subclass' property list
        for superclass in subclass.__bases__:
            if hasattr(superclass, "_properties"):
                if isinstance(superclass._properties, dict):
                    for prop, props in superclass._properties.items():
                        if not prop in subclass._properties:
                            subclass._properties[prop] = props

        if not name in cls._entities:
            # raise RuntimeError(
            #     "The extended entity '%s' has the same name as an existing entity!" % (subclass.__name__)
            # )

            # setattr(cls, name, class_type)
            cls._entities[name] = subclass

            if isinstance(glo, dict):
                # Add the class to global namespace so that it can be accessed elsewhere
                glo[name] = subclass

    @classmethod
    def entity(cls, name: str = None, property: str = None) -> Model | None:
        """Helper method to return the referenced entity type from the model"""

        if isinstance(name, str):
            if name in cls._entities:
                return cls._entities[name]
        elif isinstance(property, str):
            for name, entity in cls._entities.items():
                if isinstance(entity._property, list):
                    if property in entity._property:
                        return entity
        else:
            raise ValueError(
                "An entity name or entity-assignable property name must be provided!"
            )

    def __new__(cls, *args, **kwargs):
        # The '_special' list variable is defined in the base class and holds a list of
        # special class attribute names

        cls._special += [
            attr
            for attr in [
                "_hidden",
                "_reference",
                "_referenced",
                "_cloned",
            ]
            if attr not in cls._special
        ]

        return super().__new__(cls)

    def __init__(
        self,
        ident: str = None,
        label: str = None,
        data: dict[str, object] = None,
        **kwargs,
    ):
        super().__init__(
            # TODO: Determine if setting data via the superclass' constructor is optimal
            # data=data,
        )

        self._annotations: dict[str, object] = {}

        # Enable support for the essential model properties
        for prop in ["id", "type", "_label"]:
            if not prop in self._properties:
                self._properties[prop] = {
                    "accepted": True,
                    "individual": True,
                    "range": "xsd:string",
                }

        self.type: str = self.__class__.__name__

        if isinstance(data, dict):
            if ident is None:
                ident = data.get("id")

            if label is None:
                label = data.get("_label")

        if ident is None:
            pass
        elif not isinstance(ident, str):
            raise TypeError(
                "The 'ident' argument, if specified, must have a string value!"
            )

        self.id: str = ident or None

        if label is None:
            pass
        elif not isinstance(label, str):
            raise TypeError(
                "The 'label' argument, if specified, must have a string value!"
            )

        self._label: str = label or None

        # If a 'json' keyword argument has been specified, attempt to parse the value as
        # a JSON serialized string so long as the 'data' argument has not been specified
        if not (jsons := kwargs.pop("json", None)) is None:
            if not isinstance(jsons, str):
                raise TypeError(
                    "The 'json' argument must be a string containing the JSON-LD of the record to load!"
                )

            if data is None:
                try:
                    data = json.loads(jsons)
                except Exception as exception:
                    raise ValueError(
                        "The 'json' argument does not contain a valid JSON string: %s!"
                        % (str(exception))
                    )
            else:
                raise ValueError(
                    "The 'json' and 'data' arguments cannot be specified at the same time; please either provide data as a dictionary via the 'data' argument or as a serialized JSON string via the 'json' argument!"
                )

        if data is None:
            pass
        elif isinstance(data, dict):
            self.load(data=data, model=self)
        else:
            raise TypeError(
                "The 'data' argument, if specified, must have a dictionary value!"
            )

        for key, value in kwargs.items():
            self.__setattr__(key, value)

    # TODO: Should 'create' be a "private" method?
    @classmethod
    def create(cls, data: dict, property: str = None) -> Model:
        """Support creating a model entity from its data (dictionary) representation"""

        if not isinstance(data, dict):
            raise TypeError("The 'data' argument must have a dictionary value!")

        # Attempt to determine the entity type from the assigned 'type' string value
        if isinstance(typed := data.get("type"), str):
            if not isinstance(entity := cls.entity(name=typed), type):
                raise ValueError(
                    "The '%s' entity type cannot be mapped to a model entity!" % (typed)
                )

            if not isinstance(model := entity(data=data), Model):
                raise ValueError(
                    "The '%s' entity type could not be instantiated!" % (typed)
                )

        # Alternatively, for untyped model extensions, attempt to determine the entity
        # type from the property name that the entity has been assigned to in data
        elif isinstance(entity := cls.entity(property=property), type):
            if not isinstance(model := entity(data=data), Model):
                raise ValueError(
                    "The '%s' entity type could not be instantiated!" % (typed)
                )

        # If no entity type can be determined, raise an exception as the current data
        # node cannot be loaded into the data model; ensure the model has been defined
        # completely and in accordance with the provided data, including any extensions
        else:
            raise ValueError(
                "The entity type cannot be determined for the provided data dictionary; the dictionary must contain a valid 'type' property, or be an extended model entity assigned to an expected named property!"
            )

        return model

    # TODO: Should 'load' be a "private" method?
    def load(self, data: dict, model: Model) -> None:
        if not isinstance(data, dict):
            raise ValueError("The 'data' argument must be provided as a dictionary!")

        if not isinstance(model, self.__class__):
            raise TypeError(
                "The 'model' argument must be a subclass of %s!"
                % (self.__class__.__name__)
            )

        for property, value in data.items():
            if isinstance(value, dict):
                setattr(model, property, self.create(data=value, property=property))
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    # if not isinstance(item, dict):
                    #     raise TypeError(
                    #         "The list item at index %d is not a dictionary, but rather %s!" % (index, type(item))
                    #     )
                    setattr(model, property, self.create(data=item, property=property))
            else:
                setattr(model, property, value)

    def __getstate__(self) -> dict:
        """Support serializing deep copies of instances of this class"""

        return self.__dict__.copy()

    def __setstate__(self, state: dict) -> None:
        """Support restoring from deep copies of instances of this class"""

        self.__dict__.update(state)

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(ident = {self.id}, label = {self._label})>"

    def _find_type(self, range: str | Model) -> type | tuple[type] | None:
        if isinstance(range, str):
            if range == "rdfs:Literal":
                return (str, int, float)
            elif range == "rdfs:Class":
                return str
            elif range == "xsd:string":
                return str
            elif range == "xsd:dateTime":
                return (str, datetime.datetime)

        for key, entity in self._entities.items():
            if isinstance(range, str):
                if entity._name == range:
                    return entity
            elif issubclass(range, Model):
                if entity is range:
                    return entity

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def ident(self) -> str | None:
        return self.id

    @property
    def label(self) -> str | None:
        return self._label

    def __setattr__(self, name: str, value: object) -> None:
        # logger.debug("%s.%s(name: %s, value: %s) called" % (self.__class__.__name__, self.__setattr__.__name__, name, value))

        prop: dict[str, object] = self._properties.get(name) or {}

        if canonical := prop.get("canonical"):
            name = canonical
        elif alias := prop.get("alias"):
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
                types: tuple = ()

                if isinstance(range, str):
                    ranges = [range]
                elif isinstance(range, list):
                    ranges = range
                elif issubclass(range, Model):
                    ranges = [range]
                else:
                    raise TypeError(
                        "The 'range' property must be defined as a string, list, or a Model class type, not %s!"
                        % (range)
                    )

                for range in ranges:
                    if not (isinstance(range, str) or issubclass(range, Model)):
                        raise TypeError(
                            "The 'range' property can only contain valid type names or Model class types!"
                        )

                    if typed := self._find_type(range=range):
                        types += (typed,)
                    else:
                        raise ValueError(
                            "The '%s' range for the '%s' property cannot be reconciled to a known range type!"
                            % (range, name)
                        )

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

    def _serialize(
        self,
        source=None,
        sorting: list[str] | dict[str, int] = None,
    ) -> str:
        """Support serializing the current model instance into JSON-LD."""

        data: str = super()._serialize(source=source, sorting=sorting)

        if self._hidden and isinstance(data, dict):
            for prop in self._hidden:
                if prop in data:
                    del data[prop]

        return data

    @property
    def is_blank(self) -> bool:
        """Determine if a node is a blank node (i.e. that it does not have an id)."""

        return self.id is None

    def clone(self, properties: bool = True, reference: bool = False) -> Model:
        """Support cloning a Model instance."""

        cloned: Model = self.__class__(ident=self.id, label=self._label)

        special: list[str] = ["ident", "label", "data", "name", "type"]

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
        """Determine if a node has been cloned."""

        return hasattr(self, "_cloned") and isinstance(self._cloned, Model)

    def reference(self) -> Model:
        """Support creating a reference to another Model instance."""

        cloned: Model = self.clone(properties=False, reference=True)

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
        """Determine if a node is reference to another node."""

        return hasattr(self, "_reference") and isinstance(self._reference, Model)

    @property
    def was_referenced(self) -> bool:
        """Determine if a node was referenced by another node at least once."""

        return self._referenced is True

    def properties(
        self,
        sorting: list[str] | dict[str, int] = None,
        callback: callable = None,
        attribute: str | int = None,
    ) -> dict[str, object]:
        """Support obtaining a dictionary representation of the properties assigned to
        the current model instance."""

        properties: dict[str, object] = (
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

    def property(self, name: str = None, default: object = None) -> dict | None:
        """Support obtaining a copy of the value assigned to a model property"""

        if name is None:
            return copy.copy(self._properties)
        elif info := self._properties.get(name):
            return copy.copy(info)
        else:
            return default

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

            included: bool = True

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

        nodes: list[Model] = _nodes(self, nodes=[], parent=self)

        if callable(filter):
            temp: list[Model] = []

            for node in nodes:
                if filter(node, self) is True:
                    temp.append(node)

            nodes = temp

        return nodes
