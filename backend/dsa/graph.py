"""
Warehouse Graph Data Structures: Adjacency List and Adjacency Matrix.

Academic Purpose:
Demonstrates dual representation of the same weighted graph:
1. Adjacency List: Space Complexity O(V + E), ideal for sparse warehouse graphs.
2. Adjacency Matrix: Space Complexity O(V^2), ideal for dense graphs and Floyd-Warshall DP.
"""

from typing import List, Dict, Any, Tuple, Optional


class WarehouseGraph:
    """
    Weighted Undirected Graph representing warehouse navigation network.
    Maintains synchronized Adjacency List and Adjacency Matrix representations.
    """

    def __init__(self):
        self.vertices: List[Dict[str, Any]] = []
        self.name_to_id: Dict[str, int] = {}
        self.id_to_name: Dict[int, str] = {}
        # Adjacency List: {u: [(v, weight), ...]}
        self.adj_list: Dict[int, List[Tuple[int, float]]] = {}
        # Adjacency Matrix: 2D list of size V x V
        self.adj_matrix: List[List[float]] = []

    def get_num_vertices(self) -> int:
        return len(self.vertices)

    def add_vertex(self, vertex_id: int, name: str, x: int = 0, y: int = 0) -> None:
        """Add a warehouse location node."""
        if vertex_id in self.id_to_name:
            raise ValueError(f"Vertex ID {vertex_id} already exists.")
        if name in self.name_to_id:
            raise ValueError(f"Vertex name '{name}' already exists.")

        self.vertices.append({"id": vertex_id, "name": name, "x": x, "y": y})
        self.name_to_id[name] = vertex_id
        self.id_to_name[vertex_id] = name
        self.adj_list[vertex_id] = []
        self._rebuild_matrix()

    def add_edge(self, u: int, v: int, weight: float) -> None:
        """
        Add undirected edge between u and v with non-negative weight.
        """
        if u not in self.id_to_name or v not in self.id_to_name:
            raise ValueError(f"Invalid edge: endpoints {u} or {v} do not exist.")
        if weight < 0:
            raise ValueError(f"Negative weight {weight} not allowed in warehouse graph.")
        if u == v:
            raise ValueError("Self-loops are not allowed in warehouse navigation.")

        # Check if edge already exists in adj_list and update or add
        updated_u = False
        for i, (neighbor, _) in enumerate(self.adj_list[u]):
            if neighbor == v:
                self.adj_list[u][i] = (v, float(weight))
                updated_u = True
                break
        if not updated_u:
            self.adj_list[u].append((v, float(weight)))

        updated_v = False
        for i, (neighbor, _) in enumerate(self.adj_list[v]):
            if neighbor == u:
                self.adj_list[v][i] = (u, float(weight))
                updated_v = True
                break
        if not updated_v:
            self.adj_list[v].append((u, float(weight)))

        self._rebuild_matrix()

    def _rebuild_matrix(self) -> None:
        """Reconstruct the V x V Adjacency Matrix."""
        n = len(self.vertices)
        # Initialize matrix with infinity (or 0 for diagonal)
        # Using float('inf') for non-adjacent nodes is standard for shortest-path algorithms
        self.adj_matrix = [[float("inf")] * n for _ in range(n)]

        for i in range(n):
            self.adj_matrix[i][i] = 0.0

        for u in self.adj_list:
            if u < n:
                for v, weight in self.adj_list[u]:
                    if v < n:
                        self.adj_matrix[u][v] = float(weight)

    def get_adjacency_list(self) -> Dict[str, Any]:
        """
        Returns readable Adjacency List with location names and weights.
        Complexity: Space O(V + E)
        """
        readable_list: Dict[str, List[Dict[str, Any]]] = {}
        for u, neighbors in self.adj_list.items():
            u_name = self.id_to_name.get(u, f"Node-{u}")
            readable_list[u_name] = [
                {
                    "neighbor_id": v,
                    "neighbor_name": self.id_to_name.get(v, f"Node-{v}"),
                    "weight": weight,
                }
                for v, weight in neighbors
            ]
        return {
            "type": "Adjacency List",
            "space_complexity": "O(V + E)",
            "num_vertices": len(self.vertices),
            "num_edges": sum(len(n) for n in self.adj_list.values()) // 2,
            "data": readable_list,
        }

    def get_adjacency_matrix(self) -> Dict[str, Any]:
        """
        Returns 2D Adjacency Matrix with header names.
        Complexity: Space O(V^2)
        """
        headers = [v["name"] for v in self.vertices]
        display_matrix = []
        for row in self.adj_matrix:
            display_row = []
            for val in row:
                if val == float("inf"):
                    display_row.append("∞")
                else:
                    display_row.append(int(val) if val.is_integer() else round(val, 2))
            display_matrix.append(display_row)

        json_raw = [
            [None if val == float("inf") else val for val in row]
            for row in self.adj_matrix
        ]
        return {
            "type": "Adjacency Matrix",
            "space_complexity": "O(V²)",
            "num_vertices": len(self.vertices),
            "headers": headers,
            "raw_matrix": json_raw,
            "display_matrix": display_matrix,
        }

    def get_edges_list(self) -> List[Dict[str, Any]]:
        """Return unique undirected edges."""
        edges = []
        seen = set()
        for u in self.adj_list:
            for v, weight in self.adj_list[u]:
                edge_key = tuple(sorted([u, v]))
                if edge_key not in seen:
                    seen.add(edge_key)
                    edges.append({
                        "u": u,
                        "v": v,
                        "u_name": self.id_to_name[u],
                        "v_name": self.id_to_name[v],
                        "weight": weight,
                    })
        return edges

    @classmethod
    def from_config(cls, data: Dict[str, Any]) -> "WarehouseGraph":
        """Instantiate and populate graph from config dataset."""
        graph = cls()
        for v in data.get("vertices", []):
            graph.add_vertex(v["id"], v["name"], v.get("x", 0), v.get("y", 0))
        for e in data.get("edges", []):
            graph.add_edge(e["u"], e["v"], float(e["weight"]))
        return graph
