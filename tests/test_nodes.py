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


def test_nodes_append(node: Node, nodes: Nodes):
    """Test appending Node entities to a Nodes list."""

    assert isinstance(nodes, list)
    assert isinstance(nodes, Nodes)
    assert len(nodes) == 1

    assert node in nodes
    assert nodes[0] is node
    assert nodes[0] == node

    new_node = Node(data=node.properties(), four=4.567)

    assert isinstance(new_node, Node)
    assert new_node is not node
    assert node is not new_node
    assert new_node.equals(node, strict=True) is False
    assert new_node.equals(node, strict=False) is True
    assert node.equals(new_node, strict=True) is False
    assert node.equals(new_node, strict=False) is True

    if not new_node in nodes:
        nodes.append(new_node)

    assert len(nodes) == 2
    assert node in nodes
    assert new_node in nodes

    assert nodes[0] is node
    assert nodes[0].equals(node, strict=True)
    assert nodes[0].equals(node, strict=False)

    assert nodes[1] is new_node
    assert nodes[1].equals(new_node, strict=True)
    assert nodes[1].equals(new_node, strict=False)


def test_nodes_append_duplicate_node(node: Node, nodes: Nodes):
    """Test appending duplicate Node entities to a Nodes list."""

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
    assert new_node.equals(node, strict=True)
    assert new_node.equals(node, strict=False)

    # Check if an equivalent Node is already present or not in the Nodes list
    if not new_node in nodes:
        nodes.append(new_node)

    assert len(nodes) == 1
    assert node in nodes
    # The Node
    # However, from an identity perspective, they are not the same
    assert new_node in nodes

    assert nodes[0] is node
    assert nodes[0].equals(node)
    assert nodes[0].equals(node, strict=True)
    assert nodes[0].equals(node, strict=False)

    assert nodes[0] is not new_node
    assert nodes[0].equals(new_node)
    assert nodes[0].equals(new_node, strict=True)
    assert nodes[0].equals(new_node, strict=False)


def test_nodes_filter():
    nodes: Nodes = Nodes()

    nodes.append(Node(a=1, b=2, c=3))
    nodes.append(Node(a=1, b=2, c=4))
    nodes.append(Node(a=1, b=3, c=5))

    filtered = nodes.filter(a=1, b=2)

    assert isinstance(filtered, list)
    assert isinstance(filtered, Nodes)
    assert len(filtered) == 2
    assert filtered[0] is nodes[0]
    assert filtered[1] is nodes[1]

    filtered = nodes.filter(c=5)

    assert isinstance(filtered, list)
    assert isinstance(filtered, Nodes)
    assert len(filtered) == 1
    assert filtered[0] is nodes[2]
