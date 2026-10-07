"""
Dijkstra's Single-Source Shortest Path Algorithm for Warehouse Navigation.

Academic Purpose:
Determines the minimum movement cost route between any two warehouse
locations (e.g., Receiving to Dispatch Bay) using a greedy strategy
and an internal Min-Heap Priority Queue.
Time Complexity: O((V + E) log V)
Space Complexity: O(V)
"""

from typing import List, Dict, Any, Tuple, Optional
from backend.dsa.graph import WarehouseGraph


class MinHeapPriorityQueue:
    """
    Min-Heap Priority Queue implemented from scratch for Dijkstra and Prim.
    Stores tuples: (key, item) where key is numeric priority/distance.
    """

    def __init__(self):
        self.heap: List[Tuple[float, Any]] = []

    def is_empty(self) -> bool:
        return len(self.heap) == 0

    def push(self, priority: float, item: Any) -> None:
        self.heap.append((priority, item))
        self._heapify_up(len(self.heap) - 1)

    def pop(self) -> Tuple[float, Any]:
        if self.is_empty():
            raise IndexError("pop from empty priority queue")
        min_item = self.heap[0]
        last = self.heap.pop()
        if not self.is_empty():
            self.heap[0] = last
            self._heapify_down(0)
        return min_item

    def _heapify_up(self, idx: int) -> None:
        while idx > 0:
            parent_idx = (idx - 1) // 2
            if self.heap[idx][0] < self.heap[parent_idx][0]:
                self.heap[idx], self.heap[parent_idx] = self.heap[parent_idx], self.heap[idx]
                idx = parent_idx
            else:
                break

    def _heapify_down(self, idx: int) -> None:
        min_idx = idx
        left = 2 * idx + 1
        right = 2 * idx + 2

        if left < len(self.heap) and self.heap[left][0] < self.heap[min_idx][0]:
            min_idx = left
        if right < len(self.heap) and self.heap[right][0] < self.heap[min_idx][0]:
            min_idx = right

        if min_idx != idx:
            self.heap[idx], self.heap[min_idx] = self.heap[min_idx], self.heap[idx]
            self._heapify_down(min_idx)


def dijkstra_shortest_path(
    graph: WarehouseGraph, source_id: int, dest_id: int
) -> Dict[str, Any]:
    """
    Execute Dijkstra's algorithm from source_id to dest_id.
    Returns comprehensive trace for viva explanation.
    """
    if source_id not in graph.id_to_name:
        raise ValueError(f"Unknown source location ID {source_id}.")
    if dest_id not in graph.id_to_name:
        raise ValueError(f"Unknown destination location ID {dest_id}.")

    num_vertices = len(graph.vertices)
    # Initialize distances and predecessors
    dist: Dict[int, float] = {v["id"]: float("inf") for v in graph.vertices}
    parent: Dict[int, Optional[int]] = {v["id"]: None for v in graph.vertices}
    visited = set()

    dist[source_id] = 0.0

    pq = MinHeapPriorityQueue()
    pq.push(0.0, source_id)

    step_log: List[Dict[str, Any]] = []
    visited_sequence: List[str] = []

    step_num = 1

    while not pq.is_empty():
        current_dist, u = pq.pop()

        if u in visited:
            continue

        visited.add(u)
        visited_sequence.append(graph.id_to_name[u])

        step_log.append({
            "step": step_num,
            "action": f"Extracted '{graph.id_to_name[u]}' with tentative distance {current_dist}",
            "node_id": u,
            "node_name": graph.id_to_name[u],
            "distance": current_dist,
        })
        step_num += 1

        if u == dest_id:
            # Reached target
            break

        # Relax adjacent edges
        for neighbor, weight in graph.adj_list.get(u, []):
            if neighbor not in visited:
                new_dist = current_dist + weight
                if new_dist < dist[neighbor]:
                    old_dist = dist[neighbor]
                    dist[neighbor] = new_dist
                    parent[neighbor] = u
                    pq.push(new_dist, neighbor)

                    step_log.append({
                        "step": step_num,
                        "action": f"Relaxed edge ({graph.id_to_name[u]} -> {graph.id_to_name[neighbor]}): updated distance from {('∞' if old_dist == float('inf') else old_dist)} to {new_dist}",
                        "from_node": graph.id_to_name[u],
                        "to_node": graph.id_to_name[neighbor],
                        "new_distance": new_dist,
                    })
                    step_num += 1

    # Check if reachable
    if dist[dest_id] == float("inf"):
        return {
            "source": graph.id_to_name[source_id],
            "destination": graph.id_to_name[dest_id],
            "reachable": False,
            "total_cost": None,
            "route_ids": [],
            "route_names": [],
            "path_description": "No path exists between the selected locations.",
            "steps": step_log,
            "visited_sequence": visited_sequence,
            "complexity": "O((V + E) log V)",
        }

    # Reconstruct path
    path: List[int] = []
    curr = dest_id
    while curr is not None:
        path.append(curr)
        curr = parent[curr]
    path.reverse()

    route_names = [graph.id_to_name[n] for n in path]
    path_description = " → ".join(route_names)

    return {
        "source": graph.id_to_name[source_id],
        "destination": graph.id_to_name[dest_id],
        "reachable": True,
        "total_cost": dist[dest_id],
        "route_ids": path,
        "route_names": route_names,
        "path_description": path_description,
        "steps": step_log,
        "visited_sequence": visited_sequence,
        "complexity": "O((V + E) log V)",
    }
