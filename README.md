# Academic DSA Project – Smart Warehouse Inventory Management Platform

> **Course:** Data Structures and Algorithms - II (DSA-II)  
> **Curriculum:** B.Tech Computer Science & Engineering (PBL Track)  
> **Status:** Fully Functional Academic Prototype  
> **Repository:** [yogesshh-27/DSA-Support-Material](https://github.com/yogesshh-27/DSA-Support-Material)

---

## 1. Project Overview

The **Smart Warehouse Inventory Management Platform** is an academic software prototype developed for B.Tech CSE Data Structures and Algorithms-II Project-Based Learning (PBL). It demonstrates how core advanced data structures and classic algorithms directly model and optimize fundamental physical operations within a modern automated warehouse distribution facility.

### Core Philosophy: Academic Integrity
- **Zero Third-Party Algorithm Libraries:** No external libraries like `networkx`, `scipy.spatial`, or pre-packaged tree/graph structures are used for the algorithmic computations.
- **Manual Implementations:** All algorithms (AVL Tree, Binary Max Heap, Adjacency List & Matrix, Min-Heap Priority Queue, Dijkstra's Algorithm, Prim's Minimum Spanning Tree, Floyd-Warshall All-Pairs DP, and 0/1 Knapsack DP) are implemented **from scratch** in pure Python.
- **Full Traceability:** The backend computes and exposes internal states (comparisons, rotations, visited orders, relaxations, and full 2D dynamic programming matrices) to provide transparent visualization and easy viva explanation.

---

## 2. Architecture & Design

The platform follows a clean, modular 4-tier academic architecture:

```
[ Frontend: HTML5 / Vanilla CSS / JavaScript ]
                   │
                   ▼ (HTTP JSON REST APIs)
[ Application Layer: FastAPI Backend Services ]
                   │
                   ▼
[ Pure DSA Core: Manual Python Data Structures & Algorithms ]
  ├── AVL Tree (Self-balancing BST)
  ├── Binary Max Heap (Priority Queue)
  ├── Warehouse Graph (Dual: Adjacency List & Matrix)
  ├── Min-Heap Priority Queue (Internal to Dijkstra & Prim)
  ├── Dijkstra's Algorithm (Single-Source Shortest Path)
  ├── Prim's Algorithm (Minimum Spanning Tree)
  ├── Floyd-Warshall Algorithm (All-Pairs Shortest Path DP)
  └── 0/1 Knapsack Algorithm (Dispatch Optimization DP)
                   │
                   ▼
[ Warehouse Datasets: inventory.json & warehouse.json ]
```

---

## 3. Data Structures & Algorithms (Viva Guide)

Every module is designed around the **WHAT &bull; WHY &bull; INPUT &bull; OUTPUT &bull; COMPLEXITY** framework:

### 3.1 Inventory Management – AVL Tree
* **WHAT:** Self-Balancing Binary Search Tree maintaining balance factor $|h(L) - h(R)| \le 1$.
* **WHY:** Standard BSTs can degrade to $O(n)$ skewed lists upon sequential SKU ingestion. The AVL Tree guarantees worst-case $O(\log n)$ SKU searches during high-velocity order picking.
* **Rotations Implemented:**
  1. Left Rotation (RR imbalance)
  2. Right Rotation (LL imbalance)
  3. Left-Right Rotation (LR imbalance)
  4. Right-Left Rotation (RL imbalance)
* **INPUT:** Item SKU (`SKU001`..`SKU005`), Name, Category, Quantity, Location, Priority.
* **OUTPUT:** Retrieved item record, rotation event counters, Inorder traversal (lexicographical SKU ordering), Preorder traversal (structural hierarchy).
* **COMPLEXITY:**
  * Search: $\mathcal{O}(\log n)$
  * Insertion: $\mathcal{O}(\log n)$
  * Deletion: $\mathcal{O}(\log n)$
  * Space: $\mathcal{O}(n)$

### 3.2 Warehouse Alerts – Binary Max Heap
* **WHAT:** Array-based Complete Binary Tree maintaining the max-heap property: $A[\text{parent}(i)] \ge A[i]$.
* **WHY:** Warehouse operators need instant $\mathcal{O}(1)$ inspection of critical emergencies (e.g., Priority 10 Critical Stockout, Priority 8 Low Stock, Priority 5 Normal).
* **INPUT:** Alert record (SKU, Alert Type, Priority [1..10], Quantity, Location).
* **OUTPUT:** Highest priority alert via `peek()` / `extract_max()`, dynamic heap array view with parent-child relationship tracking.
* **COMPLEXITY:**
  * Insert: $\mathcal{O}(\log n)$ (Heapify-Up)
  * Peek: $\mathcal{O}(1)$
  * Extract-Max: $\mathcal{O}(\log n)$ (Heapify-Down)
  * Space: $\mathcal{O}(n)$

### 3.3 Warehouse Network – Graph Representations
* **WHAT:** Dual graph representations: Adjacency List and Adjacency Matrix.
* **WHY:**
  * **Adjacency List:** $\mathcal{O}(V + E)$ space, optimal for sparse warehouse layouts and neighbor exploration.
  * **Adjacency Matrix:** $\mathcal{O}(V^2)$ space, provides instant $\mathcal{O}(1)$ edge weight lookups and acts as the initial distance matrix $D^{(0)}$ for Floyd-Warshall.
* **INPUT:** 7 Warehouse locations ($0$: Receiving, $1$: Rack A, $2$: Rack B, $3$: Rack C, $4$: Rack D, $5$: Packing Zone, $6$: Dispatch Bay) and 11 movement aisles.
* **COMPLEXITY:**
  * Adjacency List Space: $\mathcal{O}(V + E)$
  * Adjacency Matrix Space: $\mathcal{O}(V^2)$

### 3.4 Routing – Dijkstra's Algorithm
* **WHAT:** Single-Source Shortest Path using a custom Min-Heap Priority Queue.
* **WHY:** Directs automated guided vehicles (AGVs) or human pickers along the shortest aisle route from a source to destination to minimize travel time and energy.
* **INPUT:** Source ID, Destination ID, non-negative aisle distance weights.
* **OUTPUT:** Minimum total travel cost, exact sequence of zones, step-by-step edge relaxation log.
* **COMPLEXITY:**
  * Time: $\mathcal{O}((V + E) \log V)$
  * Space: $\mathcal{O}(V)$

### 3.5 Network Optimization – Prim's Algorithm (MST)
* **WHAT:** Minimum Spanning Tree algorithm using a custom Min-Heap Priority Queue.
* **WHY:** Determines the lowest-cost infrastructure backbone (e.g., conveyor belts, pneumatic tubes, or network cables) that interconnects all $V$ warehouse locations with $V-1$ edges without cycles.
* **CRITICAL VIVA DISTINCTION:**
  * **Dijkstra** minimizes total distance from *one source* to destinations.
  * **Prim** minimizes the *sum of all selected edges* connecting *all vertices*.
* **COMPLEXITY:**
  * Time: $\mathcal{O}((V + E) \log V)$
  * Space: $\mathcal{O}(V + E)$

### 3.6 All-Pairs Shortest Path – Floyd-Warshall Algorithm
* **WHAT:** Dynamic Programming algorithm operating over the Adjacency Matrix:
  $$D^{(k)}[i][j] = \min\left(D^{(k-1)}[i][j],\, D^{(k-1)}[i][k] + D^{(k-1)}[k][j]\right)$$
* **WHY:** Pre-calculates an all-pairs distance lookup matrix. During multi-order batch picking, the warehouse dispatch system queries distance between any two locations in $\mathcal{O}(1)$ time.
* **INPUT:** Initial distance matrix $D^{(0)}$ with edge weights and $\infty$.
* **OUTPUT:** Initial matrix $D^{(0)}$, Final shortest distance matrix $D^{(V)}$, and predecessor path reconstruction.
* **COMPLEXITY:**
  * Time: $\mathcal{O}(V^3)$
  * Space: $\mathcal{O}(V^2)$

### 3.7 Dispatch Picking Optimization – 0/1 Knapsack
* **WHAT:** Dynamic Programming optimization using a 2D table $dp[i][w]$:
  $$dp[i][w] = \begin{cases} 
  dp[i-1][w] & \text{if } w_i > w \\ 
  \max\left(dp[i-1][w],\, dp[i-1][w - w_i] + v_i\right) & \text{if } w_i \le w 
  \end{cases}$$
* **WHY:** Picking carts or delivery dispatch vans have a strict maximum weight limit $W$. Selects the optimal combination of discrete packages to maximize overall priority fulfillment without exceeding cart capacity.
* **INPUT:** Items pool (Weight $w_i$, Priority Value $v_i$) and maximum capacity $W$.
* **OUTPUT:** Maximum achieved priority value, total weight, selected items list, complete 2D DP matrix ($0..n \times 0..W$), and backtracking decision trace.
* **COMPLEXITY:**
  * Time: $\mathcal{O}(n \cdot W)$
  * Space: $\mathcal{O}(n \cdot W)$

---

## 4. Master Complexity Summary Table

| Data Structure / Algorithm | Operation / Role | Time Complexity | Space Complexity |
| :--- | :--- | :--- | :--- |
| **AVL Tree** | Search SKU | $\mathcal{O}(\log n)$ | $\mathcal{O}(n)$ |
| **AVL Tree** | Insert SKU | $\mathcal{O}(\log n)$ | $\mathcal{O}(n)$ |
| **AVL Tree** | Delete SKU | $\mathcal{O}(\log n)$ | $\mathcal{O}(n)$ |
| **Binary Max Heap** | Peek Top Alert | $\mathcal{O}(1)$ | $\mathcal{O}(n)$ |
| **Binary Max Heap** | Insert / Extract-Max | $\mathcal{O}(\log n)$ | $\mathcal{O}(n)$ |
| **Adjacency List** | Graph Representation | $\mathcal{O}(\text{deg}(u))$ lookup | $\mathcal{O}(V + E)$ |
| **Adjacency Matrix** | Graph Representation | $\mathcal{O}(1)$ edge check | $\mathcal{O}(V^2)$ |
| **Dijkstra's Algorithm** | Single-Source Shortest Route | $\mathcal{O}((V + E) \log V)$ | $\mathcal{O}(V)$ |
| **Prim's Algorithm** | Minimum Spanning Tree | $\mathcal{O}((V + E) \log V)$ | $\mathcal{O}(V + E)$ |
| **Floyd-Warshall** | All-Pairs Shortest Distances | $\mathcal{O}(V^3)$ | $\mathcal{O}(V^2)$ |
| **0/1 Knapsack** | Dispatch Cargo Optimization | $\mathcal{O}(n \cdot W)$ | $\mathcal{O}(n \cdot W)$ |

---

## 5. Academic Scope & Syllabus Exclusions

The following algorithms are part of the standard B.Tech DSA-II syllabus but were **intentionally excluded** from the warehouse platform:

| Syllabus Algorithm | Academic Rationale for Exclusion |
| :--- | :--- |
| **Kruskal's Algorithm** | Both Prim and Kruskal find the MST. Prim was selected because warehouse networks are localized and dense with an intuitive central root (Receiving Bay). |
| **Bellman-Ford** | Warehouse movement costs and aisle lengths are strictly non-negative. Dijkstra with a Min-Heap solves the problem in $\mathcal{O}((V+E)\log V)$ compared to Bellman-Ford's slower $\mathcal{O}(V \cdot E)$. |
| **Warshall's Transitive Closure** | Transitive closure only indicates boolean reachability ($0$ or $1$). Real-world warehouse logistics requires exact quantitative movement costs, provided by Floyd-Warshall. |
| **Longest Common Subsequence (LCS)** | Tailored to genomic sequences or diff utilities; has no meaningful physical mapping to warehouse storage or vehicle routing. |
| **Matrix Chain Multiplication (MCM)** | Optimizes matrix multiplication parenthesization, which does not govern physical material handling. |
| **Resource Allocation** | 0/1 Knapsack directly models weight-limited cart picking, providing a more transparent dynamic programming demonstration. |

---

## 6. Directory Structure

```
DSA PBL/
├── backend/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application & REST endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py           # Pydantic validation schemas
│   ├── dsa/                     # Pure DSA implementations (Zero external libs)
│   │   ├── __init__.py
│   │   ├── avl_tree.py          # AVL tree with 4 rotations & traversals
│   │   ├── binary_heap.py       # Max Heap priority queue for alerts
│   │   ├── graph.py             # Graph with Adjacency List & Matrix
│   │   ├── dijkstra.py          # Custom Min-Heap Dijkstra algorithm
│   │   ├── prim.py              # Custom Min-Heap Prim MST algorithm
│   │   ├── floyd_warshall.py    # All-pairs DP with matrix reconstruction
│   │   └── knapsack.py          # 0/1 Knapsack with 2D DP table & backtracking
│   └── data/
│       ├── inventory.json       # Initial sample inventory (SKU001 - SKU005)
│       └── warehouse.json       # Standard warehouse graph (7 nodes, 11 edges)
├── frontend/
│   ├── index.html               # Semantic academic UI with 9 sections
│   ├── css/
│   │   └── style.css            # Minimal academic stylesheet (light theme)
│   └── js/
│       ├── api.js               # Clean REST client wrapper
│       ├── graph_canvas.js      # HTML5 Canvas warehouse network renderer
│       └── app.js               # Event controller & UI state management
├── tests/
│   ├── __init__.py
│   ├── test_avl_tree.py         # AVL unit tests (rotations, balance, delete)
│   ├── test_binary_heap.py      # Heap unit tests (insert, peek, extract)
│   ├── test_graph_algorithms.py # Dijkstra, Prim, Floyd-Warshall, edge cases
│   ├── test_knapsack.py         # Knapsack DP table, backtracking, edge cases
│   └── test_api.py              # FastAPI endpoints & static file serving tests
├── .gitignore
├── pytest.ini (optional)
└── README.md
```

---

## 7. Installation & Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.12 / 3.14)
- Web browser (Chrome, Edge, Firefox)

### Step 1: Install Dependencies
```bash
pip install fastapi uvicorn pydantic pytest starlette httpx
```

### Step 2: Start the Backend Server
Run the FastAPI application from the project root:
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 3: Open the Dashboard
Open your web browser and navigate to:
```
http://127.0.0.1:8000
```
*(The FastAPI backend automatically mounts and serves the `frontend/` directory).*

Interactive Swagger API Documentation is also accessible at:
```
http://127.0.0.1:8000/docs
```

---

## 8. Running Automated Unit Tests

A comprehensive suite of **27 unit and integration tests** verifies every algorithm, rotation case, priority queue action, and edge condition:

```bash
python -m pytest tests/ -v
```

### Test Coverage Highlights:
- **AVL Tree:** Insertion, duplicate SKU rejection, search path, Left-Left, Right-Right, Left-Right, Right-Left rotations, height balance validation, leaf & internal node deletion, Inorder and Preorder traversals.
- **Binary Heap:** Insertion, peek $\mathcal{O}(1)$, sequential extract-max priority order verification, empty heap handling.
- **Graph & Routing:** Adjacency List and Matrix symmetry, negative weight rejection, Dijkstra shortest path ($18.0$), Prim MST ($21.0$, $6$ edges), Floyd-Warshall all-pairs distance matrix, disconnected graph handling, invalid vertex IDs.
- **0/1 Knapsack:** Sample data optimal value ($23$), 2D DP table dimensions, zero-capacity edge case, empty item list, invalid negative weight validation.
- **API Endpoints:** Complete HTTP CRUD cycle for inventory, alerts, graph calculations, and static asset serving.

---

## 9. Sample Datasets

### Initial Inventory (`backend/data/inventory.json`)
* `SKU001`: Wireless Keyboard &bull; Electronics &bull; Qty: 25 &bull; Location: Rack A &bull; Priority: 5
* `SKU002`: Wireless Mouse &bull; Electronics &bull; Qty: 8 &bull; Location: Rack B &bull; Priority: 8
* `SKU003`: USB Cable &bull; Accessories &bull; Qty: 6 &bull; Location: Rack C &bull; Priority: 9
* `SKU004`: Notebook &bull; Stationery &bull; Qty: 120 &bull; Location: Rack D &bull; Priority: 2
* `SKU005`: Headphones &bull; Electronics &bull; Qty: 12 &bull; Location: Rack C &bull; Priority: 7

### Warehouse Graph (`backend/data/warehouse.json`)
* **Vertices (7):**
  * $0$: Receiving
  * $1$: Rack A
  * $2$: Rack B
  * $3$: Rack C
  * $4$: Rack D
  * $5$: Packing Zone
  * $6$: Dispatch Bay
* **Edges (11):**
  * Receiving $\leftrightarrow$ Rack A: 4
  * Receiving $\leftrightarrow$ Rack B: 6
  * Rack A $\leftrightarrow$ Rack B: 3
  * Rack A $\leftrightarrow$ Rack C: 7
  * Rack B $\leftrightarrow$ Rack C: 4
  * Rack B $\leftrightarrow$ Rack D: 8
  * Rack C $\leftrightarrow$ Rack D: 2
  * Rack C $\leftrightarrow$ Packing Zone: 5
  * Rack D $\leftrightarrow$ Packing Zone: 6
  * Rack D $\leftrightarrow$ Dispatch Bay: 9
  * Packing Zone $\leftrightarrow$ Dispatch Bay: 3

### Default Dispatch Knapsack Cargo
* Medical Kit &bull; Wt: 4 kg &bull; Priority: 10
* Packaged Food &bull; Wt: 3 kg &bull; Priority: 7
* Electronics &bull; Wt: 5 kg &bull; Priority: 12
* Stationery &bull; Wt: 2 kg &bull; Priority: 4
* Tools &bull; Wt: 6 kg &bull; Priority: 13
* **Cart Capacity:** $10$ kg &rarr; **Optimal Value:** $23$

---

## 10. Limitations & Future Scope

### Project Limitations (Academic Focus)
1. **In-Memory Volatility:** To remain focused on data structure mechanics, tree and heap structures reside in server memory (with initial JSON seeding).
2. **Deterministic Static Weights:** Edge weights represent fixed aisle distances rather than dynamic real-time traffic congestion.
3. **Discrete 0/1 Packing:** Assumes single indivisible units per item category rather than fractional item selection.

### Future Scope
1. **Multi-Cart Packing (Bin Packing):** Extending Knapsack to 3D Bin Packing for multi-shelf picker trolleys.
2. **A\* Search:** Incorporating spatial Manhattan/Euclidean heuristics into Dijkstra for large-scale logistics fulfillment centers.
3. **B+ Tree Secondary Indexing:** Combining the in-memory AVL index with disk-based B+ Trees for enterprise-scale multi-million SKU databases.

---

## 11. Viva Voce Quick Checklist

When presenting this project to an examiner:
1. **Open the Dashboard:** Explain the 9-module layout and how each module matches a syllabus DSA topic.
2. **Demonstrate AVL Tree:**
   * Insert a new SKU (e.g. `SKU006`). Point out the comparison count and rotation counters.
   * Search for `SKU003`. Show the exact search path and explain the $\mathcal{O}(\log n)$ time guarantee.
   * View the Inorder traversal to demonstrate automatic lexicographical ordering.
3. **Demonstrate Binary Max Heap:**
   * Show the root alert ($P=10$ or $P=9$).
   * Click **Extract Max Alert** and explain how the last element moves to index $0$ followed by `heapify_down` in $\mathcal{O}(\log n)$.
4. **Demonstrate Graph Dual Representations:**
   * Switch between Adjacency List ($\mathcal{O}(V+E)$) and Adjacency Matrix ($\mathcal{O}(V^2)$).
5. **Run Dijkstra vs Prim:**
   * Run Dijkstra from Receiving to Dispatch Bay: Shortest path is $18.0$ (via Receiving $\rightarrow$ Rack B $\rightarrow$ Rack C $\rightarrow$ Packing $\rightarrow$ Dispatch).
   * Run Prim MST: Total network cost is $21.0$ using $6$ edges ($V-1$).
   * Clearly state the difference: Dijkstra solves single-source shortest path; Prim minimizes total network construction cost.
6. **Show Floyd-Warshall:**
   * Explain how the Adjacency Matrix is transformed through intermediate vertices $k \in [0..V-1]$ in $\mathcal{O}(V^3)$ time to yield the all-pairs matrix.
7. **Show 0/1 Knapsack:**
   * Set capacity to $10$. Point out the 2D DP table $dp[i][w]$ and explain the backtracking step that selects optimal items to reach total value $23$.