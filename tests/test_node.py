import pytest

import semanticpy
from semanticpy.types import Node


@pytest.fixture(name="node", scope="function")
def test_node_initialisation():
    """Test Node class initialisation."""

    node = Node(data=dict(one=1, two=2, three="three"))

    assert isinstance(node, Node)

    return node


def test_node_len(node: Node):
    """Test Node class length."""

    assert isinstance(node, Node)

    assert len(node) == 3


def test_node_attribute_access(node: Node):
    """Test Node class attribute access."""

    assert isinstance(node, Node)

    assert hasattr(node, "one")
    assert isinstance(node.one, int)
    assert node.one == 1

    assert hasattr(node, "two")
    assert isinstance(node.two, int)
    assert node.two == 2

    assert hasattr(node, "three")
    assert isinstance(node.three, str)
    assert node.three == "three"


def test_node_attribute_assignment(node: Node):
    """Test Node class attribute assignment."""

    assert isinstance(node, Node)

    node.four = 4

    node.five = five = Node()

    five.six = "six"

    assert hasattr(node, "four")
    assert isinstance(node.four, int)
    assert node.four == 4

    assert hasattr(node, "five")
    assert isinstance(node.five, Node)

    assert hasattr(node.five, "six")
    assert isinstance(node.five.six, str)
    assert node.five.six == "six"


def test_node_identity():
    """Test Node identity."""

    # Create a new Node instance using the attribute properties and values of another
    node1 = Node(data=dict(one=1, two="two"))
    node2 = Node(data=dict(one=1, two="two"))

    assert isinstance(node1, Node)
    assert isinstance(node2, Node)

    # Ensure the two nodes do not report having the same identity
    assert node1 is not node2
    assert not id(node1) == id(node2)
    assert not hash(node1) == hash(node2)

    assert node2 is not node1
    assert not id(node2) == id(node1)
    assert not hash(node2) == hash(node1)


def test_node_equality():
    """Test Node equality."""

    # Create a new Node instance using the attribute properties and values of another
    node1 = Node(data=dict(one=1, two="two", three="three"))
    node2 = Node(data=dict(one=1, two="two"))

    assert isinstance(node1, Node)
    assert isinstance(node2, Node)

    # Ensure the two nodes do not report having the same identity
    assert node1 is not node2
    assert node2 is not node1

    # Ensure the two nodes, report being equal to each other as they have the same data
    assert node1.equals(node2)
    assert node2.equals(node1)


def test_node_equality_strict():
    """Test Node equality in strict mode."""

    # Create a new Node instance using the attribute properties and values of another
    node1 = Node(data=dict(one=1, two="two", three="three"))
    node2 = Node(data=dict(one=1, two="two"))

    assert isinstance(node1, Node)
    assert isinstance(node2, Node)

    # Ensure the two nodes do not report having the same identity
    assert node1 is not node2
    assert node2 is not node1

    # Ensure the two nodes, report being equal to each other as they have the same data
    assert not node1.equals(node2, strict=True)  # not equal as node1.three cannot match
    assert not node2.equals(node1, strict=True)  # not equal as node1.three cannot match


def test_node_merge(data: callable):
    """Test Node merging."""

    model = semanticpy.Model.factory(profile="linked-art")

    operson = model.Person(
        ident="https://data.example.org/person/123",
        label="Person 123",
    )

    operson.classified_as = model.Type(
        ident="http://vocab.getty.edu/aat/300025103",
        label="Artists (Visual Artists)",
    )

    operson.referred_to_by = name = model.Name(
        ident="https://data.example.org/person/123/name",
        label="Person 123 Name",
    )

    name.classified_as = model.Type(
        ident="http://vocab.getty.edu/aat/300404670",
        label="Preferred Term",
    )

    name.content = "Person 123's Name"

    nperson = model.Person(
        ident="https://data.example.org/person/123",
        label="Person 123",
    )

    nperson.classified_as = model.Type(
        ident="http://vocab.getty.edu/aat/300025687",
        label="Photographers",
    )

    nperson.referred_to_by = name = model.Name(
        ident="https://data.example.org/person/123/name-other",
        label="Person 123 Name Other",
    )

    name.content = "Person 123's Name Other"

    # Ensure that the original Person entity's classified_as list has 1 item
    assert isinstance(operson.classified_as, list)
    assert len(operson.classified_as) == 1

    # Ensure that the new Person entity's classified_as list has 1 item
    assert isinstance(nperson.classified_as, list)
    assert len(nperson.classified_as) == 1

    # Ensure that the original Person entity's referred_to_by list has 1 item
    assert isinstance(operson.referred_to_by, list)
    assert len(operson.referred_to_by) == 1

    # Ensure that the new Person entity's referred_to_by list has 1 item
    assert isinstance(nperson.referred_to_by, list)
    assert len(nperson.referred_to_by) == 1

    # Merge the new Person entity into the original Person entity
    mperson = operson.merge(nperson)

    # After merge ensure the merged Person entity's classified_as list still has 2 items
    assert isinstance(mperson.classified_as, list)
    assert len(mperson.classified_as) == 2

    # Ensure that the item is as expected – a reference to the pre-existing item
    assert mperson.classified_as[0] is operson.classified_as[0]
    assert mperson.classified_as[1] is nperson.classified_as[0]

    # After merge ensure that the merged Person entity's referred_to_by list has 2 items
    assert isinstance(mperson.referred_to_by, list)
    assert len(mperson.referred_to_by) == 2

    # Ensure that the two items are as expected – references to the pre-existing items
    assert mperson.referred_to_by[0] is operson.referred_to_by[0]
    assert mperson.referred_to_by[1] is nperson.referred_to_by[0]

    # Ensure that the merged record has the expected structure and content
    assert mperson.json(indent=2) == data("examples/merged.json")


def test_node_merge_for_specified_properties(data: callable):
    """Test Node merging for specified properties."""

    model = semanticpy.Model.factory(profile="linked-art")

    operson = model.Person(
        ident="https://data.example.org/person/123",
        label="Person 123",
    )

    operson.classified_as = model.Type(
        ident="http://vocab.getty.edu/aat/300025103",
        label="Artists (Visual Artists)",
    )

    operson.referred_to_by = name = model.Name(
        ident="https://data.example.org/person/123/name",
        label="Person 123 Name",
    )

    name.classified_as = model.Type(
        ident="http://vocab.getty.edu/aat/300404670",
        label="Preferred Term",
    )

    name.content = "Person 123's Name"

    nperson = model.Person(
        ident="https://data.example.org/person/123",
        label="Person 123",
    )

    nperson.classified_as = model.Type(
        ident="http://vocab.getty.edu/aat/300025687",
        label="Photographers",
    )

    nperson.referred_to_by = name = model.Name(
        ident="https://data.example.org/person/123/name-other",
        label="Person 123 Name Other",
    )

    name.content = "Person 123's Name Other"

    # Ensure that the original Person entity's classified_as list has 1 item
    assert isinstance(operson.classified_as, list)
    assert len(operson.classified_as) == 1

    # Ensure that the new Person entity's classified_as list has 1 item
    assert isinstance(nperson.classified_as, list)
    assert len(nperson.classified_as) == 1

    # Ensure that the original Person entity's referred_to_by list has 1 item
    assert isinstance(operson.referred_to_by, list)
    assert len(operson.referred_to_by) == 1

    # Ensure that the new Person entity's referred_to_by list has 1 item
    assert isinstance(nperson.referred_to_by, list)
    assert len(nperson.referred_to_by) == 1

    # Merge the new Person entity into the original Person entity, but limit the merge
    # to the specified model properties only, skipping any other model properties:
    mperson = operson.merge(nperson, properties=["classified_as"])

    # After merge ensure the merged Person entity's classified_as list still has 2 items
    assert isinstance(mperson.classified_as, list)
    assert len(mperson.classified_as) == 2

    # Ensure that the item is as expected – a reference to the pre-existing item
    assert mperson.classified_as[0] is operson.classified_as[0]
    assert mperson.classified_as[1] is nperson.classified_as[0]

    # After merge ensure the merged Person entity's referred_to_by list still has 1 item
    # because the referred_to_by property was not in the list of properties to merge:
    assert isinstance(mperson.referred_to_by, list)
    assert len(mperson.referred_to_by) == 1

    # Ensure that the item is as expected – a reference to the pre-existing item
    assert mperson.referred_to_by[0] is operson.referred_to_by[0]

    # Ensure that the merged record has the expected structure and content
    assert mperson.json(indent=2) == data("examples/merged-specified-properties.json")
