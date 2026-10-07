"""
Floyd-Warshall All-Pairs Shortest Path Algorithm for Warehouse Operations.

Academic Purpose:
A Dynamic Programming approach that calculates the shortest distances between
EVERY pair of warehouse locations in O(V^3) time using the Adjacency Matrix.
Enables rapid O(1) distance lookups for batch dispatch routing.

Recurrence Relation:
dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]) for intermediate nodes k in [0..V-1].
"""

import copy
from typing import List, Dict, Any, Optional
from backend.dsa.graph import WarehouseGraph


def floyd_warshall_all_pairs(graph: WarehouseGraph) -> Dict[str, Any]:
    """
    Computes all-pairs shortest paths using the graph's adjacency matrix.
    Time Complexity: O(V^3)
    Space Complexity: O(V^2)
    """
    n = len(graph.vertices)
    headers = [v["name"] for v in graph.vertices]

    # Initialize distance matrix D and predecessor matrix Next
    # D^(0) is copied from the graph's Adjacency Matrix
    dist: List[List[float]] = copy.deepcopy(graph.adj_matrix)
    next_node: List[List[Optional[int]]] = [[None] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i != j and dist[i][j] != float("inf"):
                next_node[i][j] = j
            elif i == j:
                next_node[i][j] = i

    initial_display = _format_matrix(dist)

    # DP iterations: consider each vertex k as an intermediate node
    intermediate_steps = []
    for k in range(n):
        k_name = headers[k]
        updates_count = 0
        for i in range(n):
            for j in range(n):
                if dist[i][k] != float("inf") and dist[k][j] != float("inf"):
                    possible_shorter = dist[i][k] + dist[k][j]
                    if possible_shorter < dist[i][j]:
                        dist[i][j] = possible_shorter
                        next_node[i][j] = next_node[i][k]
                        updates_count += 1

        intermediate_steps.append({
            "k": k,
            "intermediate_node": k_name,
            "updates_made": updates_count,
        })

    final_display = _format_matrix(dist)

    return {
        "num_vertices": n,
        "headers": headers,
        "initial_matrix": initial_display,
        "final_matrix": final_display,
        "raw_distances": dist,
        "next_node": next_node,
        "intermediate_steps": intermediate_steps,
        "complexity": "Time: O(V³), Space: O(V²)",
    }


def query_floyd_warshall_pair(
    graph: WarehouseGraph, fw_result: Dict[str, Any], u: int, v: int
) -> Dict[str, Any]:
    """Lookup shortest distance and path between u and v from computed matrix."""
    n = len(graph.vertices)
    if u < 0 or u >= n or v < 0 or v >= n:
        raise ValueError(f"Invalid node indices ({u}, {v}). Must be 0 to {n-1}.")

    dist_val = fw_result["raw_distances"][u][v]
    u_name = graph.id_to_name[u]
    v_name = graph.id_to_name[v]

    if dist_val == float("inf"):
        return {
            "source": u_name,
            "destination": v_name,
            "distance": "∞",
            "reachable": False,
            "path": [],
            "path_description": "No reachable path.",
        }

    # Reconstruct path using next_node matrix
    next_node = fw_result["next_node"]
    curr = u
    path = [curr]
    while curr != v:
        nxt = next_node[curr][v]
        if nxt is None:
            break
        curr = nxt
        path.append(curr)

    route_names = [graph.id_to_name[idx] for idx in path]
    return {
        "source": u_name,
        "destination": v_name,
        "distance": int(dist_val) if dist_val.is_integer() else round(dist_val, 2),
        "reachable": True,
        "path_ids": path,
        "path_names": route_names,
        "path_description": " → ".join(route_names),
    }


def _format_matrix(matrix: List[List[float]]) -> List[List[Any]]:
    formatted = []
    for row in matrix:
        formatted_row = []
        for val in row:
            if val == float("inf"):
                formatted_row.append("∞")
            else:
                formatted_row.append(int(val) if val.is_integer() else round(val, 2))
        formatted.append(formatted_row)
    return formatted
