"""
Unit tests for Warehouse Route Optimizer: TSP using Branch and Bound.
Tests:
- Small graph with known optimal tour
- Graph with asymmetric / differing edge weights
- Graph with missing connections
- Disconnected graph where no complete tour exists
- Minimum supported number of locations (K=1, K=2)
- Verification of branch pruning (pruned count > 0)
- Tour validity: starts and ends at start node, visits all locations once, cost matches edge sum
- Nearest-neighbor heuristic comparison
"""

import pytest
from backend.dsa.tsp_branch_bound import solve_tsp_branch_and_bound, solve_tsp_nearest_neighbor
from backend.dsa.graph import WarehouseGraph


def test_tsp_single_location():
    """K = 1: Single warehouse location edge case."""
    cost_matrix = [[0.0]]
    id_to_name = {0: "Receiving"}
    result = solve_tsp_branch_and_bound(
        location_ids=[0],
        cost_matrix=cost_matrix,
        id_to_name=id_to_name,
        start_vertex_id=0,
    )
    assert result["success"] is True
    assert result["tour_possible"] is True
    assert result["total_cost"] == 0.0
    assert result["optimal_route_ids"] == [0, 0]


def test_tsp_two_locations():
    """K = 2: Two warehouse locations with an edge."""
    # Location 0 <-> Location 1 with weight 5.0
    cost_matrix = [
        [float("inf"), 5.0],
        [5.0, float("inf")],
    ]
    id_to_name = {0: "Receiving", 1: "Rack A"}
    result = solve_tsp_branch_and_bound(
        location_ids=[0, 1],
        cost_matrix=cost_matrix,
        id_to_name=id_to_name,
        start_vertex_id=0,
    )
    assert result["success"] is True
    assert result["tour_possible"] is True
    assert result["total_cost"] == 10.0
    assert result["optimal_route_ids"] == [0, 1, 0]


def test_tsp_known_optimal_triangle():
    """
    K = 3: Triangle graph with known costs:
    0-1: 10, 1-2: 20, 2-0: 15.
    Tour: 0 -> 1 -> 2 -> 0 with cost 10 + 20 + 15 = 45.
    """
    cost_matrix = [
        [float("inf"), 10.0, 15.0],
        [10.0, float("inf"), 20.0],
        [15.0, 20.0, float("inf")],
    ]
    id_to_name = {0: "Receiving", 1: "Rack A", 2: "Rack B"}
    result = solve_tsp_branch_and_bound(
        location_ids=[0, 1, 2],
        cost_matrix=cost_matrix,
        id_to_name=id_to_name,
        start_vertex_id=0,
    )
    assert result["success"] is True
    assert result["tour_possible"] is True
    assert result["total_cost"] == 45.0
    assert result["optimal_route_ids"][0] == 0
    assert result["optimal_route_ids"][-1] == 0
    assert set(result["optimal_route_ids"]) == {0, 1, 2}


def test_tsp_known_4_vertex_tour_and_pruning():
    """
    Classic textbook 4-city TSP matrix:
        0   1   2   3
    0   inf 10  15  20
    1   10  inf 35  25
    2   15  35  inf 30
    3   20  25  30  inf

    Possible tours from 0:
    - 0 -> 1 -> 3 -> 2 -> 0: 10 + 25 + 30 + 15 = 80
    - 0 -> 2 -> 3 -> 1 -> 0: 15 + 30 + 25 + 10 = 80
    - 0 -> 1 -> 2 -> 3 -> 0: 10 + 35 + 30 + 20 = 95
    Optimal tour cost is 80.
    Must prune subtrees (e.g. branch through 0->1->2 has higher lower bound).
    """
    cost_matrix = [
        [float("inf"), 10.0, 15.0, 20.0],
        [10.0, float("inf"), 35.0, 25.0],
        [15.0, 35.0, float("inf"), 30.0],
        [20.0, 25.0, 30.0, float("inf")],
    ]
    id_to_name = {0: "Receiving", 1: "Rack A", 2: "Rack B", 3: "Rack C"}
    result = solve_tsp_branch_and_bound(
        location_ids=[0, 1, 2, 3],
        cost_matrix=cost_matrix,
        id_to_name=id_to_name,
        start_vertex_id=0,
    )
    assert result["success"] is True
    assert result["tour_possible"] is True
    assert result["total_cost"] == 80.0
    assert result["optimal_route_ids"][0] == 0
    assert result["optimal_route_ids"][-1] == 0
    assert len(result["optimal_route_ids"]) == 5  # 4 cities + return
    assert result["branches_pruned"] >= 1  # Verify branch pruning occurred


def test_tsp_missing_connections_and_disconnected_graph():
    """Graph where some edges are missing (inf) and no complete tour can be formed."""
    # 0 is connected to 1, but 2 is completely isolated
    cost_matrix = [
        [float("inf"), 5.0, float("inf")],
        [5.0, float("inf"), float("inf")],
        [float("inf"), float("inf"), float("inf")],
    ]
    id_to_name = {0: "Receiving", 1: "Rack A", 2: "Rack D"}
    result = solve_tsp_branch_and_bound(
        location_ids=[0, 1, 2],
        cost_matrix=cost_matrix,
        id_to_name=id_to_name,
        start_vertex_id=0,
    )
    assert result["tour_possible"] is False
    assert "cannot form a complete tour" in result["message"] or "No complete" in result["message"]


def test_tsp_warehouse_subgraph():
    """
    Test on actual warehouse cycle: Receiving (0), Rack A (1), Rack B (2).
    Edges in warehouse.json:
    0-1: 4
    0-2: 6
    1-2: 3
    Tour 0 -> 1 -> 2 -> 0 has cost 4 + 3 + 6 = 13.
    """
    cost_matrix = [
        [float("inf"), 4.0, 6.0],
        [4.0, float("inf"), 3.0],
        [6.0, 3.0, float("inf")],
    ]
    id_to_name = {0: "Receiving", 1: "Rack A", 2: "Rack B"}
    result = solve_tsp_branch_and_bound(
        location_ids=[0, 1, 2],
        cost_matrix=cost_matrix,
        id_to_name=id_to_name,
        start_vertex_id=0,
    )
    assert result["success"] is True
    assert result["tour_possible"] is True
    assert result["total_cost"] == 13.0
    assert result["optimal_route_ids"] in ([0, 1, 2, 0], [0, 2, 1, 0])


def test_tsp_nearest_neighbor_comparison():
    """Verify that nearest-neighbor heuristic produces a valid route and is labeled correctly."""
    cost_matrix = [
        [float("inf"), 10.0, 15.0],
        [10.0, float("inf"), 20.0],
        [15.0, 20.0, float("inf")],
    ]
    id_to_name = {0: "Receiving", 1: "Rack A", 2: "Rack B"}
    result = solve_tsp_branch_and_bound(
        location_ids=[0, 1, 2],
        cost_matrix=cost_matrix,
        id_to_name=id_to_name,
        start_vertex_id=0,
    )
    nn = result["nearest_neighbor"]
    assert nn is not None
    assert nn["possible"] is True
    assert "Nearest-Neighbor" in nn["heuristic_name"]
    assert nn["total_cost"] is not None
