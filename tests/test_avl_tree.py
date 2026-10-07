"""
Unit tests for AVL Tree implementation.
Tests: Insert, Search, Delete, Rotations (LL, RR, LR, RL), Traversals, and Duplicate SKU rejection.
"""

import pytest
from backend.dsa.avl_tree import AVLTree


def test_avl_insert_and_search():
    tree = AVLTree()
    item1 = {"sku": "SKU001", "name": "Keyboard", "quantity": 10, "location": "Rack A", "priority": 5}
    success, msg, comps = tree.insert(item1)
    assert success is True
    assert tree.size == 1

    found, search_comps, path = tree.search("SKU001")
    assert found is not None
    assert found["name"] == "Keyboard"
    assert "SKU001" in path


def test_avl_duplicate_sku_rejection():
    tree = AVLTree()
    item = {"sku": "SKU001", "name": "Keyboard", "quantity": 10, "location": "Rack A"}
    tree.insert(item)
    success, msg, comps = tree.insert(item)
    assert success is False
    assert "Duplicate SKU" in msg
    assert tree.size == 1


def test_avl_search_non_existent():
    tree = AVLTree()
    tree.insert({"sku": "SKU002", "name": "Mouse", "quantity": 5})
    found, comps, path = tree.search("SKU999")
    assert found is None


def test_avl_rotations_and_balancing():
    """
    Test that inserting keys in ascending order causes Left Rotations (RR case)
    and maintains AVL height constraint.
    """
    tree = AVLTree()
    # Inserting in ascending order without balancing would become a linked list of height 5.
    # In AVL, height of 5 nodes should be at most 3.
    for i in range(1, 6):
        tree.insert({"sku": f"SKU00{i}", "name": f"Item {i}", "quantity": i})

    assert tree.root is not None
    assert tree.root.height <= 3
    # Check balance factor of every node is in {-1, 0, 1}
    def check_balance(node):
        if not node:
            return
        assert abs(node.balance_factor()) <= 1
        check_balance(node.left)
        check_balance(node.right)

    check_balance(tree.root)
    assert tree.rotation_stats["left_rotations"] > 0


def test_avl_left_right_rotation():
    tree = AVLTree()
    # Sequence to trigger Left-Right rotation (LR)
    tree.insert({"sku": "SKU030", "name": "Thirty"})
    tree.insert({"sku": "SKU010", "name": "Ten"})
    tree.insert({"sku": "SKU020", "name": "Twenty"})

    assert tree.root.sku == "SKU020"
    assert tree.root.left.sku == "SKU010"
    assert tree.root.right.sku == "SKU030"
    assert tree.rotation_stats["left_right_rotations"] == 1


def test_avl_delete_leaf_and_internal_nodes():
    tree = AVLTree()
    for i in ["SKU010", "SKU020", "SKU030", "SKU040", "SKU050"]:
        tree.insert({"sku": i, "name": f"Item {i}"})

    assert tree.size == 5

    # Delete non-existent
    del_ok, msg, _ = tree.delete("SKU999")
    assert del_ok is False

    # Delete existing node
    del_ok, msg, _ = tree.delete("SKU020")
    assert del_ok is True
    assert tree.size == 4

    found, _, _ = tree.search("SKU020")
    assert found is None

    # Verify remaining order via inorder traversal
    inorder = tree.inorder_traversal()
    skus = [it["sku"] for it in inorder]
    assert skus == ["SKU010", "SKU030", "SKU040", "SKU050"]


def test_avl_traversals():
    tree = AVLTree()
    items = [
        {"sku": "SKU003", "name": "C"},
        {"sku": "SKU001", "name": "A"},
        {"sku": "SKU005", "name": "E"},
    ]
    for it in items:
        tree.insert(it)

    inorder = tree.inorder_traversal()
    inorder_skus = [it["sku"] for it in inorder]
    assert inorder_skus == ["SKU001", "SKU003", "SKU005"]

    preorder = tree.preorder_traversal()
    assert len(preorder) == 3
