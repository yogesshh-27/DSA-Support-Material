"""
Warehouse Route Optimizer: Travelling Salesman Problem (TSP) using Branch and Bound.

Academic Purpose (Unit 4 - Backtracking and Branch & Bound):
Solves the NP-hard Travelling Salesman Problem to find a minimum-cost tour visiting
a selected subset of warehouse locations exactly once and returning to the starting point.

Branch and Bound Mechanics:
1. State Space Tree: Each node represents a partial tour starting at the root location.
2. Bounding Function: Matrix reduction (row and column reduction) computes a rigorous
   mathematical lower bound for every partial path.
3. Pruning Criteria: Any branch whose lower bound >= current best complete tour cost
   is pruned immediately, avoiding exhaustive exploration of suboptimal subtrees.
4. Execution Trace: Emits step-by-step exploration events for interactive step-by-step
   visualization and academic viva demonstration.
5. Heuristic Comparison: Compares Branch & Bound optimal results against a simple
   Nearest-Neighbor greedy heuristic to show why greedy solutions are often suboptimal.
"""

from typing import List, Dict, Any, Optional, Tuple
import copy
import heapq


class TSPNode:
    """Represents a search node in the Branch and Bound State Space Tree."""

    def __init__(
        self,
        node_id: int,
        parent_id: Optional[int],
        vertex: int,
        level: int,
        path: List[int],
        reduced_matrix: List[List[float]],
        cost: float,
        bound: float,
    ):
        self.node_id = node_id
        self.parent_id = parent_id
        self.vertex = vertex
        self.level = level
        self.path = list(path)
        self.reduced_matrix = reduced_matrix
        self.cost = cost
        self.bound = bound

    def __lt__(self, other: "TSPNode") -> bool:
        # Priority queue orders by lower bound (best-first search)
        if abs(self.bound - other.bound) < 1e-9:
            return self.level > other.level  # Prefer deeper nodes on ties
        return self.bound < other.bound


def reduce_matrix(matrix: List[List[float]], n: int) -> Tuple[List[List[float]], float]:
    """
    Performs row and column reduction on the cost matrix.
    Returns the reduced matrix and the reduction cost (sum of minimums).
    """
    reduced = [row[:] for row in matrix]
    reduction_cost = 0.0

    # 1. Row Reduction
    for i in range(n):
        row_min = float("inf")
        for j in range(n):
            if reduced[i][j] < row_min:
                row_min = reduced[i][j]

        if row_min != float("inf") and row_min > 0:
            reduction_cost += row_min
            for j in range(n):
                if reduced[i][j] != float("inf"):
                    reduced[i][j] -= row_min

    # 2. Column Reduction
    for j in range(n):
        col_min = float("inf")
        for i in range(n):
            if reduced[i][j] < col_min:
                col_min = reduced[i][j]

        if col_min != float("inf") and col_min > 0:
            reduction_cost += col_min
            for i in range(n):
                if reduced[i][j] != float("inf"):
                    reduced[i][j] -= col_min

    return reduced, reduction_cost


def solve_tsp_branch_and_bound(
    location_ids: List[int],
    cost_matrix: List[List[float]],
    id_to_name: Dict[int, str],
    start_vertex_id: int,
) -> Dict[str, Any]:
    """
    Executes Branch and Bound for TSP on the given set of warehouse locations.

    Parameters:
    - location_ids: List of warehouse location IDs to visit.
    - cost_matrix: |V| x |V| distance matrix for all vertices in location_ids.
    - id_to_name: Mapping from location ID to location name.
    - start_vertex_id: Starting location ID (must be in location_ids).

    Returns:
    - Comprehensive result dictionary with optimal route, total cost,
      exploration statistics, pruning statistics, step-by-step trace, and
      nearest-neighbor comparison.
    """
    if start_vertex_id not in location_ids:
        raise ValueError(f"Start location {start_vertex_id} is not in selected locations {location_ids}.")

    k = len(location_ids)
    if k == 0:
        return {
            "success": False,
            "tour_possible": False,
            "message": "No warehouse locations selected for TSP tour.",
        }

    # Handle single location edge case
    if k == 1:
        loc = location_ids[0]
        name = id_to_name.get(loc, f"Node-{loc}")
        return {
            "success": True,
            "tour_possible": True,
            "algorithm": "Branch and Bound for TSP",
            "start_location": {"id": loc, "name": name},
            "selected_locations": [{"id": loc, "name": name}],
            "optimal_route_ids": [loc, loc],
            "optimal_route_names": [name, name],
            "total_cost": 0.0,
            "nodes_explored": 1,
            "branches_pruned": 0,
            "execution_steps": [
                {
                    "step_index": 1,
                    "node_id": 1,
                    "parent_id": None,
                    "action": "SOLUTION",
                    "partial_route": [loc, loc],
                    "partial_names": [name, name],
                    "current_vertex": loc,
                    "current_name": name,
                    "accumulated_cost": 0.0,
                    "lower_bound": 0.0,
                    "best_cost_so_far": 0.0,
                    "reason": "Single location selected; trivial zero-cost tour.",
                }
            ],
            "nearest_neighbor": {
                "route_ids": [loc, loc],
                "route_names": [name, name],
                "total_cost": 0.0,
            },
            "complexity": {
                "time_worst_case": "O(2^n * n^2) or O(n!) in worst case",
                "space": "O(n^2 * 2^n)",
                "pruning_efficiency": "Subtrees with LB >= Best Cost are eliminated",
            },
        }

    # Map global vertex IDs to local 0..k-1 indices
    local_to_global = list(location_ids)
    # Ensure start vertex is at index 0 for canonical root
    start_idx = local_to_global.index(start_vertex_id)
    local_to_global[0], local_to_global[start_idx] = local_to_global[start_idx], local_to_global[0]
    global_to_local = {gid: idx for idx, gid in enumerate(local_to_global)}

    # Construct local k x k matrix
    local_matrix = [[float("inf")] * k for _ in range(k)]
    for i in range(k):
        for j in range(k):
            u = local_to_global[i]
            v = local_to_global[j]
            if i == j:
                local_matrix[i][j] = float("inf")
            else:
                local_matrix[i][j] = cost_matrix[i][j]

    # Pre-check: Check if start node has any outgoing/incoming valid edges
    outgoing_from_start = [local_matrix[0][j] for j in range(k) if local_matrix[0][j] < float("inf")]
    if not outgoing_from_start:
        return {
            "success": True,
            "tour_possible": False,
            "message": f"Starting location '{id_to_name.get(start_vertex_id)}' has no outgoing paths to other selected zones.",
            "start_location": {"id": start_vertex_id, "name": id_to_name.get(start_vertex_id)},
            "selected_locations": [{"id": gid, "name": id_to_name.get(gid)} for gid in location_ids],
            "optimal_route_ids": [],
            "optimal_route_names": [],
            "total_cost": None,
            "nodes_explored": 1,
            "branches_pruned": 0,
            "execution_steps": [],
            "nearest_neighbor": None,
        }

    # 1. Initialize Root Node via Matrix Reduction
    initial_reduced_matrix, initial_bound = reduce_matrix(local_matrix, k)
    if initial_bound == float("inf"):
        # Graph is disconnected among selected locations
        return {
            "success": True,
            "tour_possible": False,
            "message": "Selected warehouse locations cannot form a complete tour due to missing connections.",
            "start_location": {"id": start_vertex_id, "name": id_to_name.get(start_vertex_id)},
            "selected_locations": [{"id": gid, "name": id_to_name.get(gid)} for gid in location_ids],
            "optimal_route_ids": [],
            "optimal_route_names": [],
            "total_cost": None,
            "nodes_explored": 1,
            "branches_pruned": 0,
            "execution_steps": [],
            "nearest_neighbor": None,
        }

    # Best tour tracking
    best_cost = float("inf")
    best_tour_local: List[int] = []

    # Priority queue for Best-First Branch and Bound
    pq: List[TSPNode] = []
    node_counter = 1

    root_node = TSPNode(
        node_id=node_counter,
        parent_id=None,
        vertex=0,
        level=1,
        path=[0],
        reduced_matrix=initial_reduced_matrix,
        cost=0.0,
        bound=initial_bound,
    )
    heapq.heappush(pq, root_node)

    # Trace steps for visualization
    execution_steps: List[Dict[str, Any]] = []
    nodes_explored = 0
    branches_pruned = 0

    root_path_names = [id_to_name[local_to_global[0]]]
    execution_steps.append({
        "step_index": len(execution_steps) + 1,
        "node_id": root_node.node_id,
        "parent_id": None,
        "action": "START",
        "partial_route": [local_to_global[0]],
        "partial_names": root_path_names,
        "current_vertex": local_to_global[0],
        "current_name": id_to_name[local_to_global[0]],
        "accumulated_cost": 0.0,
        "lower_bound": round(initial_bound, 2),
        "best_cost_so_far": "None",
        "reason": f"Initialized root state at {id_to_name[local_to_global[0]]} with Matrix Reduction Lower Bound = {round(initial_bound, 2)}.",
    })

    # Limit search space exploration steps to prevent unbounded memory on pathological graphs
    MAX_EXPLORED_NODES = 5000

    while pq and nodes_explored < MAX_EXPLORED_NODES:
        curr = heapq.heappop(pq)
        nodes_explored += 1

        curr_global_v = local_to_global[curr.vertex]
        curr_name = id_to_name[curr_global_v]
        curr_route_global = [local_to_global[i] for i in curr.path]
        curr_route_names = [id_to_name[gid] for gid in curr_route_global]

        # Prune if bound is already worse than or equal to current best
        if curr.bound >= best_cost:
            branches_pruned += 1
            execution_steps.append({
                "step_index": len(execution_steps) + 1,
                "node_id": curr.node_id,
                "parent_id": curr.parent_id,
                "action": "PRUNE",
                "partial_route": curr_route_global,
                "partial_names": curr_route_names,
                "current_vertex": curr_global_v,
                "current_name": curr_name,
                "accumulated_cost": round(curr.cost, 2),
                "lower_bound": round(curr.bound, 2),
                "best_cost_so_far": round(best_cost, 2) if best_cost < float("inf") else "None",
                "reason": f"Pruned branch at {curr_name}: Lower bound ({round(curr.bound, 2)}) >= Best tour cost ({round(best_cost, 2)}).",
            })
            continue

        # Check if we have visited all k locations
        if curr.level == k:
            # Need to close the tour back to root (index 0)
            return_cost = local_matrix[curr.vertex][0]
            if return_cost < float("inf"):
                total_tour_cost = curr.cost + return_cost
                if total_tour_cost < best_cost:
                    best_cost = total_tour_cost
                    best_tour_local = curr.path + [0]
                    complete_route_global = [local_to_global[i] for i in best_tour_local]
                    complete_route_names = [id_to_name[gid] for gid in complete_route_global]

                    execution_steps.append({
                        "step_index": len(execution_steps) + 1,
                        "node_id": curr.node_id,
                        "parent_id": curr.parent_id,
                        "action": "SOLUTION",
                        "partial_route": complete_route_global,
                        "partial_names": complete_route_names,
                        "current_vertex": curr_global_v,
                        "current_name": curr_name,
                        "accumulated_cost": round(total_tour_cost, 2),
                        "lower_bound": round(curr.bound, 2),
                        "best_cost_so_far": round(best_cost, 2),
                        "reason": f"Found new optimal complete tour with total cost {round(best_cost, 2)} returning to {id_to_name[local_to_global[0]]}.",
                    })
            else:
                branches_pruned += 1
                execution_steps.append({
                    "step_index": len(execution_steps) + 1,
                    "node_id": curr.node_id,
                    "parent_id": curr.parent_id,
                    "action": "PRUNE",
                    "partial_route": curr_route_global,
                    "partial_names": curr_route_names,
                    "current_vertex": curr_global_v,
                    "current_name": curr_name,
                    "accumulated_cost": round(curr.cost, 2),
                    "lower_bound": round(curr.bound, 2),
                    "best_cost_so_far": round(best_cost, 2) if best_cost < float("inf") else "None",
                    "reason": f"Cannot complete tour from {curr_name}: no return corridor to {id_to_name[local_to_global[0]]}.",
                })
            continue

        # Branch to all unvisited neighbors
        unvisited = [j for j in range(k) if j not in curr.path]

        for nxt in unvisited:
            # Check edge weight
            edge_weight = local_matrix[curr.vertex][nxt]
            if edge_weight == float("inf"):
                # Missing corridor between these two zones
                continue

            node_counter += 1
            child_cost = curr.cost + edge_weight

            # Prepare child reduced matrix
            child_matrix = [row[:] for row in curr.reduced_matrix]

            # Set row curr.vertex to inf (cannot leave current again)
            for j in range(k):
                child_matrix[curr.vertex][j] = float("inf")
            # Set col nxt to inf (cannot enter nxt again)
            for i in range(k):
                child_matrix[i][nxt] = float("inf")
            # Set return edge to start to inf to prevent premature sub-tour (if not last step)
            if curr.level < k - 1:
                child_matrix[nxt][0] = float("inf")

            # Perform reduction on child matrix
            child_reduced, child_reduction_cost = reduce_matrix(child_matrix, k)
            child_bound = curr.bound + curr.reduced_matrix[curr.vertex][nxt] + child_reduction_cost

            child_global_v = local_to_global[nxt]
            child_name = id_to_name[child_global_v]
            child_path_global = [local_to_global[i] for i in curr.path + [nxt]]
            child_path_names = [id_to_name[gid] for gid in child_path_global]

            # Pruning check
            if child_bound >= best_cost:
                branches_pruned += 1
                execution_steps.append({
                    "step_index": len(execution_steps) + 1,
                    "node_id": node_counter,
                    "parent_id": curr.node_id,
                    "action": "PRUNE",
                    "partial_route": child_path_global,
                    "partial_names": child_path_names,
                    "current_vertex": child_global_v,
                    "current_name": child_name,
                    "accumulated_cost": round(child_cost, 2),
                    "lower_bound": round(child_bound, 2),
                    "best_cost_so_far": round(best_cost, 2) if best_cost < float("inf") else "None",
                    "reason": f"Pruned candidate branch to {child_name}: LB ({round(child_bound, 2)}) >= Best Cost ({round(best_cost, 2)}).",
                })
            else:
                child_node = TSPNode(
                    node_id=node_counter,
                    parent_id=curr.node_id,
                    vertex=nxt,
                    level=curr.level + 1,
                    path=curr.path + [nxt],
                    reduced_matrix=child_reduced,
                    cost=child_cost,
                    bound=child_bound,
                )
                heapq.heappush(pq, child_node)
                execution_steps.append({
                    "step_index": len(execution_steps) + 1,
                    "node_id": node_counter,
                    "parent_id": curr.node_id,
                    "action": "EXPLORE",
                    "partial_route": child_path_global,
                    "partial_names": child_path_names,
                    "current_vertex": child_global_v,
                    "current_name": child_name,
                    "accumulated_cost": round(child_cost, 2),
                    "lower_bound": round(child_bound, 2),
                    "best_cost_so_far": round(best_cost, 2) if best_cost < float("inf") else "None",
                    "reason": f"Exploring branch to {child_name} (Cost so far: {round(child_cost, 2)}, Lower Bound: {round(child_bound, 2)}).",
                })

    # Check if a valid tour was found
    if best_cost == float("inf") or not best_tour_local:
        return {
            "success": True,
            "tour_possible": False,
            "message": "No complete Hamiltonian tour exists for the selected warehouse locations with direct corridors.",
            "start_location": {"id": start_vertex_id, "name": id_to_name.get(start_vertex_id)},
            "selected_locations": [{"id": gid, "name": id_to_name.get(gid)} for gid in location_ids],
            "optimal_route_ids": [],
            "optimal_route_names": [],
            "total_cost": None,
            "nodes_explored": nodes_explored,
            "branches_pruned": branches_pruned,
            "execution_steps": execution_steps,
            "nearest_neighbor": None,
        }

    optimal_route_ids = [local_to_global[i] for i in best_tour_local]
    optimal_route_names = [id_to_name[gid] for gid in optimal_route_ids]

    # Calculate Nearest-Neighbor Greedy Heuristic for academic comparison
    nn_result = solve_tsp_nearest_neighbor(location_ids, local_matrix, local_to_global, id_to_name)

    # Final summary step
    execution_steps.append({
        "step_index": len(execution_steps) + 1,
        "node_id": 0,
        "parent_id": None,
        "action": "COMPLETE",
        "partial_route": optimal_route_ids,
        "partial_names": optimal_route_names,
        "current_vertex": optimal_route_ids[0],
        "current_name": optimal_route_names[0],
        "accumulated_cost": round(best_cost, 2),
        "lower_bound": round(best_cost, 2),
        "best_cost_so_far": round(best_cost, 2),
        "reason": f"Branch and Bound completed. Optimal tour cost: {round(best_cost, 2)}. Total search nodes explored: {nodes_explored}, branches pruned: {branches_pruned}.",
    })

    return {
        "success": True,
        "tour_possible": True,
        "algorithm": "Branch and Bound for TSP",
        "start_location": {"id": start_vertex_id, "name": id_to_name.get(start_vertex_id)},
        "selected_locations": [{"id": gid, "name": id_to_name.get(gid)} for gid in location_ids],
        "optimal_route_ids": optimal_route_ids,
        "optimal_route_names": optimal_route_names,
        "total_cost": round(best_cost, 2),
        "nodes_explored": nodes_explored,
        "branches_pruned": branches_pruned,
        "execution_steps": execution_steps,
        "nearest_neighbor": nn_result,
        "pruning_efficiency_percent": round((branches_pruned / max(1, nodes_explored + branches_pruned)) * 100, 1),
        "complexity": {
            "time_worst_case": "O(2^n * n^2) or O(n!) in worst case",
            "space": "O(n^2 * 2^n)",
            "pruning_benefit": "Bounding function eliminates entire branches whose lower bound exceeds current best tour.",
        },
    }


def solve_tsp_nearest_neighbor(
    location_ids: List[int],
    local_matrix: List[List[float]],
    local_to_global: List[int],
    id_to_name: Dict[int, str],
) -> Dict[str, Any]:
    """
    Computes a Nearest-Neighbor greedy heuristic tour for comparison with Branch and Bound.
    Note: Explicitly marked as non-optimal greedy heuristic.
    """
    k = len(location_ids)
    visited = [False] * k
    path = [0]
    visited[0] = True
    total_cost = 0.0
    possible = True

    curr = 0
    for _ in range(k - 1):
        best_nxt = -1
        best_dist = float("inf")
        for nxt in range(k):
            if not visited[nxt] and local_matrix[curr][nxt] < best_dist:
                best_dist = local_matrix[curr][nxt]
                best_nxt = nxt

        if best_nxt == -1 or best_dist == float("inf"):
            possible = False
            break

        path.append(best_nxt)
        visited[best_nxt] = True
        total_cost += best_dist
        curr = best_nxt

    # Return to start
    if possible:
        return_cost = local_matrix[curr][0]
        if return_cost < float("inf"):
            path.append(0)
            total_cost += return_cost
        else:
            possible = False

    if not possible:
        return {
            "possible": False,
            "message": "Greedy Nearest-Neighbor heuristic could not complete a tour (trapped at dead end).",
            "route_ids": [],
            "route_names": [],
            "total_cost": None,
        }

    route_ids = [local_to_global[i] for i in path]
    route_names = [id_to_name[gid] for gid in route_ids]

    return {
        "possible": True,
        "route_ids": route_ids,
        "route_names": route_names,
        "total_cost": round(total_cost, 2),
        "heuristic_name": "Nearest-Neighbor Greedy Heuristic (Non-Optimal)",
    }
