"""
FastAPI Backend Application for Smart Warehouse Inventory Management Platform.
Provides RESTful APIs for all manual DSA modules and serves the frontend dashboard.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.dsa.avl_tree import AVLTree
from backend.dsa.binary_heap import MaxHeap
from backend.dsa.graph import WarehouseGraph
from backend.dsa.dijkstra import dijkstra_shortest_path
from backend.dsa.prim import prim_mst
from backend.dsa.floyd_warshall import floyd_warshall_all_pairs, query_floyd_warshall_pair
from backend.dsa.knapsack import solve_01_knapsack
from backend.dsa.tsp_branch_bound import solve_tsp_branch_and_bound, solve_tsp_nearest_neighbor
from backend.dsa.b_plus_tree import BPlusTree
from backend.models.schemas import (
    InventoryItemSchema,
    AlertSchema,
    DijkstraRequest,
    PrimRequest,
    FloydWarshallQueryRequest,
    KnapsackRequest,
    GraphEdgeSchema,
    GraphVertexSchema,
    TSPRequest,
    BPlusProductSchema,
    BPlusRangeRequest,
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
FRONTEND_DIR = BASE_DIR.parent / "frontend"

app = FastAPI(
    title="Smart Warehouse Inventory Management Platform - DSA PBL",
    description="Academic prototype demonstrating custom DSA algorithms for warehouse operations.",
    version="1.0.0",
)

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory DSA state instances
avl_tree = AVLTree()
alert_heap = MaxHeap()
warehouse_graph = WarehouseGraph()
bplus_tree = BPlusTree(order=4)
latest_floyd_warshall: Dict[str, Any] = {}
default_knapsack_data: Dict[str, Any] = {}


def load_initial_datasets():
    """Load default sample inventory, warehouse network, and B+ tree data."""
    global avl_tree, alert_heap, warehouse_graph, bplus_tree, latest_floyd_warshall, default_knapsack_data

    # Reset
    avl_tree = AVLTree()
    alert_heap = MaxHeap()
    warehouse_graph = WarehouseGraph()
    bplus_tree = BPlusTree(order=4)


    # Load inventory
    inv_file = DATA_DIR / "inventory.json"
    if inv_file.exists():
        with open(inv_file, "r", encoding="utf-8") as f:
            items = json.load(f)
            for item in items:
                avl_tree.insert(item)

    # Load initial alerts
    initial_alerts = [
        {
            "sku": "SKU003",
            "alert_type": "Low Stock",
            "priority": 9,
            "quantity": 6,
            "location": "Rack C",
        },
        {
            "sku": "SKU002",
            "alert_type": "Low Stock",
            "priority": 8,
            "quantity": 8,
            "location": "Rack B",
        },
        {
            "sku": "SKU005",
            "alert_type": "Normal",
            "priority": 5,
            "quantity": 12,
            "location": "Rack C",
        },
    ]
    for alert in initial_alerts:
        alert_heap.insert(alert)

    # Load warehouse graph
    wh_file = DATA_DIR / "warehouse.json"
    if wh_file.exists():
        with open(wh_file, "r", encoding="utf-8") as f:
            wh_data = json.load(f)
            warehouse_graph = WarehouseGraph.from_config(wh_data)
            default_knapsack_data = {
                "items": wh_data.get("default_knapsack_items", []),
                "capacity": wh_data.get("default_capacity", 10),
            }
            # Pre-compute initial Floyd-Warshall cache
            latest_floyd_warshall = floyd_warshall_all_pairs(warehouse_graph)

    # Load B+ Tree sample products
    bplus_file = DATA_DIR / "bplus_products.json"
    if bplus_file.exists():
        with open(bplus_file, "r", encoding="utf-8") as f:
            bplus_items = json.load(f)
            for it in bplus_items:
                bplus_tree.insert(it)


# Initialize on module load
load_initial_datasets()



# =====================================================================
# 1. INVENTORY MANAGEMENT (AVL TREE) ENDPOINTS
# =====================================================================

@app.get("/inventory", summary="Get all inventory items (AVL Inorder Traversal)")
def get_inventory():
    items = avl_tree.inorder_traversal()
    return {
        "success": True,
        "count": len(items),
        "items": items,
        "rotations": avl_tree.rotation_stats,
        "tree_structure": avl_tree.to_tree_dict(),
        "algorithm": "AVL Tree (Self-Balancing BST)",
        "complexity": {"search": "O(log n)", "insert": "O(log n)", "delete": "O(log n)"},
    }


@app.post("/inventory", summary="Insert new SKU item into AVL Tree")
def add_inventory_item(item: InventoryItemSchema):
    item_dict = item.model_dump()
    success, message, comparisons = avl_tree.insert(item_dict)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return {
        "success": True,
        "message": message,
        "comparisons": comparisons,
        "rotations": avl_tree.rotation_stats,
        "item": item_dict,
        "algorithm": "AVL Tree Insert with Auto-Rebalancing",
        "complexity": "O(log n)",
    }


@app.get("/inventory/search/{sku}", summary="Search SKU in AVL Tree")
def search_inventory_item(sku: str):
    clean_sku = sku.strip().upper()
    if not clean_sku:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SKU cannot be blank.")
    item, comparisons, path = avl_tree.search(clean_sku)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SKU '{clean_sku}' not found in inventory. Comparisons performed: {comparisons}.",
        )
    return {
        "success": True,
        "item": item,
        "comparisons": comparisons,
        "search_path": path,
        "algorithm": "AVL Tree Search",
        "complexity": "O(log n)",
    }


@app.delete("/inventory/{sku}", summary="Delete SKU from AVL Tree")
def delete_inventory_item(sku: str):
    clean_sku = sku.strip().upper()
    if not clean_sku:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SKU cannot be blank.")
    success, message, comparisons = avl_tree.delete(clean_sku)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
    return {
        "success": True,
        "message": message,
        "comparisons": comparisons,
        "rotations": avl_tree.rotation_stats,
        "algorithm": "AVL Tree Delete with Rebalancing",
        "complexity": "O(log n)",
    }


@app.get("/inventory/traversals", summary="Get Inorder and Preorder Traversals")
def get_inventory_traversals():
    return {
        "inorder": avl_tree.inorder_traversal(),
        "preorder": avl_tree.preorder_traversal(),
        "explanation": {
            "inorder": "Left-Root-Right: Produces inventory items in alphabetical/lexicographical order of SKU.",
            "preorder": "Root-Left-Right: Shows root node followed by left and right subtrees.",
        },
    }


# =====================================================================
# 2. PRIORITY ALERTS (BINARY MAX HEAP) ENDPOINTS
# =====================================================================

@app.post("/alerts", summary="Insert alert into Priority Queue (Max Heap)")
def add_alert(alert: AlertSchema):
    new_alert = alert_heap.insert(alert.model_dump())
    return {
        "success": True,
        "message": f"Alert for {new_alert.sku} (Priority {new_alert.priority}) added to Max Heap.",
        "alert": new_alert.to_dict(),
        "heap_size": alert_heap.size(),
        "algorithm": "Binary Max Heap Insert with Heapify-Up",
        "complexity": "O(log n)",
    }


@app.get("/alerts", summary="View all warehouse alerts in heap array order")
def get_alerts():
    return {
        "success": True,
        "size": alert_heap.size(),
        "alerts": alert_heap.display_heap(),
        "top_alert": alert_heap.peek(),
        "algorithm": "Binary Max Heap",
        "complexity": {"insert": "O(log n)", "peek": "O(1)", "extract_max": "O(log n)"},
    }


@app.get("/alerts/top", summary="Peek highest-priority alert without removing")
def peek_top_alert():
    top = alert_heap.peek()
    if not top:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert heap is currently empty.")
    return {
        "success": True,
        "top_alert": top,
        "algorithm": "Binary Max Heap Peek (Root Access)",
        "complexity": "O(1)",
    }


@app.post("/alerts/extract", summary="Extract highest-priority alert")
def extract_highest_alert():
    extracted = alert_heap.extract_max()
    if not extracted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert heap is empty. Nothing to extract.")
    return {
        "success": True,
        "message": f"Extracted critical alert for SKU {extracted['sku']}",
        "extracted_alert": extracted,
        "remaining_alerts_count": alert_heap.size(),
        "algorithm": "Binary Max Heap Extract-Max with Heapify-Down",
        "complexity": "O(log n)",
    }


# =====================================================================
# 3. WAREHOUSE GRAPH REPRESENTATIONS ENDPOINTS
# =====================================================================

@app.get("/graph", summary="Get warehouse graph structure and visualization data")
def get_warehouse_graph():
    return {
        "vertices": warehouse_graph.vertices,
        "edges": warehouse_graph.get_edges_list(),
        "num_vertices": len(warehouse_graph.vertices),
        "num_edges": len(warehouse_graph.get_edges_list()),
    }


@app.get("/graph/adjacency-list", summary="Get Adjacency List representation")
def get_graph_adj_list():
    return warehouse_graph.get_adjacency_list()


@app.get("/graph/adjacency-matrix", summary="Get Adjacency Matrix representation")
def get_graph_adj_matrix():
    return warehouse_graph.get_adjacency_matrix()


@app.post("/graph/reset", summary="Reset graph to default warehouse layout")
def reset_graph():
    load_initial_datasets()
    return {
        "success": True,
        "message": "Warehouse graph and dataset reset to initial state.",
        "graph": get_warehouse_graph(),
    }


@app.post("/graph/edge", summary="Add custom edge to graph")
def add_custom_edge(edge: GraphEdgeSchema):
    try:
        warehouse_graph.add_edge(edge.u, edge.v, edge.weight)
        global latest_floyd_warshall
        latest_floyd_warshall = floyd_warshall_all_pairs(warehouse_graph)
        return {
            "success": True,
            "message": f"Edge added between {warehouse_graph.id_to_name[edge.u]} and {warehouse_graph.id_to_name[edge.v]} (Weight: {edge.weight})",
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# =====================================================================
# 4. DIJKSTRA SHORTEST PATH ENDPOINTS
# =====================================================================

@app.post("/dijkstra", summary="Calculate shortest path between two locations")
def run_dijkstra(req: DijkstraRequest):
    try:
        result = dijkstra_shortest_path(warehouse_graph, req.source_id, req.dest_id)
        return {
            "success": True,
            "algorithm": "Dijkstra's Single-Source Shortest Path (Custom Min-Heap)",
            "purpose": "Find the lowest-cost movement route between two warehouse locations",
            "result": result,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# =====================================================================
# 5. PRIM'S MINIMUM SPANNING TREE (MST) ENDPOINTS
# =====================================================================

@app.post("/prim", summary="Generate Minimum Spanning Tree for the warehouse")
def run_prim(req: PrimRequest = PrimRequest(start_node_id=0)):
    try:
        result = prim_mst(warehouse_graph, req.start_node_id)
        return {
            "success": True,
            "algorithm": "Prim's Minimum Spanning Tree (Custom Min-Heap)",
            "purpose": "Construct the minimum-cost connectivity network connecting all warehouse zones",
            "result": result,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# =====================================================================
# 6. FLOYD-WARSHALL ALL-PAIRS SHORTEST PATH ENDPOINTS
# =====================================================================

@app.post("/floyd-warshall", summary="Run Floyd-Warshall on Adjacency Matrix")
def run_floyd_warshall():
    global latest_floyd_warshall
    latest_floyd_warshall = floyd_warshall_all_pairs(warehouse_graph)
    return {
        "success": True,
        "algorithm": "Floyd-Warshall Dynamic Programming",
        "purpose": "Find shortest movement distances between ALL pairs of warehouse locations",
        "result": {
            "headers": latest_floyd_warshall["headers"],
            "initial_matrix": latest_floyd_warshall["initial_matrix"],
            "final_matrix": latest_floyd_warshall["final_matrix"],
            "intermediate_steps": latest_floyd_warshall["intermediate_steps"],
            "complexity": latest_floyd_warshall["complexity"],
        },
    }


@app.post("/floyd-warshall/query", summary="Query shortest distance between a specific pair from computed matrix")
def query_floyd_warshall(req: FloydWarshallQueryRequest):
    global latest_floyd_warshall
    if not latest_floyd_warshall:
        latest_floyd_warshall = floyd_warshall_all_pairs(warehouse_graph)
    try:
        result = query_floyd_warshall_pair(warehouse_graph, latest_floyd_warshall, req.source_id, req.dest_id)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# =====================================================================
# 7. DYNAMIC PROGRAMMING (0/1 KNAPSACK) ENDPOINTS
# =====================================================================

@app.get("/knapsack/default", summary="Get default sample knapsack items and capacity")
def get_default_knapsack():
    return default_knapsack_data


@app.post("/knapsack", summary="Solve 0/1 Knapsack for dispatch picking")
def run_knapsack(req: KnapsackRequest):
    try:
        raw_items = [it.model_dump() for it in req.items]
        result = solve_01_knapsack(raw_items, req.capacity)
        return {
            "success": True,
            "algorithm": "0/1 Knapsack Dynamic Programming",
            "purpose": "Select optimal combination of warehouse items to maximize priority within cart/dispatch capacity",
            "result": result,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# =====================================================================
# 8. DASHBOARD OVERVIEW ENDPOINT
# =====================================================================

@app.get("/dashboard/stats", summary="Overview metrics for Dashboard")
def get_dashboard_stats():
    inventory_items = avl_tree.inorder_traversal()
    internals, leaves = bplus_tree.count_nodes()
    return {
        "total_inventory_items": len(inventory_items),
        "total_stock_units": sum(it.get("quantity", 0) for it in inventory_items),
        "warehouse_locations_count": len(warehouse_graph.vertices),
        "warehouse_routes_count": len(warehouse_graph.get_edges_list()),
        "active_alerts_count": alert_heap.size(),
        "highest_priority_alert": alert_heap.peek(),
        "default_dispatch_capacity": default_knapsack_data.get("capacity", 10),
        "total_bplus_products": bplus_tree.size,
        "bplus_tree_height": bplus_tree.get_height(),
        "bplus_leaf_count": leaves,
        "bplus_internal_count": internals,
    }


# =====================================================================
# 9. WAREHOUSE ROUTE OPTIMIZER (TSP BRANCH AND BOUND) ENDPOINTS
# =====================================================================

@app.get("/tsp/locations", summary="Get all warehouse locations selectable for TSP tour")
def get_tsp_locations():
    return {
        "success": True,
        "locations": warehouse_graph.vertices,
        "count": len(warehouse_graph.vertices),
    }


@app.post("/tsp/solve", summary="Solve TSP tour using Branch and Bound")
def run_tsp(req: TSPRequest):
    try:
        adj = warehouse_graph.adj_matrix
        n = len(warehouse_graph.vertices)

        # Validate location IDs
        for loc_id in req.selected_location_ids:
            if loc_id < 0 or loc_id >= n:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid location ID {loc_id}")
        if req.start_location_id not in req.selected_location_ids:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start location must be among selected locations.")

        # Build submatrix of direct edge weights for selected locations
        k = len(req.selected_location_ids)
        sub_matrix = [[float("inf")] * k for _ in range(k)]
        for i, u in enumerate(req.selected_location_ids):
            for j, v in enumerate(req.selected_location_ids):
                if i == j:
                    sub_matrix[i][j] = float("inf")
                else:
                    sub_matrix[i][j] = adj[u][v]

        result = solve_tsp_branch_and_bound(
            location_ids=req.selected_location_ids,
            cost_matrix=sub_matrix,
            id_to_name=warehouse_graph.id_to_name,
            start_vertex_id=req.start_location_id,
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# =====================================================================
# 10. ADVANCED INVENTORY SEARCH (B+ TREE) ENDPOINTS
# =====================================================================

@app.get("/bplus/products", summary="Get all inventory products in sorted order via linked leaves")
def get_bplus_products():
    records = bplus_tree.get_all_records_sorted()
    internals, leaves = bplus_tree.count_nodes()
    return {
        "success": True,
        "count": len(records),
        "products": records,
        "tree_stats": {
            "total_products": bplus_tree.size,
            "tree_height": bplus_tree.get_height(),
            "internal_nodes_count": internals,
            "leaf_nodes_count": leaves,
            "order": bplus_tree.order,
            "max_keys": bplus_tree.max_keys,
            "min_keys": bplus_tree.min_keys,
        },
        "tree_hierarchy": bplus_tree.to_tree_hierarchy(),
        "algorithm": "B+ Tree (Multi-Way Balanced Search Tree with Linked Leaves)",
        "complexity": {
            "search": f"O(log_{bplus_tree.order} n)",
            "insert": f"O(log_{bplus_tree.order} n)",
            "range_query": f"O(log_{bplus_tree.order} n + K)",
            "traversal": "O(n) via sequential leaf pointers",
        },
    }


@app.post("/bplus/product", summary="Insert new product into B+ Tree")
def add_bplus_product(product: BPlusProductSchema):
    prod_dict = product.model_dump()
    success, message, split_events = bplus_tree.insert(prod_dict)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    internals, leaves = bplus_tree.count_nodes()
    return {
        "success": True,
        "message": message,
        "product": prod_dict,
        "split_events": split_events,
        "tree_stats": {
            "total_products": bplus_tree.size,
            "tree_height": bplus_tree.get_height(),
            "internal_nodes_count": internals,
            "leaf_nodes_count": leaves,
            "order": bplus_tree.order,
        },
        "tree_hierarchy": bplus_tree.to_tree_hierarchy(),
    }


@app.get("/bplus/search/{product_id}", summary="Search product by Product ID in B+ Tree")
def search_bplus_product(product_id: str):
    clean_id = product_id.strip().upper()
    if not clean_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product ID cannot be blank.")
    record, found, path, comparisons = bplus_tree.search(clean_id)
    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product ID '{clean_id}' not found in B+ Tree index. Comparisons: {comparisons}.",
        )
    return {
        "success": True,
        "found": True,
        "product": record,
        "comparisons": comparisons,
        "search_path": path,
        "algorithm": "B+ Tree Point Search",
        "complexity": f"O(log_{bplus_tree.order} n)",
    }


@app.post("/bplus/range", summary="Range search between two Product IDs using linked leaves")
def range_bplus_products(req: BPlusRangeRequest):
    result = bplus_tree.range_query(req.min_product_id, req.max_product_id)
    return result


@app.get("/bplus/tree", summary="Get complete B+ Tree structural hierarchy for visualization")
def get_bplus_tree():
    return {
        "success": True,
        "tree": bplus_tree.to_tree_hierarchy(),
    }


@app.post("/bplus/reset", summary="Reset B+ Tree to default sample warehouse inventory")
def reset_bplus_tree():
    global bplus_tree
    bplus_tree = BPlusTree(order=4)
    bplus_file = DATA_DIR / "bplus_products.json"
    if bplus_file.exists():
        with open(bplus_file, "r", encoding="utf-8") as f:
            bplus_items = json.load(f)
            for it in bplus_items:
                bplus_tree.insert(it)
    internals, leaves = bplus_tree.count_nodes()
    return {
        "success": True,
        "message": "B+ Tree index reset to default sample warehouse products.",
        "tree_stats": {
            "total_products": bplus_tree.size,
            "tree_height": bplus_tree.get_height(),
            "internal_nodes_count": internals,
            "leaf_nodes_count": leaves,
            "order": bplus_tree.order,
        },
        "tree_hierarchy": bplus_tree.to_tree_hierarchy(),
    }



# =====================================================================
# FRONTEND STATIC FILES SERVING
# =====================================================================

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend_index():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "Frontend index.html not found"}
