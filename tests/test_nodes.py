import pytest

from semanticpy.types import Node, Nodes


@pytest.fixture(name="node", scope="function")
def test_node_initialisation():
    """Test Node class initialisation."""

    node = Node(data=dict(one=1, two=2, three="three"))

    assert isinstance(node, Node)

    return node


@pytest.fixture(name="nodes", scope="function")
def test_nodes_initialisation(node: Node):
    """Test Nodes class initialisation."""

    nodes = Nodes([node])

    assert isinstance(nodes, Nodes)

    return nodes


def test_nodes_length(nodes: Node):
    """Test Node class length."""

    assert isinstance(nodes, Nodes)

    assert len(nodes) == 1


def test_nodes_lists(node: Node, nodes: Nodes):
    """Test adding Node entities to a list."""

    assert isinstance(nodes, list)
    assert isinstance(nodes, Nodes)
    assert len(nodes) == 1

    assert node in nodes
    assert nodes[0] is node
    assert nodes[0] == node

    new_node = Node(data=node.properties())

    assert isinstance(new_node, Node)
    assert new_node is not node
    assert new_node.equals(node)

    if not new_node in nodes:
        nodes.append(new_node)

    assert len(nodes) == 1
    assert node in nodes

    assert nodes[0] is node
    assert nodes[0].equals(node)

    assert nodes[0] is not new_node
    assert nodes[0].equals(new_node)
