"""
Unit tests for Graph Representations, Dijkstra, Prim MST, and Floyd-Warshall algorithms.
Tests: Representations, known shortest paths, known MST, all-pairs shortest distances,
and edge cases (disconnected graph, invalid node, negative weights).
"""

import pytest
from backend.dsa.graph import WarehouseGraph
from backend.dsa.dijkstra import dijkstra_shortest_path
from backend.dsa.prim import prim_mst
from backend.dsa.floyd_warshall import floyd_warshall_all_pairs, query_floyd_warshall_pair


@pytest.fixture
def sample_graph():
    """Build standard warehouse graph from requirements."""
    g = WarehouseGraph()
    nodes = [
        (0, "Receiving"),
        (1, "Rack A"),
        (2, "Rack B"),
        (3, "Rack C"),
        (4, "Rack D"),
        (5, "Packing Zone"),
        (6, "Dispatch Bay"),
    ]
    for nid, name in nodes:
        g.add_vertex(nid, name)

    edges = [
        (0, 1, 4),
        (0, 2, 6),
        (1, 2, 3),
        (1, 3, 7),
        (2, 3, 4),
        (2, 4, 8),
        (3, 4, 2),
        (3, 5, 5),
        (4, 5, 6),
        (4, 6, 9),
        (5, 6, 3),
    ]
    for u, v, w in edges:
        g.add_edge(u, v, w)
    return g


def test_graph_representations(sample_graph):
    adj_list = sample_graph.get_adjacency_list()
    assert adj_list["num_vertices"] == 7
    assert adj_list["num_edges"] == 11
    assert "Receiving" in adj_list["data"]

    adj_matrix = sample_graph.get_adjacency_matrix()
    assert adj_matrix["num_vertices"] == 7
    assert len(adj_matrix["raw_matrix"]) == 7
    # Diagonal should be 0
    for i in range(7):
        assert adj_matrix["raw_matrix"][i][i] == 0.0
    # Edge between Receiving (0) and Rack A (1) is 4
    assert adj_matrix["raw_matrix"][0][1] == 4.0
    assert adj_matrix["raw_matrix"][1][0] == 4.0


def test_negative_weight_rejection(sample_graph):
    with pytest.raises(ValueError, match="Negative weight"):
        sample_graph.add_edge(0, 5, -3)


def test_dijkstra_known_shortest_path(sample_graph):
    # Shortest path from Receiving (0) to Dispatch Bay (6)
    result = dijkstra_shortest_path(sample_graph, 0, 6)
    assert result["reachable"] is True
    assert result["total_cost"] == 18.0
    assert result["route_ids"] == [0, 2, 3, 5, 6]
    assert result["route_names"] == ["Receiving", "Rack B", "Rack C", "Packing Zone", "Dispatch Bay"]
    assert len(result["steps"]) > 0


def test_dijkstra_same_source_and_destination(sample_graph):
    result = dijkstra_shortest_path(sample_graph, 2, 2)
    assert result["reachable"] is True
    assert result["total_cost"] == 0.0
    assert result["route_ids"] == [2]


def test_dijkstra_invalid_nodes(sample_graph):
    with pytest.raises(ValueError, match="Unknown source"):
        dijkstra_shortest_path(sample_graph, 999, 1)
    with pytest.raises(ValueError, match="Unknown destination"):
        dijkstra_shortest_path(sample_graph, 0, 999)


def test_prim_known_mst(sample_graph):
    mst = prim_mst(sample_graph, start_node_id=0)
    assert mst["is_connected"] is True
    assert mst["edge_count"] == 6  # V - 1 = 7 - 1 = 6 edges
    # Check edges selected:
    # 1. (0,1): 4
    # 2. (1,2): 3
    # 3. (2,3): 4
    # 4. (3,4): 2
    # 5. (3,5): 5
    # 6. (5,6): 3
    # Total = 4 + 3 + 4 + 2 + 5 + 3 = 21
    assert mst["total_cost"] == 21.0


def test_floyd_warshall_all_pairs(sample_graph):
    fw = floyd_warshall_all_pairs(sample_graph)
    # Check distance from 0 to 6 in matrix equals 18.0
    assert fw["raw_distances"][0][6] == 18.0
    assert fw["raw_distances"][6][0] == 18.0
    # Check diagonal is 0
    for i in range(7):
        assert fw["raw_distances"][i][i] == 0.0

    # Query specific pair
    query_res = query_floyd_warshall_pair(sample_graph, fw, 0, 6)
    assert query_res["distance"] == 18
    assert query_res["reachable"] is True
    assert query_res["path_ids"] == [0, 2, 3, 5, 6]


def test_disconnected_graph_edge_case():
    g = WarehouseGraph()
    g.add_vertex(0, "Zone A")
    g.add_vertex(1, "Zone B")
    g.add_vertex(2, "Isolated Zone")
    g.add_edge(0, 1, 10)

    # Dijkstra to isolated zone
    res = dijkstra_shortest_path(g, 0, 2)
    assert res["reachable"] is False
    assert res["total_cost"] is None

    # Prim on disconnected graph
    mst = prim_mst(g, 0)
    assert mst["is_connected"] is False
    assert mst["edge_count"] == 1  # only edge (0,1) can be reached

    # Floyd-Warshall on disconnected graph
    fw = floyd_warshall_all_pairs(g)
    assert fw["raw_distances"][0][2] == float("inf")
