import logging
import semanticpy

logger = logging.getLogger(__name__)


def test_record_create(factory: callable, data: callable):
    # Initialise the Model using a named profile; in this case specify the "linked-art"
    # profile which is provided with the library so only needs specifying by its name.
    # Other profiles may be used to create models of other types; see the *Profiles*
    # section in the README for more information. The factory method dynamically creates
    # the required model class types and adds them to the scope defined by the `globals`
    # argument making the class types available for use just by referencing their names:
    model = factory(profile="linked-art", globals=globals())

    # Register a URI prefix and its corresponding URI; prefixes can be registered with
    # or without the ":" suffix, but a ":" must be used when the prefix is used in place
    # of the URI in identifiers referenced elsewhere when assembling documents.
    semanticpy.Model.prefix("aat", "http://vocab.getty.edu/aat/")

    assert getattr(model, "HumanMadeObject")

    # Create a HumanMadeObject (HMO) model instance
    hmo = HumanMadeObject(
        ident="https://example.org/object/1",
        label="Example Object #1",
    )

    assert isinstance(hmo, HumanMadeObject)

    # Assign a classification of "Works of Art" to the HMO as per the Linked.Art model
    hmo.classified_as = Type(
        ident="aat:300133025",
        label="Works of Art",
    )

    # As this example HMO represents a painting, add a classification of "Paintings" as
    # per the Linked.Art model to specify the type of artwork that this HMO represents:
    hmo.classified_as = typed = Type(
        ident="http://vocab.getty.edu/aat/300033618",
        label="Paintings (Visual Works)",
    )

    # Classify the type classification above as the "type of work" as per the model:
    typed.classified_as = Type(
        ident="http://vocab.getty.edu/aat/300435443",
        label="Type of Work",
    )

    # Include a Name node on the HMO to carry a name of the artwork
    hmo.identified_by = name = Name(
        label="Name of Artwork",
    )

    name.content = "A Painting"

    # Include an Identifier node on the HMO to carry an identifier of the artwork
    hmo.identified_by = identifier = Identifier(
        label="Accession Number for Artwork",
    )

    identifier.content = "1982.A.39"

    hmo.produced_by = production = Production()

    production.timespan = timespan = TimeSpan()

    timespan.begin_of_the_begin = "2026-01-01T00:00:00"

    timespan.end_of_the_end = "2026-12-31T23:59:59"

    # Serialise the model into JSON, in this case optionally specifying an indent of two
    # spaces per level of nesting to make the JSON easier to read; by default the method
    # will not indent, compacting the JSON to save storage and transmission overhead:
    serialised = hmo.json(indent=2)

    assert isinstance(serialised, str)

    # For the purposes of this example, print the JSON for review; the JSON could also
    # be saved to a file, stored in a database, or used in some other way:
    content: str = data("examples/object.json")

    assert isinstance(content, str)

    assert content == serialised
