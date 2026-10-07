"""
Prim's Minimum Spanning Tree (MST) Algorithm for Warehouse Network Optimization.

Academic Purpose:
Constructs a backbone sub-network (e.g. pneumatic tubes, AGV main track,
fiber-optic monitoring grid) that connects ALL warehouse zones with
minimum total installation/travel cost without forming cycles.

Key Difference from Dijkstra:
- Prim's MST minimizes the TOTAL weight of edges connecting all V vertices (V-1 edges).
- Dijkstra minimizes the distance from a SINGLE source vertex to destination vertices.
"""

from typing import List, Dict, Any, Tuple, Set
from backend.dsa.graph import WarehouseGraph
from backend.dsa.dijkstra import MinHeapPriorityQueue


def prim_mst(graph: WarehouseGraph, start_node_id: int = 0) -> Dict[str, Any]:
    """
    Computes the Minimum Spanning Tree starting from start_node_id.
    Time Complexity: O((V + E) log V)
    Space Complexity: O(V + E)
    """
    if not graph.vertices:
        return {
            "total_cost": 0,
            "mst_edges": [],
            "edge_count": 0,
            "is_connected": True,
            "steps": [],
            "complexity": "O((V + E) log V)",
        }

    if start_node_id not in graph.id_to_name:
        start_node_id = graph.vertices[0]["id"]

    visited: Set[int] = set()
    mst_edges: List[Dict[str, Any]] = []
    total_cost: float = 0.0
    steps_log: List[Dict[str, Any]] = []

    # Priority queue stores tuples: (weight, (u, v))
    pq = MinHeapPriorityQueue()

    # Add start node to visited
    visited.add(start_node_id)
    steps_log.append({
        "step": 1,
        "action": f"Started MST construction from root vertex '{graph.id_to_name[start_node_id]}'",
        "vertex": graph.id_to_name[start_node_id],
    })

    # Push all incident edges from start node
    for neighbor, weight in graph.adj_list.get(start_node_id, []):
        pq.push(weight, (start_node_id, neighbor))

    step_counter = 2
    # MST must contain V - 1 edges
    target_edges = len(graph.vertices) - 1

    while not pq.is_empty() and len(mst_edges) < target_edges:
        weight, (u, v) = pq.pop()

        # If already in visited set, ignore (avoids cycle)
        if v in visited:
            continue

        visited.add(v)
        total_cost += weight
        mst_edges.append({
            "u": u,
            "v": v,
            "u_name": graph.id_to_name[u],
            "v_name": graph.id_to_name[v],
            "weight": weight,
        })

        steps_log.append({
            "step": step_counter,
            "action": f"Selected minimum cut edge: {graph.id_to_name[u]} ───({weight})─── {graph.id_to_name[v]}",
            "added_vertex": graph.id_to_name[v],
            "edge_weight": weight,
            "running_total": total_cost,
        })
        step_counter += 1

        # Add edges from new vertex v
        for next_neighbor, edge_weight in graph.adj_list.get(v, []):
            if next_neighbor not in visited:
                pq.push(edge_weight, (v, next_neighbor))

    is_connected = len(visited) == len(graph.vertices)

    return {
        "start_node": graph.id_to_name[start_node_id],
        "is_connected": is_connected,
        "total_cost": total_cost,
        "edge_count": len(mst_edges),
        "expected_edges": target_edges,
        "mst_edges": mst_edges,
        "steps": steps_log,
        "complexity": "O((V + E) log V)",
    }
