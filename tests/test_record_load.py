import logging

import semanticpy

from semanticpy import Model, Node, Nodes

logger = logging.getLogger(__name__)


def test_record_load(factory: callable, data: callable, path: callable):
    # Initialise the Model using a named profile; in this case specify the "linked-art"
    # profile which is provided with the library so only needs specifying by its name.
    # Other profiles may be used to create models of other types; see the *Profiles*
    # section in the README for more information. The factory method dynamically creates
    # the required model class types and adds them to the scope defined by the `globals`
    # argument making the class types available for use just by referencing their names:
    model = factory(profile="linked-art")

    # Open the record; this could be a JSON-LD record stored in a locally accessible
    # filesystem or on a web server accessible via a HTTP(S) URL without authentication:
    artefact = semanticpy.Model.open(path("examples/object.json"))

    # Ensure that the opened JSON-LD record is of the type expected
    assert isinstance(artefact, model.HumanMadeObject)
    assert isinstance(artefact, Model)
    assert isinstance(artefact, Node)

    # Ensure that the record @context property is as expected
    assert artefact.context == "https://linked.art/ns/v1/linked-art.json"

    # Ensure that the record entity type is as expected
    assert artefact.typed == "E22"  # E22 (HumanMadeObject)

    # Ensure that the record type name is as expected
    assert artefact.type == "HumanMadeObject"

    # Ensure that the record type name is as expected
    assert artefact.name == "HumanMadeObject"

    # Ensure that the record identifier (`id` property value) is as expected
    assert artefact.ident == "https://data.example.org/object/1"

    assert isinstance(artefact.classified_as, list)
    assert isinstance(artefact.classified_as, Nodes)
    assert len(artefact.classified_as) == 2

    assert artefact.classified_as[0].equals(
        model.Type(
            ident="http://vocab.getty.edu/aat/300133025",
            label="Works of Art",
        )
    )

    assert model.Type(
        ident="http://vocab.getty.edu/aat/300133025",
        label="Works of Art",
    ).equals(artefact.classified_as[0])

    assert artefact.classified_as[1].equals(
        model.Type(
            ident="http://vocab.getty.edu/aat/300033618",
            label="Paintings (Visual Works)",
        )
    )

    assert model.Type(
        ident="http://vocab.getty.edu/aat/300033618",
        label="Paintings (Visual Works)",
    ).equals(artefact.classified_as[1])

    assert isinstance(artefact.identified_by, list)
    assert isinstance(artefact.identified_by, Nodes)
    assert len(artefact.identified_by) == 3

    assert artefact.identified_by[0].equals(
        model.Name(
            label="Name of Artwork",
            content="A Painting",
        )
    )

    assert model.Name(
        label="Name of Artwork",
        content="A Painting",
    ).equals(artefact.identified_by[0])

    # Find the name by its type
    name = artefact.identified_by.first(type="Name")
    assert isinstance(name, model.Name)
    assert isinstance(name, Model)
    assert isinstance(name, Node)
    assert name.label == "Name of Artwork"
    assert name.content == "A Painting"

    artefact.identified_by[1].equals(
        model.Identifier(
            label="Accession Number for Artwork",
            content="1982.A.39",
        )
    )

    assert model.Identifier(
        label="Accession Number for Artwork",
        content="1982.A.39",
    ).equals(artefact.identified_by[1])

    # Find the identifier by its type
    identifier = artefact.identified_by.first(type="Identifier")
    assert isinstance(identifier, model.Identifier)
    assert isinstance(identifier, Model)
    assert isinstance(identifier, Node)
    assert identifier.label == "Accession Number for Artwork"
    assert identifier.content == "1982.A.39"

    # Find the identifier by the desired classification
    identifier = artefact.identified_by.first(
        classified_as=model.Type(ident="http://vocab.getty.edu/aat/300312355")
    )
    assert isinstance(identifier, model.Identifier)
    assert identifier.label == "Accession Number for Artwork"
    assert identifier.content == "1982.A.39"

    # Find the identifier by the desired classification
    identifier = artefact.identified_by.first(
        classified_as=dict(
            ident="http://vocab.getty.edu/aat/300417447",
            label="Catalog Number",
        )
    )
    assert isinstance(identifier, model.Identifier)
    assert isinstance(identifier, Model)
    assert isinstance(identifier, Node)
    assert identifier.label == "Catalog Number for Artwork"
    assert identifier.content == "X1290231.A72"

    assert isinstance(artefact.produced_by, model.Production)
    assert isinstance(artefact.produced_by.timespan, model.TimeSpan)

    assert artefact.produced_by.timespan.begin_of_the_begin == "2026-01-01T00:00:00"
    assert artefact.produced_by.timespan.end_of_the_end == "2026-12-31T23:59:59"
