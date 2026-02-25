# SemanticPy

The SemanticPy library for Python provides a simplified and consistent way to create JSON-LD documents from Python source code constructs such as classes and properties. In addition to simplifying the creation of JSON-LD documents, the library validates the model as it is being created, ensuring that properties can only be assigned valid values that are of the type or within the expected range defined in the model profile.

The SemanticPy library also supports loading JSON-LD documents from disk or the web, with support for automatically dereferencing linked documents, and enables these documents and the data they contain to be parsed and used.

### Requirements

The SemanticPy library has been tested with Python 3.10, 3.11, 3.12, 3.13 and 3.14. The
library has not been tested with, nor is it compatible with Python 3.9 or earlier.

### Installation

The SemanticPy library is available from the PyPi repository, so may be added to a project's dependencies via its `requirements.txt` file or similar by referencing the SemanticPy library's name, `semanticpy`, or the library may be installed directly onto your local development system using `pip install` by entering the following command:

	$ pip install semanticpy

### Example of Use

The SemanticPy library can be used to build simple or highly complex JSON-LD documents
through the streamlined use of Python classes and properties. The library will validate
the document as it is being assembled to ensure that only valid data model classes and
their associated properties are used, and that only values of the accepted domain and
range can be assigned to the properties.

The below example demonstrates the creation of a simple `HumanMadeObject` record using
the Linked.Art JSON-LD model:

```python
# Import the SemanticPy base Model from the library
from semanticpy import Model

# Initialize the Model using a named profile; in this case we specify the "linked-art"
# profile which is packaged with the library so only needs to be specified by its name.
# Other model profiles may be used to create models of other types; see the *Profiles*
# section in the README for more information. The factory method will dynamically create
# the required model class types and add them to the scope defined by the `globals`
# argument making the class types available for use just by referencing their names:
Model.factory(profile="linked-art", globals=globals())

# Register one or more identifier prefixes that take the form "<prefix>:" when used in
# an identifier and are replaced with the specified URIs during document serialization:
Model.prefix("aat", "http://vocab.getty.edu/aat/")

# Register one or more identifier prefixes that take the form "<prefix>:" when used in
# an identifier and are replaced with the specified URIs during document serialization:
Model.prefix("tgn", "http://vocab.getty.edu/tgn/")

# Create a HumanMadeObject (HMO) model instance
hmo = HumanMadeObject(
    ident = "https://example.org/object/1",
    label = "Example Object #1",
)

# Assign a classification of "Works of Art" to the HMO as per the Linked.Art model
hmo.classified_as = Type(
    ident = "aat:300133025",
    label = "Works of Art",
)

# As this example HMO represents a painting, add a classification of "Paintings" as per
# the Linked.Art model to specify the type of artwork that this HMO represents:
hmo.classified_as = typed = Type(
    ident = "aat:300033618",
    label = "Paintings (Visual Works)",
)

# Then classify the type classification above as the "type of work" as per the model:
typed.classified_as = Type(
    ident = "http://vocab.getty.edu/aat/300435443",
    label = "Type of Work",
)

# Include a Name node on the HMO to carry a name of the artwork
hmo.identified_by = name = Name(
    label = "Name of Artwork",
)

name.content = "A Painting"

# Include an Identifier node on the HMO to carry an identifier of the artwork
hmo.identified_by = identifier = Identifier(
    label = "Accession Number for Artwork",
)

identifier.content = "1982.A.39"

# Then serialise the model into a JSON string, in this case optionally specifying an
# indent of 2 spaces per level of nesting to make the JSON easier to read; by default
# the `json()` method will not use any indentation, compacting the JSON, which is great
# for saving storage, but can make longer JSON strings harder to read:
serialised = hmo.json(indent = 2)

# Then for the purposes of this example, we print out the JSON for review; the JSON
# could also be saved to a file, stored in a database, or used in some other way:
print(serialised)
```

The above code example will produce the following printed JSON output:

```json
{
  "@context": "https://linked.art/ns/v1/linked-art.json",
  "id": "https://example.org/object/1",
  "type": "HumanMadeObject",
  "_label": "Example Object #1",
  "classified_as": [
    {
      "id": "http://vocab.getty.edu/aat/300133025",
      "type": "Type",
      "_label": "Works of Art"
    },
    {
      "id": "http://vocab.getty.edu/aat/300033618",
      "type": "Type",
      "_label": "Paintings (Visual Works)",
      "classified_as": [
        {
          "id": "http://vocab.getty.edu/aat/300435443",
          "type": "Type",
          "_label": "Type of Work"
        }
      ]
    }
  ],
  "identified_by": [
    {
      "type": "Name",
      "_label": "Name of Artwork",
      "content": "A Painting"
    },
    {
      "type": "Identifier",
      "_label": "Accession Number for Artwork",
      "content": "1982.A.39"
    }
  ]
}
```

### Methods

The primary interface to the SemanticPy library is its `Model` class which offers the following methods:

 * `factory()` (`Namespace`) – the `factory()` class method is used to initialise the model for use, and returns a reference to the `Namespace` class instance into which the model is initialised and from which
 all available model entity classes can be referenced. If the optional `globals` argument is specified, the `factory()` method will also create references to the model entity classes in the provided `globals` scope. The `factory()` method accepts the following arguments:

   * `profile` (`str`) – (required) the `profile` argument specifies which profile the Model factory should use to initialise the model; the `profile` value can reference a profile provided by the library in the `profiles` subfolder, with or without the file name extension, or a profile stored externally to the library if a file path is provided. The profile should conform to that expected by the library and be held in JSON file.

   * `context` (`str`) - (optional) the `context` argument can be used to specify a `@context` URL to be used in the generated JSON-LD, if there is a need to override the `@context` URL specified within the
   profile.

   * `globals` (`dict`) – (optional) the `globals` argument can be used to specify a reference to a `globals()` scope into which the `factory()` method should create references to the model entities provided by the model as specified in the profile. If the `globals` argument is not specified 

 * `teardown()` – the `teardown()` class method is used to de-initialise the model, reversing the setup performed by the `factory()` method. The `teardown()` method accepts the following arguments:

   * `globals` (`dict`) – (optional) the `globals` argument can be used to specify a reference to the `globals()` scope from which the `teardown()` method should remove the references to the model entities provided by the model as specified in the profile.

 * `configure()` – the `configure()` class method may be used to configure certain aspects of the library's behaviour:

   * the overwrite behaviour of single-value properties
  
   * the appending behaviour of multiple-value properties

   The `configure()` method accepts the following arguments:
 
   * `overwrite` (`OverwriteMode` | `str`) – the `overwrite` argument is used to specify the desired overwrite behaviour mode, either via reference to an `OverwriteMode` enumeration option, or the string name of the `OverwriteMode` enumeration option. See the [**Overwrite Modes**](#overwrite-modes) section below for more information.

   * `appending` (`AppendingMode` | `str`) – the `appending` argument is used to specify the desired appending behaviour mode, either via reference to an `AppendingMode` enumeration option, or the string name of the `AppendingMode` enumeration option. See the [**Appending Modes**](#appending-modes) section below for more information.

 * `extend()` – the `extend()` class method is used to support extending the factory-generated model with additional model subclasses, and optionally, additional model-wide properties. The `extend()` method accepts the following arguments:

   * `subclass` (`Model`) – the `subclass` argument is used to reference the Model subclass that will be extended.

   * `properties` (`dict[str, dict[str, object]]`) – the `properties` argument is used to specify any additional properties that should be supported by the model subclass.

   * `context` (`str`) – (optional) the `context` argument can be used to specify an alternative `@context` URL for the model subclass.

   * `globals` (`dict`) – (optional) the `globals` argument can be used to specify an optional `globals()` scope into which a reference for the extended model subclass will be added.

   * `typed` (`bool`) – (optional) the `typed` argument can be used to specify if the model subclass should be serialised into JSON-LD with its `type` property or not; by default the `type` property is 
   always included during serialisation; this option can be used to prevent this if required.

 * `prefix(prefix: str, uri: str)` – the `prefix()` class method can be used to register one or more identifier prefixes with the library that will be replaced with the specified URI during document serialization.

 * `entity()` (`Model` | `None`) – the `entity()` method may be used to obtain the `type` reference for a named model entity, from which a new instance of that named model entity may be created; if no matching `Model` subclass can be found, the method returns `None`. The `entity()` method accepts the following arguments:

   * `name` (`str`) – the `name` argument is used to specify the name of the Model to find and return a
   reference to its `Model` subclass.

 * `clone()` (`Model`) – the `clone()` method may be used to clone the current model instance, creating a separate copy of the instance in memory which may be used or modified without affecting the original.

   * `properties` (`bool`) – (optional) the `properties` argument may be used to specify if the clone operation should also clone the properties of the current model instance into the clone or not. By default the properties are cloned; if the `properties` argument is specified and set to `False`, they will be skipped.

   * `reference` (`bool`) – (optional) the `reference` argument may be used to specify if the clone operation will create a reference in the cloned instance to its source instance. By default a reference will be created; if the `reference` argument is specified and set to `True`, the reference to its source instance will be omitted.

 * `merge()` (`Model`) – the `merge()` method may be used to merge properties from another model instance, into the current model instance, updating the current instance with the properties and property values of the other instance. The `merge()` method accepts the following arguments:

   * `model` (`Model`) – (required) the `model` argument must be used to specify the source model from which to merge the properties into the current model. The `model` must be of the same model instance type as the model that the properties and property values will be merged into, otherwise a `SemanticPyError` exception will be raised.

   * `properties` (`list[str]`) – (optional) the `properties` argument may be used to specify which properties should be merged from the source model instance into the current model instance. If the argument is not specified then all properties will be merged. Properties must be specified by their property names.

 * `reference()` (`Model`) – the `reference()` method may be used to create a reference to a model instance – useful for referencing a model entity from a property on another model instance without incorporating and nesting all of the properties of the referenced model instance.

 * `properties()` (`dict[str, object]`) – the `properties()` method may be used to obtain a dictionary representation of the current model instance, containing all of its properties as dictionary keys and property values as dictionary values. The `properties()` method accepts the following arguments:

   * `sorting` (`list[str]` | `dict[str, int]`) – (optional) the `sorting` argument may be used to specify a sort order that should be applied to the returned property data; sorting may be specified as a `list` of `str` values, where the list comprises the names of the properties in the order that they should be sorted into; alternatively, the `sorting` may be specified as a `dict` that comprise a list of property names associated with a sort order ranking specified as an integer where higher values integer sort later in the results.

   * `callback` (`callable`) – (optional) the `callback` argument may be used to specify a callback method that can be used to modify the value that is included in the returned container. The callback method must accept three arguments: the `key` (the name of the property as a `str` value), its `value` (an `object` value), and a reference to the current `container` (which will be either a `dict` or `list` reference). The callback must return the value to include in the container, either returning the `value` it was provided to leave the value as-is or to return a different value to change the value that will be included.

   * `attribute` (`str` | `int`) – (optional) the `attribute` argument may be used to control if the `callback` method should only be called for the named/indexed property/attribute, or to if the `callback` should be called for all properties. To limit calls to the `callback`, use the `attribute` argument to specify the name of the property or the index position that would need to match in order to call the `callback` method.

 * `property()` (`object`) – the `property()` method may be used to obtain a single named property from the current model instance, or if no property name is specified, a full clone of the current model instance. The `property()` method will accepts the following arguments:

   * `name` (`str`) – (optional) the `name` argument is used to specify the property to attempt to obtain from the model entity; if the named property exists, it will be returned, otherwise the value assigned to the `default` argument, which defaults to `None` will be returned instead; if no `name` is specified, then all current properties associated with the model entity will be returned;

   * `default` (`object`) – (optional) the `default` argument may be used to set an alternative return value for a call to the `property()` method if the method is unable to find and return the named property.

 * `documents()` (`list[Model]`) – the `documents()` method may be used to obtain a list of model entity
 documents from the current model instance; the `documents()` method accepts the following
 arguments, which control whether nodes of the following types will be including in the resulting list:

   * `blank` (`bool`) – (optional) to return any blank nodes within the current document, leave the
  `blank` argument set to its default value of `True` or to omit blank nodes, set to `False`;

   * `embedded` (`bool`) – (optional) to return any embedded nodes within the current document, leave the
 `embedded` argument set to its default value of `True` or to omit embedded nodes, set to `False`;

   * `referenced` (`bool`) – (optional) to return any referenced documents within the current document,
  leave the `referenced` argument to its default value of `True` or to omit any referenced nodes, set to `False`;

   * `filter` (`callable`) – (optional) to achieve finer-grained control over whether nodes are include in the resulting list, a callback method can be provided to the method via the `filter` argument; the callback method must take a reference to the current document, and its containing entity, and must return a `bool` value each time it is called; to include a node in the returned list via custom filtering, the method must return `True` and to omit the node, the method must return `False`.

### Properties

The `Model` class offers the following named properties in addition to the methods defined above:

 * `name` (`str`) – the `name` property provides access to the model instance's class name.

 * `label` (`str` | `None`) – the `label` property provides access to the model instance's assigned label, if any.

 * `ident` (`str` | `None`) – the `ident` property provides access to the model instance's assigned identifier, if any.

 * `is_blank` (`bool`) – the `is_blank` property may be used to determine if the current model instance is considered a blank node or not – a blank node is a model node without an assigned identifier. The `is_blank` property will be `True` if the node is blank (lacks an identifier) or `False` otherwise.

 * `is_cloned` (`bool`) – the `is_cloned` property may be used to determine if the current model instance is a clone of another node or not. The `is_cloned` property will be `True` if the current model instance is a clone of another or will be `False` otherwise.

 * `is_reference` (`bool`) – the `is_reference` property may be used to determine if the current model instance is a reference to another node or not. The `is_reference` property will be `True` if the current model instance is a reference to another or will be `False` otherwise.

 * `was_referenced` (`bool`) – the `was_referenced` property may be used to determine if one or more references have been created to the current model instance or not, via the `reference` method. The `was_referenced` property will be `True` if at least one reference has previously been generated for the current model instance via the `reference` method or will be `False` otherwise.

<a name="overwrite-modes"></a>
### Overwrite Modes

The overwrite behaviour mode for single-value properties can be changed from the default
behaviour of overwriting the value of single-value properties, to one of the following:

| Overwrite Mode   | Description                                                       |
|------------------|-------------------------------------------------------------------|
| `Allow`          | Default behaviour allows property values to be overwritten.       |
| `Warning`        | Warning emitted on value reassignment; value is overwritten.      |
| `Prevent`        | Warning emitted on attempted reassignment; value not overwritten. |
| `PreventQuietly` | No warning on attempted reassignment; value not overwritten.      |
| `Error`          | Error raised on attempted reassignment; value not overwritten.    |

The overwrite behaviour mode can be changed as shown below; changes to behaviour mode
will be remembered and applied to all `Model` classes until changed again or until the
models are torn-down via a call to `Model.teardown()`. The overwrite behaviour mode is
set via the `Model` class' `overwrite()` method by specifying the desired `OverwriteMode`
enumeration option, or its option name equivalent:

```python
from semanticpy import Model, OverwriteMode, SemanticPyError

# Instantiate the model with the desired profile
model = Model.factory(profile="linked-art")

# Create an instance to demonstrate the various single-value property overwrite modes
identifier = model.Identifier()

# Assign the initial value
identifier.content = "123"

assert identifier.content == "123"

# Change the overwrite mode to "Allow"
Model.configure(overwrite="Allow")
Model.configure(overwrite=OverwriteMode.Allow)

# Overwrite the value; the overwrite is allowed based on mode; no warning or error
identifier.content = "456"

assert identifier.content == "456"  # Note that the value change was allowed

# Change the overwrite mode to "Warning"
Model.configure(overwrite="Warning")
Model.configure(overwrite=OverwriteMode.Warning)

# Overwrite the value; the overwrite is allowed based on mode; a warning is emitted
identifier.content = "789"

assert identifier.content == "789"  # Note that the value change was allowed

# Change the overwrite mode to "Prevent"
Model.configure(overwrite="Prevent")
Model.configure(overwrite=OverwriteMode.Prevent)

# Overwrite the value; the overwrite is prevented based on mode; a warning is emitted
identifier.content = "321"

assert identifier.content == "789"  # Note that the value change was prevented

# Change the overwrite mode to "PreventQuietly"
Model.configure(overwrite="PreventQuietly")
Model.configure(overwrite=OverwriteMode.PreventQuietly)

# Overwrite the value; the overwrite is prevented based on mode; no warning is emitted
identifier.content = "321"

assert identifier.content == "789"  # Note that the value change was prevented

# Change the overwrite mode to "Error"
Model.configure(overwrite="Error")
Model.configure(overwrite=OverwriteMode.Error)

# Attempt to overwrite; the overwrite is prevented based on mode; an error is raised
try:
  identifier.content = "321"
except SemanticPyError:
  pass

assert identifier.content == "789"  # Note that the value change was prevented

Model.teardown()
```

⚠️ Note: The overwrite behaviour mode does not affect model properties which accept
multiple values; in the case of multi-value properties, all assignments result in the
assigned value being added to the list of values held by the property according to the
default behaviour; any later value assignment simply appends the value to the list,
rather than overwriting earlier values. To adjust the behavior of appending values to
multi-value properties, see the [Appending Modes](#appending-modes) section below.

<a name="appending-modes"></a>
### Appending Modes

The appending behaviour mode for multiple-value properties can be changed from the default
behaviour of always appending the value to the multiple-value properties' list:

| Appending Mode | Description                                                       |
|----------------|-------------------------------------------------------------------|
| `Always`       | The default behaviour always appends values to the list.          |
| `Unique`       | Appends only unique values to the list, preventing duplicates.    |

The appending behaviour mode can be changed as shown below; changes to behaviour mode
will be remembered and applied to all `Model` classes until changed again or until the
models are torn-down via a call to `Model.teardown()`. The appending behaviour mode is
set via the `Model` class' `configure()` method by specifying the desired `AppendingMode`
enumeration option, or its option name equivalent.

An example of the "Always" appending mode (the default) is shown below, where when a value
is assigned to a multiple-value property, that it is appended to the list of values held
by the property regardless of whether that value has already been assigned previously to
the property or not:

```python
from semanticpy import Model, AppendingMode

# Instantiate the model with the desired profile
model = Model.factory(profile="linked-art")

# Configure the appending mode to "Always" (this is the default value, so doesn't need
# to be set unless the appending mode has been changed and you want to change it back)
# The option can be set via name or enumeration option; all of these ways are valid:
Model.configure(appending="Always")
Model.configure(appending="always")
Model.configure(appending="ALWAYS")
Model.configure(appending=AppendingMode.Always)

# Create an instance to demonstrate the various multiple-value property appending modes
object = model.HumanMadeObject()

# Create an instance to demonstrate the various multiple-value property appending modes
identifier = model.Identifier(content="123")

assert identifier.content == "123"

object.identified_by = identifier

assert len(object.identified_by) == 1
assert object.identified_by[0] is identifier

object.identified_by = identifier

assert len(object.identified_by) == 2
assert object.identified_by[1] is identifier
```

An example of the "Unique" appending mode is shown below, where when a value is assigned
to a multiple-value property, it will only be appended to the list of values held by the
property if the value has not been assigned previously to the property; if the value has
already been assigned, the duplicate assignment is silently ignored and is not appended:

```python
from semanticpy import Model, AppendingMode

# Instantiate the model with the desired profile
model = Model.factory(profile="linked-art")

# Configure the append mode to "Unique" to only allow unique values to be appended
# The option can be set via name or enumeration option; all of these ways are valid:
Model.configure(appending="Unique")
Model.configure(appending="unique")
Model.configure(appending="UNIQUE")
Model.configure(appending=AppendingMode.Unique)

# Create an instance to demonstrate the various multiple-value property appending modes
object = model.HumanMadeObject()

# Create an instance to demonstrate the various multiple-value property appending modes
identifier = model.Identifier(content="123")

assert identifier.content == "123"

object.identified_by = identifier

assert len(object.identified_by) == 1
assert object.identified_by[0] is identifier

object.identified_by = identifier

assert len(object.identified_by) == 1
assert object.identified_by[0] is identifier

Model.teardown()
```

<a name="code-formatting"></a>
### Code Formatting

The SemanticPy library adheres to the code formatting specifications set out in PEP-8, which are verified and applied by the _Black_ code formatting tool. Whenever code changes are made to the library, one needs to ensure that the code conforms to these code formatting specifications. To simplify this, the provided `Dockerfile` creates an image that supports running the _Black_ code formatting tool against the latest version of the code, and will report back if any issues are found. To run the code formatting checks, perform the following commands, which will build the Docker image via `docker compose build` and then run the tests via `docker compose run black` – the output of running the formatting checks will be displayed:

```shell
$ docker compose build
$ docker compose run black
```

If any code formatting issues are found, it is possible to run _Black_ so that it will
automatically reformat the affected files; this can be achieved as follows:

```shell
$ docker compose run black --reformat
```

The above command will reformat any files that contained code formatting issues, and will
report back on what changes were made; once the code has been automatically reformatted,
it will continue to pass the formatting checks until any future code changes that fall
outside of the PEP-8 and _Black_ code formatting specifications.

<a name="code-linting"></a>
### Code Linting

The SemanticPy library adheres to the code linting specifications set out in PEP-8, which are verified and applied by the _PyFlakes_ code linting tool. Whenever code changes are made to the library, one needs to ensure that the code conforms to these code formatting specifications. To simplify this, the provided `Dockerfile` creates an image that supports running the _PyFlakes_ code linting tool against the latest version of the code, and will report back if any issues are found. To run the code linting checks, perform the following commands, which will build the Docker image via `docker compose build` and then run the tests via `docker compose run flakes` – the output of running the linting checks will be displayed:

```shell
$ docker compose build
$ docker compose run flakes
```

If any code linting issues are found, such as references to undefined names, or unused imports, each issue will need to be addressed by making the necessary code changes and re-testing with `PyFlakes`, before the library changes can be submitted for review.

<a name="unit-tests"></a>
### Unit Tests

The SemanticPy library includes a suite of comprehensive unit tests which ensure that
the library functionality operates as expected. The unit tests were developed with and
are run via `pytest`.

To ensure that the unit tests are run within a predictable runtime environment where all
of the necessary dependencies are available, a [Docker](https://www.docker.com) image is
created within which the tests are run. To run the unit tests, ensure Docker and Docker
Compose is [installed](https://docs.docker.com/engine/install/), and perform the
following commands, which will build the Docker image via `docker compose build` and
then run the tests via `docker compose run` – the output the tests will be displayed:

```shell
$ docker compose build
$ docker compose run tests
```

To run the unit tests with optional command line arguments being passed to `pytest`,
append the relevant arguments to the `docker compose run tests` command, as follows, for
example passing `-v` to enable verbose output and `-s` to print standard output:

```shell
$ docker compose run tests -v -s
```

See the documentation for [PyTest](https://docs.pytest.org/en/latest/) regarding
available optional command line arguments.

### Copyright & License Information

Copyright © 2022–2026 Daniel Sissman; licensed under the MIT License.