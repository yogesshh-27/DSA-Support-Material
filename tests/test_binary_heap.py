"""
Unit tests for Binary Max Heap Priority Queue.
Tests: Insert, Peek, Extract Max, Heap ordering property, and Empty Heap handling.
"""

import pytest
from backend.dsa.binary_heap import MaxHeap


def test_heap_insert_and_peek():
    heap = MaxHeap()
    assert heap.peek() is None

    heap.insert({"sku": "SKU001", "alert_type": "Normal", "priority": 5, "quantity": 10, "location": "Rack A"})
    assert heap.peek()["priority"] == 5

    heap.insert({"sku": "SKU002", "alert_type": "Critical Stock", "priority": 10, "quantity": 1, "location": "Rack B"})
    assert heap.peek()["priority"] == 10
    assert heap.peek()["sku"] == "SKU002"


def test_heap_extract_max_order():
    heap = MaxHeap()
    alerts = [
        {"sku": "SKU_P3", "priority": 3, "alert_type": "Info", "quantity": 50, "location": "Rack A"},
        {"sku": "SKU_P9", "priority": 9, "alert_type": "Critical", "quantity": 2, "location": "Rack B"},
        {"sku": "SKU_P7", "priority": 7, "alert_type": "Warning", "quantity": 5, "location": "Rack C"},
        {"sku": "SKU_P10", "priority": 10, "alert_type": "Emergency", "quantity": 0, "location": "Rack D"},
        {"sku": "SKU_P1", "priority": 1, "alert_type": "Low", "quantity": 100, "location": "Rack A"},
    ]
    for a in alerts:
        heap.insert(a)

    assert heap.size() == 5

    extracted_priorities = []
    while not heap.is_empty():
        top = heap.extract_max()
        extracted_priorities.append(top["priority"])

    assert extracted_priorities == [10, 9, 7, 3, 1]
    assert heap.is_empty()
    assert heap.extract_max() is None


def test_heap_empty_edge_cases():
    heap = MaxHeap()
    assert heap.is_empty() is True
    assert heap.size() == 0
    assert heap.peek() is None
    assert heap.extract_max() is None
