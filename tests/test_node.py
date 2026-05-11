import pytest

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


def test_node_equality():
    """Test Node equality."""

    # Create a new Node instance using the attribute properties and values of another
    node1 = Node(data=dict(one=1, two="two"))
    node2 = Node(data=dict(one=1, two="two"))

    assert isinstance(node1, Node)
    assert isinstance(node2, Node)

    # Ensure the two nodes do not report having the same identity
    assert node1 is not node2

    # Ensure the two nodes, report being equal to each other as they have the same data
    assert node1.equals(node2)
