import logging

from semanticpy import Model, Node

logger = logging.getLogger(__name__)


def test_record_save_not_extended(factory: callable, data: callable, path: callable):
    # Initialise the Model using a named profile; in this case specify the "linked-art"
    # profile which is provided with the library so only needs specifying by its name.
    # Other profiles may be used to create models of other types; see the *Profiles*
    # section in the README for more information. The factory method dynamically creates
    # the required model class types and adds them to the object returned from the call:
    model = factory(profile="linked-art")

    # Create a new Model instance
    artefact = model.HumanMadeObject(
        ident="https://data.example.org/object/123",
        label="Example Object 123",
    )

    # Ensure that the created JSON-LD record is of the type expected
    assert isinstance(artefact, model.HumanMadeObject)
    assert isinstance(artefact, Model)
    assert isinstance(artefact, Node)

    # Add an example property value to the Model instance
    artefact.classified_as = model.Type(
        ident="http://vocab.getty.edu/aat/300133025",
        label="Works of Art",
    )

    # Save the Model instance object to storage
    filepath: str = artefact.save("/tmp/object.json", indent=2)

    # Ensure that the call to the .save() method returned the expected file path
    assert isinstance(filepath, str)

    # Load the contents of the saved file
    contents: str = data(filepath)
    assert isinstance(contents, str)

    # Ensure that the contents of the saved file match the pre-saved example file
    assert contents == data("examples/saved.json")


def test_record_save_with_extended(factory: callable, data: callable, path: callable):
    # Initialise the Model using a named profile; in this case specify the "linked-art"
    # profile which is provided with the library so only needs specifying by its name.
    # Other profiles may be used to create models of other types; see the *Profiles*
    # section in the README for more information. The factory method dynamically creates
    # the required model class types and adds them to the object returned from the call:
    model = factory(profile="linked-art")

    # Extend the model by registering custom schema properties
    # Register the 'test:related' custom property on the HumanMadeObject entity type
    Model.extend(
        model.HumanMadeObject,
        properties=dict(
            related=dict(
                canonical="related",
                namespace="test",
                individual=False,
                range=model.HumanMadeObject,
                sorting=10000,
            ),
        ),
    )

    # Create a new Model instance
    artefact = model.HumanMadeObject(
        ident="https://data.example.org/object/123",
        label="Example Object 123",
    )

    # Ensure that the created JSON-LD record is of the type expected
    assert isinstance(artefact, model.HumanMadeObject)
    assert isinstance(artefact, Model)
    assert isinstance(artefact, Node)

    # Add an example property value to the Model instance
    artefact.classified_as = model.Type(
        ident="http://vocab.getty.edu/aat/300133025",
        label="Works of Art",
    )

    artefact.related = model.HumanMadeObject(
        ident="https://data.example.org/object/456",
        label="Related Object 456",
    )

    artefact.related = model.HumanMadeObject(
        ident="https://data.example.org/object/789",
        label="Related Object 789",
    )

    # Save the Model instance object to storage
    filepath: str = artefact.save("/tmp/saved-extended.json", indent=2, overwrite=True)

    # Ensure that the call to the .save() method returned the expected file path
    assert isinstance(filepath, str)

    # Load the contents of the saved file
    contents: str = data(filepath)
    assert isinstance(contents, str)

    # Ensure that the contents of the saved file match the pre-saved example file
    assert contents == data("examples/saved-extended.json")
