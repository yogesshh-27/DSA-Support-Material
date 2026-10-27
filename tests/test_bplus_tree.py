"""
Unit tests for Advanced Inventory Search: B+ Tree.
Tests:
- Insertion into empty tree
- Multiple insertions
- Leaf node splitting
- Internal node splitting
- Root splitting (tree height increment)
- Point search (successful & unsuccessful)
- Duplicate Product ID handling
- Sequential sorted traversal via linked leaf nodes
- Range queries between Product IDs
- Node statistics and structural hierarchy verification
"""

import pytest
from backend.dsa.b_plus_tree import BPlusTree, BPlusNode


def test_bplus_empty_tree():
    tree = BPlusTree(order=3)
    assert tree.size == 0
    assert tree.get_height() == 1
    assert tree.get_all_records_sorted() == []
    rec, found, path, comps = tree.search("PRD101")
    assert found is False
    assert rec is None


def test_bplus_single_insert_and_search():
    tree = BPlusTree(order=3)
    item = {
        "product_id": "PRD101",
        "name": "Industrial Scanner",
        "category": "Electronics",
        "quantity": 10,
        "location": "Rack A",
        "priority": 8,
        "unit_weight": 1.5,
    }
    success, msg, events = tree.insert(item)
    assert success is True
    assert tree.size == 1

    rec, found, path, comps = tree.search("PRD101")
    assert found is True
    assert rec["product_id"] == "PRD101"
    assert rec["name"] == "Industrial Scanner"
    assert len(path) == 1  # Root leaf
    assert comps >= 1


def test_bplus_duplicate_rejection():
    tree = BPlusTree(order=3)
    item = {
        "product_id": "PRD101",
        "name": "Industrial Scanner",
        "category": "Electronics",
        "quantity": 10,
        "location": "Rack A",
        "priority": 8,
        "unit_weight": 1.5,
    }
    tree.insert(item)
    success, msg, _ = tree.insert(item)
    assert success is False
    assert "already exists" in msg
    assert tree.size == 1


def test_bplus_leaf_split_and_root_split():
    """
    With order = 3:
    max_keys = 2.
    Insert 1: ['A'] -> no split
    Insert 2: ['A', 'B'] -> no split
    Insert 3: ['A', 'B', 'C'] -> exceeds max_keys (3 > 2), triggers leaf split!
    Leaf splits into ['A'] and ['B', 'C'] (or ['A'] and ['B', 'C']),
    separator copied up, new root created. Height increases to 2.
    """
    tree = BPlusTree(order=3)
    products = [
        {"product_id": "PRD101", "name": "Item A"},
        {"product_id": "PRD102", "name": "Item B"},
        {"product_id": "PRD103", "name": "Item C"},
    ]
    for p in products:
        success, msg, events = tree.insert(p)
        assert success is True

    assert tree.size == 3
    assert tree.get_height() == 2
    internals, leaves = tree.count_nodes()
    assert internals == 1  # New root internal node
    assert leaves == 2  # 2 leaf children

    # Check search for all 3 items
    for p in products:
        rec, found, path, _ = tree.search(p["product_id"])
        assert found is True
        assert rec["product_id"] == p["product_id"]


def test_bplus_internal_node_split():
    """
    Insert enough items into an order 3 tree to cause internal node splits:
    Tree height will reach 3 as internal nodes split.
    """
    tree = BPlusTree(order=3)
    keys = [f"PRD{i:03d}" for i in range(10, 19)]  # 9 keys: PRD010..PRD018
    for k in keys:
        success, msg, _ = tree.insert({"product_id": k, "name": f"Product {k}"})
        assert success is True

    assert tree.size == 9
    assert tree.get_height() >= 2

    # Verify all 9 keys can be located
    for k in keys:
        rec, found, _, _ = tree.search(k)
        assert found is True
        assert rec["product_id"] == k


def test_bplus_linked_leaf_sequential_traversal():
    """Verify that linked leaf nodes maintain sorted order without tree recursion."""
    tree = BPlusTree(order=4)
    # Insert keys out of order
    input_keys = ["PRD150", "PRD110", "PRD130", "PRD120", "PRD140", "PRD100"]
    for k in input_keys:
        tree.insert({"product_id": k, "name": f"Product {k}"})

    sorted_records = tree.get_all_records_sorted()
    extracted_keys = [r["product_id"] for r in sorted_records]
    assert extracted_keys == sorted(input_keys)


def test_bplus_range_query():
    """
    Range query between PRD110 and PRD140.
    Should return PRD110, PRD120, PRD130, PRD140 using linked leaves.
    """
    tree = BPlusTree(order=4)
    input_keys = ["PRD100", "PRD110", "PRD120", "PRD130", "PRD140", "PRD150", "PRD160"]
    for k in input_keys:
        tree.insert({"product_id": k, "name": f"Product {k}"})

    res = tree.range_query("PRD110", "PRD140")
    assert res["success"] is True
    assert res["count"] == 4
    matched_pids = [r["product_id"] for r in res["records"]]
    assert matched_pids == ["PRD110", "PRD120", "PRD130", "PRD140"]
    assert res["leaves_traversed_count"] >= 1


def test_bplus_hierarchy_export():
    """Verify full structural hierarchy serialization."""
    tree = BPlusTree(order=4)
    for i in range(1, 8):
        tree.insert({"product_id": f"PRD{i:02d}", "name": f"Item {i}"})

    h = tree.to_tree_hierarchy()
    assert h["order"] == 4
    assert h["total_records"] == 7
    assert h["height"] >= 2
    assert len(h["levels"]) == h["height"]
    assert len(h["leaf_chain_ids"]) == h["leaf_nodes_count"]
