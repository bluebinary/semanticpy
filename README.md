# SemanticPy

The SemanticPy library for Python provides a simplified and consistent way to create JSON-LD documents from Python source code constructs such as classes and properties. In addition to simplifying the creation of JSON-LD documents, the library validates the model as it is being created, ensuring that properties can only be assigned valid values that are of the type or within the expected range defined in the model profile.

The SemanticPy library also supports loading JSON-LD documents from disk or the web, with support for automatically dereferencing linked documents, and enables these documents and the data they contain to be parsed and used.

### Example

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

# Create a HumanMadeObject (HMO) model instance
hmo = HumanMadeObject(
    ident = "https://example.org/object/1",
    label = "Example Object #1",
)

# Assign a classification of "Works of Art" to the HMO as per the Linked.Art model
hmo.classified_as = Type(
    ident = "http://vocab.getty.edu/aat/300133025",
    label = "Works of Art",
)

# As this example HMO represents a painting, add a classification of "Paintings" as per
# the Linked.Art model to specify the type of artwork that this HMO represents:
hmo.classified_as = typed = Type(
    ident = "http://vocab.getty.edu/aat/300033618",
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

### Requirements

The SemanticPy library has been tested to work with Python 3.10, 3.11, 3.12 and 3.13, but is not compatible with earlier Python 3 versions such as 3.9, 3.8, or 3.7. It was not designed to work with Python 2 or earlier.

### Installation

The SemanticPy library is available from the PyPi repository, so may be added to a project's dependencies via its `requirements.txt` file or similar by referencing the SemanticPy library's name, `semanticpy`, or the library may be installed directly onto your local development system using `pip install` by entering the following command:

	$ pip install semanticpy

### Methods

The primary interface to the SemanticPy library is its `Model` class which offers the following methods:

 * `factory` – the `factory` method is used to initialise the model for use.
 * `teardown` – the `teardown` method is used to de-initialise the model, reversing the setup performed by the `factory` method.
 * `extend` – the `extend` method is used to support extending the factory-generated model with additional model subclasses, and optionally, additional model-wide properties.
 * `entity` – the `entity` method may be used to obtain the `type` reference for a named model entity, from which a new instance of that named model entity may be created.
 * `clone` – the `clone` method may be used to clone the current model instance, creating a separate copy of the instance in memory which may be used or modified without affecting the original.
 * `reference` – the `reference` method may be used to create a reference to a model instance – useful for referencing a model entity from a property on another model instance without incorporating and nesting all of the properties of the referenced model instance.
 * `properties` – the `properties` method may be used to obtain a dictionary representation of the current model instance, containing all of its properties as dictionary keys and property values as dictionary values.
 * `property` – the `property` method may be used to obtain a single named property from the current model instance, or if no property name is specified, a full clone of the current model instance.
 * `documents` – the `documents` method may be used to obtain a list of model entity documents from the current model instance.

### Properties

The `Model` class offers the following named properties in addition to the methods defined above:

 * `name` – the `name` (`str`) property provides access to the model instance's class name.
 * `label` – the `label` (`str` | `None`) property provides access to the model instance's assigned label, if any.
 * `ident` – the `ident` (`str` | `None`) property provides access to the model instance's assigned identifier, if any.
 * `is_blank` – the `is_blank` (`bool`) property may be used to determine if the current model instance is considered a blank node or not – a blank node is a model node without an assigned identifier. The `is_blank` property will be `True` if the node is blank (lacks an identifier) or `False` otherwise.
 * `is_cloned` – the `is_cloned` (`bool`) property may be used to determine if the current model instance is a clone of another node or not. The `is_cloned` property will be `True` if the current model instance is a clone of another or will be `False` otherwise.
 * `is_reference` – the `is_reference` (`bool`) property may be used to determine if the current model instance is a reference to another node or not. The `is_reference` property will be `True` if the current model instance is a clone of another or will be `False` otherwise.
 * `was_referenced` – the `was_referenced` (`bool`) property may be used to determine if one or more references have been created to the current model instance or not, via the `reference` method. The `was_referenced` property will be `True` if at least one reference has previously been generated for the current model instance via the `reference` method or will be `False` otherwise.

### License and Copyright Information

Copyright © 2022–2025 Daniel Sissman; licensed under the MIT License.