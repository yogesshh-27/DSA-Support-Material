"""
Unit tests for 0/1 Knapsack Dynamic Programming algorithm.
Tests: Known optimal value, selected items backtracking, DP table construction,
and edge cases (capacity 0, empty items, invalid weights).
"""

import pytest
from backend.dsa.knapsack import solve_01_knapsack


def test_knapsack_sample_data():
    items = [
        {"name": "Medical Kit", "weight": 4, "value": 10},
        {"name": "Packaged Food", "weight": 3, "value": 7},
        {"name": "Electronics", "weight": 5, "value": 12},
        {"name": "Stationery", "weight": 2, "value": 4},
        {"name": "Tools", "weight": 6, "value": 13},
    ]
    capacity = 10

    result = solve_01_knapsack(items, capacity)
    assert result["max_value"] == 23
    assert result["total_weight"] <= capacity
    assert len(result["selected_items"]) > 0

    # Verify DP table size is (n + 1) x (W + 1) = 6 x 11
    dp_table = result["dp_table"]
    assert len(dp_table) == 6
    assert len(dp_table[0]) == 11
    assert dp_table[5][10] == 23


def test_knapsack_capacity_zero():
    items = [{"name": "A", "weight": 2, "value": 10}]
    result = solve_01_knapsack(items, 0)
    assert result["max_value"] == 0
    assert result["total_weight"] == 0
    assert result["selected_items"] == []


def test_knapsack_empty_items():
    result = solve_01_knapsack([], 10)
    assert result["max_value"] == 0
    assert result["total_weight"] == 0
    assert result["selected_items"] == []


def test_knapsack_invalid_inputs():
    # Negative capacity
    with pytest.raises(ValueError, match="Capacity cannot be negative"):
        solve_01_knapsack([{"name": "A", "weight": 1, "value": 1}], -5)

    # Zero or negative weight item
    with pytest.raises(ValueError, match="weight must be a positive integer"):
        solve_01_knapsack([{"name": "Bad", "weight": 0, "value": 5}], 10)
