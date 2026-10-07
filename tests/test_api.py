"""
Integration tests for FastAPI endpoints.
Tests: Inventory endpoints, Alert Heap endpoints, Graph endpoints,
Dijkstra, Prim, Floyd-Warshall, and Knapsack endpoints.
"""

import pytest
from starlette.testclient import TestClient
from backend.main import app, load_initial_datasets


@pytest.fixture(autouse=True)
def reset_state():
    """Reset datasets before each test."""
    load_initial_datasets()


client = TestClient(app)


def test_frontend_serving():
    res = client.get("/")
    assert res.status_code == 200
    assert "Smart Warehouse" in res.text

    css = client.get("/static/css/style.css")
    assert css.status_code == 200
    assert "app-sidebar" in css.text

    js = client.get("/static/js/app.js")
    assert js.status_code == 200
    assert "App" in js.text


def test_api_inventory_crud():
    # 1. Get initial inventory
    res = client.get("/inventory")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] == 5

    # 2. Search existing SKU
    search_res = client.get("/inventory/search/SKU001")
    assert search_res.status_code == 200
    assert search_res.json()["item"]["sku"] == "SKU001"

    # 3. Add new item
    new_item = {
        "sku": "SKU006",
        "name": "Barcode Scanner",
        "category": "Electronics",
        "quantity": 15,
        "location": "Rack A",
        "priority": 6,
    }
    add_res = client.post("/inventory", json=new_item)
    assert add_res.status_code == 200
    assert add_res.json()["success"] is True

    # 4. Prevent duplicate SKU
    dup_res = client.post("/inventory", json=new_item)
    assert dup_res.status_code == 400

    # 5. Delete item
    del_res = client.delete("/inventory/SKU006")
    assert del_res.status_code == 200

    # 6. Delete non-existent item
    del_non_res = client.delete("/inventory/SKU999")
    assert del_non_res.status_code == 404


def test_api_alerts_heap():
    # 1. Get alerts
    res = client.get("/alerts")
    assert res.status_code == 200
    assert res.json()["size"] >= 3

    # 2. Peek top
    top_res = client.get("/alerts/top")
    assert top_res.status_code == 200
    assert top_res.json()["top_alert"]["priority"] == 9

    # 3. Insert new higher priority
    new_alert = {
        "sku": "SKU004",
        "alert_type": "Critical Fire Hazard",
        "priority": 10,
        "quantity": 0,
        "location": "Rack D",
    }
    client.post("/alerts", json=new_alert)

    top_after = client.get("/alerts/top").json()
    assert top_after["top_alert"]["priority"] == 10

    # 4. Extract
    ext_res = client.post("/alerts/extract")
    assert ext_res.status_code == 200
    assert ext_res.json()["extracted_alert"]["priority"] == 10


def test_api_graph_and_algorithms():
    # 1. Graph representation
    g_res = client.get("/graph")
    assert g_res.status_code == 200
    assert g_res.json()["num_vertices"] == 7

    # Adjacency list
    list_res = client.get("/graph/adjacency-list")
    assert list_res.status_code == 200
    assert list_res.json()["type"] == "Adjacency List"

    # Adjacency matrix
    matrix_res = client.get("/graph/adjacency-matrix")
    assert matrix_res.status_code == 200
    assert matrix_res.json()["type"] == "Adjacency Matrix"

    # 2. Dijkstra
    dijkstra_res = client.post("/dijkstra", json={"source_id": 0, "dest_id": 6})
    assert dijkstra_res.status_code == 200
    assert dijkstra_res.json()["result"]["total_cost"] == 18.0

    # 3. Prim MST
    prim_res = client.post("/prim", json={"start_node_id": 0})
    assert prim_res.status_code == 200
    assert prim_res.json()["result"]["total_cost"] == 21.0
    assert prim_res.json()["result"]["edge_count"] == 6

    # 4. Floyd-Warshall
    fw_res = client.post("/floyd-warshall")
    assert fw_res.status_code == 200

    query_res = client.post("/floyd-warshall/query", json={"source_id": 0, "dest_id": 6})
    assert query_res.status_code == 200
    assert query_res.json()["result"]["distance"] == 18


def test_api_knapsack():
    payload = {
        "items": [
            {"name": "Medical Kit", "weight": 4, "value": 10},
            {"name": "Tools", "weight": 6, "value": 13},
        ],
        "capacity": 10,
    }
    res = client.post("/knapsack", json=payload)
    assert res.status_code == 200
    assert res.json()["result"]["max_value"] == 23
