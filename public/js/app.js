/**
 * Application Controller for Smart Warehouse Inventory Management Platform.
 * Coordinates all UI interactions, API calls, and canvas visual representations.
 */

const App = {
  graphRenderer: null,
  tspRenderer: null,
  cachedGraph: null,
  knapsackItems: [],

  // TSP State (Unit 4: Branch and Bound)
  tspLocations: [],
  tspSelectedSet: new Set([0, 1, 2, 3]),
  tspExecutionSteps: [],
  tspCurrentStepIdx: 0,
  tspIsPlaying: false,
  tspPlayTimer: null,
  tspLastResult: null,

  init() {
    this.initNavigation();
    this.graphRenderer = new GraphCanvasRenderer("warehouseCanvas");
    this.tspRenderer = new GraphCanvasRenderer("tspWarehouseCanvas");
    this.loadDashboardData();
    this.loadGraphData();
    this.loadInventoryData();
    this.loadAlertsData();
    this.initDefaultKnapsack();
    this.initTspLocations();
    this.loadBPlusData();
  },

  showFeedback(message, type = "success") {
    const box = document.getElementById("feedbackAlert");
    if (!box) return;
    box.textContent = message;
    box.className = `feedback-msg show ${type}`;
    setTimeout(() => {
      box.className = "feedback-msg";
    }, 4000);
  },

  // -------------------------------------------------------------
  // NAVIGATION
  // -------------------------------------------------------------
  initNavigation() {
    const links = document.querySelectorAll(".nav-link");
    links.forEach(link => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        const sectionId = link.getAttribute("data-section");
        this.navigateTo(sectionId);
      });
    });
  },

  navigateTo(sectionId) {
    document.querySelectorAll(".nav-link").forEach(link => {
      link.classList.toggle("active", link.getAttribute("data-section") === sectionId);
    });

    document.querySelectorAll(".section-panel").forEach(panel => {
      panel.classList.toggle("active", panel.id === `section-${sectionId}`);
    });

    if (sectionId === "graph" || sectionId === "dijkstra" || sectionId === "prim") {
      setTimeout(() => {
        if (this.graphRenderer) {
          this.graphRenderer.setupResize();
        }
      }, 50);
    }

    if (sectionId === "tsp") {
      setTimeout(() => {
        if (this.tspRenderer) {
          this.tspRenderer.setupResize();
          if (this.cachedGraph) {
            this.tspRenderer.setData(this.cachedGraph.vertices, this.cachedGraph.edges);
          }
        }
      }, 50);
    }

    if (sectionId === "dashboard") this.loadDashboardData();
    if (sectionId === "inventory") this.loadInventoryData();
    if (sectionId === "alerts") this.loadAlertsData();
    if (sectionId === "bplus") this.loadBPlusData();
  },

  // -------------------------------------------------------------
  // DASHBOARD
  // -------------------------------------------------------------
  async loadDashboardData() {
    try {
      const stats = await API.get("/dashboard/stats");
      document.getElementById("dashTotalSkus").textContent = stats.total_inventory_items;
      document.getElementById("dashTotalUnits").textContent = stats.total_stock_units;
      document.getElementById("dashLocations").textContent = stats.warehouse_locations_count;
      document.getElementById("dashRoutes").textContent = stats.warehouse_routes_count;
      document.getElementById("dashAlertsCount").textContent = stats.active_alerts_count;
      document.getElementById("dashKnapsackCapacity").textContent = `${stats.default_dispatch_capacity} kg`;

      if (document.getElementById("dashBPlusCount") && stats.total_bplus_products !== undefined) {
        document.getElementById("dashBPlusCount").textContent = stats.total_bplus_products;
      }
      if (document.getElementById("dashBPlusHeight") && stats.bplus_tree_height !== undefined) {
        document.getElementById("dashBPlusHeight").textContent = `Level ${stats.bplus_tree_height}`;
      }

      const topCard = document.getElementById("dashTopAlertContent");
      if (stats.highest_priority_alert) {
        const top = stats.highest_priority_alert;
        topCard.innerHTML = `
          <strong>SKU:</strong> ${top.sku} &bull; 
          <strong>Alert:</strong> ${top.alert_type} &bull; 
          <strong>Priority:</strong> <span class="badge badge-critical">${top.priority}/10</span> &bull; 
          <strong>Qty Remaining:</strong> ${top.quantity} &bull; 
          <strong>Location:</strong> ${top.location}
        `;
      } else {

        topCard.innerHTML = "No active warehouse alerts in the priority queue.";
      }
    } catch (err) {
      console.error("Dashboard stats failed:", err);
    }
  },

  // -------------------------------------------------------------
  // INVENTORY / AVL TREE
  // -------------------------------------------------------------
  async loadInventoryData() {
    try {
      const data = await API.get("/inventory");
      // Update rotation statistics
      document.getElementById("rotLeft").textContent = data.rotations.left_rotations;
      document.getElementById("rotRight").textContent = data.rotations.right_rotations;
      document.getElementById("rotLR").textContent = data.rotations.left_right_rotations;
      document.getElementById("rotRL").textContent = data.rotations.right_left_rotations;

      // Render table
      const tbody = document.getElementById("inventoryTableBody");
      tbody.innerHTML = "";

      if (!data.items || data.items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:#64748b;">Inventory is currently empty.</td></tr>`;
      } else {
        data.items.forEach(item => {
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td><strong>${item.sku}</strong></td>
            <td>${item.name}</td>
            <td>${item.category}</td>
            <td>${item.quantity}</td>
            <td>${item.location}</td>
            <td><span class="badge">${item.priority}/10</span></td>
            <td>
              <button class="btn btn-danger btn-sm" onclick="App.handleDeleteInventory('${item.sku}')">Delete</button>
            </td>
          `;
          tbody.appendChild(tr);
        });
      }

      // Update tree JSON view
      document.getElementById("treeJsonDisplay").textContent = JSON.stringify(data.tree_structure, null, 2);

      // Also load traversals
      this.loadInventoryTraversals();
    } catch (err) {
      this.showFeedback(err.message, "error");
    }
  },

  async loadInventoryTraversals() {
    try {
      const trav = await API.get("/inventory/traversals");
      const inBox = document.getElementById("inorderDisplay");
      const preBox = document.getElementById("preorderDisplay");

      inBox.innerHTML = trav.inorder.map((it, idx) => `
        <div class="log-item">
          <strong>${idx + 1}. [${it.sku}]</strong> ${it.name} | Qty: ${it.quantity} | Loc: ${it.location}
        </div>
      `).join("");

      preBox.innerHTML = trav.preorder.map((it, idx) => `
        <div class="log-item">
          <strong>${idx + 1}. [${it.sku}]</strong> ${it.name} | Qty: ${it.quantity} | Loc: ${it.location}
        </div>
      `).join("");
    } catch (err) {
      console.error("Failed to load traversals:", err);
    }
  },

  switchInventoryView(viewType) {
    document.querySelectorAll(".tab-nav .tab-btn").forEach((btn, idx) => {
      const types = ["table", "traversals", "tree"];
      btn.classList.toggle("active", types[idx] === viewType);
    });

    document.getElementById("invViewTable").style.display = viewType === "table" ? "block" : "none";
    document.getElementById("invViewTraversals").style.display = viewType === "traversals" ? "block" : "none";
    document.getElementById("invViewTree").style.display = viewType === "tree" ? "block" : "none";
  },

  async handleSearchSku(e) {
    e.preventDefault();
    const sku = document.getElementById("searchSkuInput").value.trim();
    if (!sku) return;

    const area = document.getElementById("searchResultArea");
    area.style.display = "block";
    area.innerHTML = "Searching AVL Tree...";

    try {
      const res = await API.get(`/inventory/search/${encodeURIComponent(sku)}`);
      const it = res.item;
      area.innerHTML = `
        <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 0.75rem; border-radius: 4px;">
          <div style="font-weight: 700; color: #166534; margin-bottom: 0.25rem;">
            Found SKU: ${it.sku} &ndash; ${it.name}
          </div>
          <div style="font-size: 0.8rem; color: #166534;">
            Category: ${it.category} | Quantity: ${it.quantity} | Location: ${it.location} | Priority: ${it.priority}
          </div>
          <div style="font-size: 0.75rem; color: #475569; margin-top: 0.35rem; font-family: var(--font-mono);">
            Comparisons: ${res.comparisons} | Path: ${res.search_path.join(" &rarr; ")} | Complexity: ${res.complexity}
          </div>
        </div>
      `;
    } catch (err) {
      area.innerHTML = `
        <div style="background-color: #fef2f2; border: 1px solid #fecaca; padding: 0.75rem; border-radius: 4px; color: #991b1b; font-size: 0.85rem;">
          ${err.message}
        </div>
      `;
    }
  },

  async handleAddInventory(e) {
    e.preventDefault();
    const payload = {
      sku: document.getElementById("addSku").value.trim().toUpperCase(),
      name: document.getElementById("addName").value.trim(),
      category: document.getElementById("addCategory").value.trim(),
      quantity: parseInt(document.getElementById("addQuantity").value, 10),
      location: document.getElementById("addLocation").value.trim(),
      priority: parseInt(document.getElementById("addPriority").value, 10),
    };

    try {
      const res = await API.post("/inventory", payload);
      this.showFeedback(`${res.message} (Comparisons: ${res.comparisons})`, "success");
      document.getElementById("formAddInventory").reset();
      this.loadInventoryData();
      this.loadDashboardData();
    } catch (err) {
      this.showFeedback(err.message, "error");
    }
  },

  async handleDeleteInventory(sku) {
    if (!confirm(`Are you sure you want to delete SKU '${sku}' from the AVL Tree?`)) return;

    try {
      const res = await API.delete(`/inventory/${encodeURIComponent(sku)}`);
      this.showFeedback(res.message, "success");
      this.loadInventoryData();
      this.loadDashboardData();
    } catch (err) {
      this.showFeedback(err.message, "error");
    }
  },

  // -------------------------------------------------------------
  // PRIORITY ALERTS (BINARY MAX HEAP)
  // -------------------------------------------------------------
  async loadAlertsData() {
    try {
      const data = await API.get("/alerts");
      document.getElementById("heapSizeCount").textContent = data.size;

      // Top Alert Card
      const topDetail = document.getElementById("topAlertDetail");
      if (data.top_alert) {
        const t = data.top_alert;
        topDetail.innerHTML = `
          <strong>SKU:</strong> ${t.sku} &bull; 
          <strong>Type:</strong> ${t.alert_type} &bull; 
          <strong>Priority:</strong> <span class="badge badge-critical">${t.priority}/10</span> &bull; 
          <strong>Quantity:</strong> ${t.quantity} &bull; 
          <strong>Location:</strong> ${t.location}
        `;
      } else {
        topDetail.innerHTML = "Alert heap is empty.";
      }

      // Heap Array Visual
      const visualBox = document.getElementById("heapArrayVisual");
      if (!data.alerts || data.alerts.length === 0) {
        visualBox.innerHTML = "<div class='log-item'>No elements in heap.</div>";
      } else {
        visualBox.innerHTML = data.alerts.map((al, idx) => {
          const parentIdx = Math.floor((idx - 1) / 2);
          const parentText = idx === 0 ? "Root" : `Parent: [${parentIdx}]`;
          return `
            <div class="log-item">
              <strong>Index [${idx}]:</strong> Priority ${al.priority} &ndash; ${al.alert_type} (${al.sku}) | ${parentText}
            </div>
          `;
        }).join("");
      }

      // Table
      const tbody = document.getElementById("alertsTableBody");
      tbody.innerHTML = "";
      if (!data.alerts || data.alerts.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:#64748b;">No alerts recorded.</td></tr>`;
      } else {
        data.alerts.forEach((al, idx) => {
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td><code>[${idx}]</code></td>
            <td><span class="badge ${al.priority >= 9 ? 'badge-critical' : al.priority >= 7 ? 'badge-warning' : ''}">${al.priority}/10</span></td>
            <td><strong>${al.alert_type}</strong></td>
            <td>${al.sku}</td>
            <td>${al.quantity}</td>
            <td>${al.location}</td>
          `;
          tbody.appendChild(tr);
        });
      }
    } catch (err) {
      this.showFeedback(err.message, "error");
    }
  },

  async handleAddAlert(e) {
    e.preventDefault();
    const payload = {
      sku: document.getElementById("alertSku").value.trim().toUpperCase(),
      alert_type: document.getElementById("alertType").value,
      priority: parseInt(document.getElementById("alertPriority").value, 10),
      quantity: parseInt(document.getElementById("alertQty").value, 10),
      location: document.getElementById("alertLoc").value.trim(),
    };

    try {
      const res = await API.post("/alerts", payload);
      this.showFeedback(res.message, "success");
      document.getElementById("formAddAlert").reset();
      this.loadAlertsData();
      this.loadDashboardData();
    } catch (err) {
      this.showFeedback(err.message, "error");
    }
  },

  async handleExtractAlert() {
    try {
      const res = await API.post("/alerts/extract");
      const al = res.extracted_alert;
      this.showFeedback(`Extracted Priority ${al.priority} Alert: ${al.sku} (${al.alert_type})`, "success");
      this.loadAlertsData();
      this.loadDashboardData();
    } catch (err) {
      this.showFeedback(err.message, "error");
    }
  },

  // -------------------------------------------------------------
  // WAREHOUSE GRAPH
  // -------------------------------------------------------------
  async loadGraphData() {
    try {
      const graph = await API.get("/graph");
      this.cachedGraph = graph;

      // Populate canvas
      if (this.graphRenderer) {
        this.graphRenderer.setData(graph.vertices, graph.edges);
      }
      if (this.tspRenderer) {
        this.tspRenderer.setData(graph.vertices, graph.edges);
      }


      // Populate select dropdowns for algorithms
      this.populateLocationSelects(graph.vertices);

      // Load representation views
      this.loadGraphRepresentations();
    } catch (err) {
      console.error("Failed to load graph:", err);
    }
  },

  populateLocationSelects(vertices) {
    const selects = [
      document.getElementById("edgeSourceSelect"),
      document.getElementById("edgeDestSelect"),
      document.getElementById("dijkstraSource"),
      document.getElementById("dijkstraDest"),
      document.getElementById("primStartNode"),
      document.getElementById("fwQuerySource"),
      document.getElementById("fwQueryDest"),
    ];

    selects.forEach(sel => {
      if (!sel) return;
      const currentVal = sel.value;
      sel.innerHTML = "";
      vertices.forEach(v => {
        const opt = document.createElement("option");
        opt.value = v.id;
        opt.textContent = `${v.id}: ${v.name}`;
        sel.appendChild(opt);
      });
      if (currentVal !== "") sel.value = currentVal;
    });

    // Sensible defaults
    if (document.getElementById("dijkstraSource")) document.getElementById("dijkstraSource").value = 0; // Receiving
    if (document.getElementById("dijkstraDest")) document.getElementById("dijkstraDest").value = 6; // Dispatch
    if (document.getElementById("fwQuerySource")) document.getElementById("fwQuerySource").value = 0;
    if (document.getElementById("fwQueryDest")) document.getElementById("fwQueryDest").value = 6;
  },

  async loadGraphRepresentations() {
    try {
      // Adjacency List
      const listData = await API.get("/graph/adjacency-list");
      const listDisplay = document.getElementById("adjListDisplay");
      listDisplay.innerHTML = "";
      for (const [nodeName, neighbors] of Object.entries(listData.data)) {
        const neighborStr = neighbors.length > 0
          ? neighbors.map(n => `[${n.neighbor_name} (Cost: ${n.weight})]`).join(" &rarr; ")
          : "None";
        listDisplay.innerHTML += `
          <div class="log-item">
            <strong>${nodeName}</strong>: ${neighborStr}
          </div>
        `;
      }

      // Adjacency Matrix
      const matrixData = await API.get("/graph/adjacency-matrix");
      const matrixTable = document.getElementById("adjMatrixTable");
      matrixTable.innerHTML = "";

      // Header row
      const thead = document.createElement("thead");
      const headRow = document.createElement("tr");
      headRow.innerHTML = "<th>Zone</th>" + matrixData.headers.map(h => `<th>${h}</th>`).join("");
      thead.appendChild(headRow);
      matrixTable.appendChild(thead);

      // Body rows
      const tbody = document.createElement("tbody");
      matrixData.display_matrix.forEach((row, i) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td><strong>${matrixData.headers[i]}</strong></td>` +
          row.map(cell => `<td>${cell}</td>`).join("");
        tbody.appendChild(tr);
      });
      matrixTable.appendChild(tbody);
    } catch (err) {
      console.error("Failed to load representations:", err);
    }
  },

  toggleGraphRepresentation(type) {
    const listCont = document.getElementById("graphRepListContainer");
    const matCont = document.getElementById("graphRepMatrixContainer");
    const btnList = document.getElementById("btnShowAdjList");
    const btnMat = document.getElementById("btnShowAdjMatrix");

    if (type === "list") {
      listCont.style.display = "block";
      matCont.style.display = "none";
      btnList.classList.add("btn-primary");
      btnMat.classList.remove("btn-primary");
    } else {
      listCont.style.display = "none";
      matCont.style.display = "block";
      btnMat.classList.add("btn-primary");
      btnList.classList.remove("btn-primary");
    }
  },

  async handleAddEdge(e) {
    e.preventDefault();
    const u = parseInt(document.getElementById("edgeSourceSelect").value, 10);
    const v = parseInt(document.getElementById("edgeDestSelect").value, 10);
    const weight = parseFloat(document.getElementById("edgeWeightInput").value);

    try {
      const res = await API.post("/graph/edge", { u, v, weight });
      this.showFeedback(res.message, "success");
      this.loadGraphData();
    } catch (err) {
      this.showFeedback(err.message, "error");
    }
  },

  async resetGraphToDefault() {
    try {
      await API.post("/graph/reset");
      if (this.graphRenderer) this.graphRenderer.clearHighlight();
      this.showFeedback("Warehouse layout reset to default standard graph.", "success");
      this.loadGraphData();
    } catch (err) {
      this.showFeedback(err.message, "error");
    }
  },

  // -------------------------------------------------------------
  // DIJKSTRA SHORT PATH
  // -------------------------------------------------------------
  async handleRunDijkstra(e) {
    e.preventDefault();
    const source_id = parseInt(document.getElementById("dijkstraSource").value, 10);
    const dest_id = parseInt(document.getElementById("dijkstraDest").value, 10);

    try {
      const res = await API.post("/dijkstra", { source_id, dest_id });
      const r = res.result;

      const area = document.getElementById("dijkstraResultsArea");
      area.style.display = "block";

      if (!r.reachable) {
        document.getElementById("dijkstraCostBadge").textContent = "Unreachable";
        document.getElementById("dijkstraPathDesc").textContent = r.path_description;
        document.getElementById("dijkstraVisitedSeq").textContent = r.visited_sequence.join(", ");
        if (this.graphRenderer) this.graphRenderer.clearHighlight();
        return;
      }

      document.getElementById("dijkstraCostBadge").textContent = `Total Cost: ${r.total_cost}`;
      document.getElementById("dijkstraPathDesc").textContent = r.path_description;
      document.getElementById("dijkstraVisitedSeq").textContent = r.visited_sequence.join(" &rarr; ");

      // Steps log
      const tbody = document.getElementById("dijkstraStepsBody");
      tbody.innerHTML = r.steps.map(s => `
        <tr>
          <td><strong>Step ${s.step}</strong></td>
          <td>${s.action}</td>
        </tr>
      `).join("");

      // Highlight in canvas
      if (this.graphRenderer && r.route_ids.length > 1) {
        const edgePairs = [];
        for (let i = 0; i < r.route_ids.length - 1; i++) {
          edgePairs.push([r.route_ids[i], r.route_ids[i + 1]]);
        }
        this.graphRenderer.setHighlight(r.route_ids, edgePairs, "dijkstra");
      }
    } catch (err) {
      this.showFeedback(err.message, "error");
    }
  },

  // -------------------------------------------------------------
  // PRIM MINIMUM SPANNING TREE (MST)
  // -------------------------------------------------------------
  async handleRunPrim() {
    const start_node_id = parseInt(document.getElementById("primStartNode").value, 10) || 0;

    try {
      const res = await API.post("/prim", { start_node_id });
      const r = res.result;

      const area = document.getElementById("primResultsArea");
      area.style.display = "block";

      document.getElementById("primTotalCostBadge").textContent = `Total MST Cost: ${r.total_cost}`;
      document.getElementById("primEdgeCount").textContent = r.edge_count;
      document.getElementById("primVertexCount").textContent = r.edge_count + 1;

      // Edges table
      const tbody = document.getElementById("primEdgesBody");
      tbody.innerHTML = r.mst_edges.map((e, idx) => `
        <tr>
          <td><strong>${idx + 1}.</strong> ${e.u_name} &mdash; ${e.v_name}</td>
          <td><strong>${e.weight}</strong></td>
        </tr>
      `).join("");

      // Steps log
      const stepsLog = document.getElementById("primStepsLog");
      stepsLog.innerHTML = r.steps.map(s => `
        <div class="log-item">
          <strong>Step ${s.step}:</strong> ${s.action} ${s.running_total !== undefined ? `(Running Sum: ${s.running_total})` : ""}
        </div>
      `).join("");

      // Highlight in canvas
      if (this.graphRenderer && r.mst_edges.length > 0) {
        const edgePairs = r.mst_edges.map(e => [e.u, e.v]);
        const nodeIds = [...new Set(r.mst_edges.flatMap(e => [e.u, e.v]))];
        this.graphRenderer.setHighlight(nodeIds, edgePairs, "prim");
      }
    } catch (err) {
      this.showFeedback(err.message, "error");
    }
  },

  // -------------------------------------------------------------
  // FLOYD-WARSHALL ALL-PAIRS
  // -------------------------------------------------------------
  async handleRunFloydWarshall() {
    try {
      const res = await API.post("/floyd-warshall");
      const r = res.result;

      // Render Initial Matrix
      const initTable = document.getElementById("fwInitialMatrixTable");
      initTable.innerHTML = "<thead><tr><th>From \\ To</th>" +
        r.headers.map(h => `<th>${h}</th>`).join("") + "</tr></thead>";

      const initTbody = document.createElement("tbody");
      r.initial_matrix.forEach((row, i) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td><strong>${r.headers[i]}</strong></td>` +
          row.map(val => `<td>${val}</td>`).join("");
        initTbody.appendChild(tr);
      });
      initTable.appendChild(initTbody);

      // Render Final Matrix
      const finalTable = document.getElementById("fwFinalMatrixTable");
      finalTable.innerHTML = "<thead><tr><th>From \\ To</th>" +
        r.headers.map(h => `<th>${h}</th>`).join("") + "</tr></thead>";

      const finalTbody = document.createElement("tbody");
      r.final_matrix.forEach((row, i) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td><strong>${r.headers[i]}</strong></td>` +
          row.map(val => `<td><strong>${val}</strong></td>`).join("");
        finalTbody.appendChild(tr);
      });
      finalTable.appendChild(finalTbody);

      this.showFeedback("Floyd-Warshall all-pairs shortest distances computed.", "success");
    } catch (err) {
      this.showFeedback(err.message, "error");
    }
  },

  async handleQueryFwPair() {
    const source_id = parseInt(document.getElementById("fwQuerySource").value, 10);
    const dest_id = parseInt(document.getElementById("fwQueryDest").value, 10);

    try {
      const res = await API.post("/floyd-warshall/query", { source_id, dest_id });
      const r = res.result;
      const resDiv = document.getElementById("fwQueryResult");
      resDiv.textContent = `Shortest Distance from ${r.source} to ${r.destination}: ${r.distance} | Route: ${r.path_description}`;
    } catch (err) {
      this.showFeedback(err.message, "error");
    }
  },

  // -------------------------------------------------------------
  // 0/1 KNAPSACK DISPATCH
  // -------------------------------------------------------------
  async initDefaultKnapsack() {
    try {
      const def = await API.get("/knapsack/default");
      this.knapsackItems = def.items || [
        { name: "Medical Kit", weight: 4, value: 10 },
        { name: "Packaged Food", weight: 3, value: 7 },
        { name: "Electronics", weight: 5, value: 12 },
        { name: "Stationery", weight: 2, value: 4 },
        { name: "Tools", weight: 6, value: 13 },
      ];
      document.getElementById("ksCapacityInput").value = def.capacity || 10;
      this.renderKnapsackItems();
    } catch (err) {
      console.error("Failed to load default knapsack:", err);
    }
  },

  renderKnapsackItems() {
    const tbody = document.getElementById("knapsackItemsBody");
    tbody.innerHTML = "";
    this.knapsackItems.forEach((it, idx) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${it.name}</td>
        <td>${it.weight} kg</td>
        <td><span class="badge">${it.value}</span></td>
        <td>
          <button class="btn btn-danger btn-sm" onclick="App.handleDeleteKnapsackItem(${idx})">Remove</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  },

  resetKnapsackItems() {
    this.initDefaultKnapsack();
    this.showFeedback("Knapsack item pool reset to standard defaults.", "success");
  },

  handleAddKnapsackItem(e) {
    e.preventDefault();
    const name = document.getElementById("ksItemName").value.trim();
    const weight = parseInt(document.getElementById("ksItemWeight").value, 10);
    const value = parseInt(document.getElementById("ksItemValue").value, 10);

    if (!name || weight <= 0 || value < 0) return;

    this.knapsackItems.push({ name, weight, value });
    this.renderKnapsackItems();
    document.getElementById("formAddKnapsackItem").reset();
  },

  handleDeleteKnapsackItem(idx) {
    this.knapsackItems.splice(idx, 1);
    this.renderKnapsackItems();
  },

  async handleRunKnapsack() {
    const capacity = parseInt(document.getElementById("ksCapacityInput").value, 10);
    if (isNaN(capacity) || capacity < 0) {
      this.showFeedback("Please provide a valid non-negative capacity.", "error");
      return;
    }

    try {
      const res = await API.post("/knapsack", {
        items: this.knapsackItems,
        capacity: capacity,
      });
      const r = res.result;

      // Summary Card
      document.getElementById("knapsackSummaryCard").style.display = "block";
      document.getElementById("ksMaxValue").textContent = r.max_value;
      document.getElementById("ksTotalWeight").textContent = r.total_weight;
      document.getElementById("ksCapacityDisplay").textContent = r.capacity;

      const selList = document.getElementById("ksSelectedList");
      selList.innerHTML = r.selected_items.map(it => `
        <li><strong>${it.name}</strong> &ndash; Weight: ${it.weight} kg, Priority Value: ${it.value}</li>
      `).join("");

      // Render 2D DP Table
      document.getElementById("knapsackDpTableCard").style.display = "block";
      const dpTable = document.getElementById("knapsackDpTable");
      dpTable.innerHTML = "";

      // Header row (capacities 0..W)
      const thead = document.createElement("thead");
      const headRow = document.createElement("tr");
      headRow.innerHTML = "<th>Item \\ W</th>" +
        r.capacities_header.map(c => `<th>${c}</th>`).join("");
      thead.appendChild(headRow);
      dpTable.appendChild(thead);

      // Body rows
      const tbody = document.createElement("tbody");
      r.dp_table.forEach((row, i) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td><strong>${r.item_labels[i] || `Item ${i}`}</strong></td>` +
          row.map(val => `<td>${val}</td>`).join("");
        tbody.appendChild(tr);
      });
      dpTable.appendChild(tbody);

      // Decision Steps
      document.getElementById("knapsackStepsCard").style.display = "block";
      const stepsDiv = document.getElementById("knapsackDecisionSteps");
      stepsDiv.innerHTML = r.decision_steps.map(step => `
        <div class="log-item">${step}</div>
      `).join("");

      this.showFeedback(`0/1 Knapsack solved: Max cargo priority is ${r.max_value}`, "success");
    } catch (err) {
      this.showFeedback(err.message, "error");
    }
  },

  // -------------------------------------------------------------
  // MODULE A: WAREHOUSE ROUTE OPTIMIZER (TSP BRANCH AND BOUND)
  // -------------------------------------------------------------
  async initTspLocations() {
    try {
      const res = await API.get("/tsp/locations");
      this.tspLocations = res.locations || [];

      // Populate Start Location Dropdown
      const sel = document.getElementById("tspStartLocation");
      if (sel) {
        sel.innerHTML = this.tspLocations.map(loc => `
          <option value="${loc.id}">${loc.id}: ${loc.name}</option>
        `).join("");
      }

      this.renderTspLocationGrid();
    } catch (err) {
      console.error("Failed to load TSP locations:", err);
    }
  },

  renderTspLocationGrid() {
    const grid = document.getElementById("tspLocationCheckboxGrid");
    if (!grid) return;

    grid.innerHTML = this.tspLocations.map(loc => {
      const isChecked = this.tspSelectedSet.has(loc.id);
      return `
        <label class="location-pill ${isChecked ? "checked" : ""}" onclick="App.toggleTspLocation(${loc.id})">
          <input type="checkbox" ${isChecked ? "checked" : ""} onclick="event.stopPropagation(); App.toggleTspLocation(${loc.id});">
          <span><strong>${loc.id}:</strong> ${loc.name}</span>
        </label>
      `;
    }).join("");
  },

  handleTspStartChange() {
    const startId = parseInt(document.getElementById("tspStartLocation").value, 10);
    this.tspSelectedSet.add(startId);
    this.renderTspLocationGrid();
  },

  toggleTspLocation(id) {
    if (this.tspSelectedSet.has(id)) {
      // Don't deselect if it's the start location
      const startId = parseInt(document.getElementById("tspStartLocation").value, 10);
      if (id === startId && this.tspSelectedSet.size > 1) {
        this.showFeedback("Start location must remain selected in the tour.", "error");
        return;
      }
      this.tspSelectedSet.delete(id);
    } else {
      this.tspSelectedSet.add(id);
    }
    this.renderTspLocationGrid();
  },

  selectAllTspLocations() {
    this.tspLocations.forEach(loc => this.tspSelectedSet.add(loc.id));
    this.renderTspLocationGrid();
  },

  selectSampleTspCycle() {
    // 0: Receiving, 1: Rack A, 2: Rack B, 3: Rack C forms a direct cycle in warehouse graph!
    this.tspSelectedSet = new Set([0, 1, 2, 3]);
    const sel = document.getElementById("tspStartLocation");
    if (sel) sel.value = "0";
    this.renderTspLocationGrid();
  },

  clearTspLocations() {
    const startId = parseInt(document.getElementById("tspStartLocation").value, 10);
    this.tspSelectedSet = new Set([startId]);
    this.renderTspLocationGrid();
  },

  async handleRunTsp() {
    const startId = parseInt(document.getElementById("tspStartLocation").value, 10);
    this.tspSelectedSet.add(startId);
    const selectedIds = Array.from(this.tspSelectedSet);

    if (selectedIds.length < 2) {
      this.showFeedback("Please select at least 2 warehouse zones for a valid tour.", "error");
      return;
    }

    try {
      this.showFeedback("Computing Branch & Bound optimal tour...", "info");
      const res = await API.post("/tsp/solve", {
        start_location_id: startId,
        selected_location_ids: selectedIds,
      });

      this.tspLastResult = res;

      // Handle impossible tour
      const impossibleAlert = document.getElementById("tspTourImpossibleAlert");
      const successContent = document.getElementById("tspTourSuccessContent");
      const resultsCard = document.getElementById("tspResultsCard");
      const stepperCard = document.getElementById("tspStepperCard");

      resultsCard.style.display = "block";

      if (!res.tour_possible) {
        impossibleAlert.style.display = "block";
        impossibleAlert.innerHTML = `<strong>Tour Impossible:</strong> ${res.message}`;
        successContent.style.display = "none";
        stepperCard.style.display = "none";
        if (this.tspRenderer) {
          this.tspRenderer.clearHighlight();
        }
        return;
      }

      impossibleAlert.style.display = "none";
      successContent.style.display = "block";

      // Populate Results
      document.getElementById("tspTotalCost").textContent = `${res.total_cost}`;
      document.getElementById("tspNodesExplored").textContent = res.nodes_explored;
      document.getElementById("tspBranchesPruned").textContent = res.branches_pruned;
      document.getElementById("tspPruningEfficiency").textContent = `${res.pruning_efficiency_percent}%`;

      // Render Route Chain
      const chainDiv = document.getElementById("tspRouteChain");
      chainDiv.innerHTML = res.optimal_route_names.map((name, idx) => `
        <span class="route-node-pill">${name}</span>
        ${idx < res.optimal_route_names.length - 1 ? '<span class="route-arrow">&rarr;</span>' : ""}
      `).join("");

      // Render Nearest-Neighbor Heuristic Comparison
      const heurDiv = document.getElementById("tspHeuristicComparisonContent");
      if (res.nearest_neighbor && res.nearest_neighbor.possible) {
        const nn = res.nearest_neighbor;
        const diff = nn.total_cost - res.total_cost;
        heurDiv.innerHTML = `
          <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
            <div><strong>Branch &amp; Bound Cost:</strong> <span class="badge badge-success">${res.total_cost} (Optimal)</span></div>
            <div><strong>Nearest-Neighbor Cost:</strong> <span class="badge ${diff > 0 ? "badge-critical" : "badge-normal"}">${nn.total_cost} (Greedy Heuristic)</span></div>
            <div><strong>Suboptimality Gap:</strong> ${diff > 0 ? `+${diff.toFixed(2)} extra distance` : "Matched (Greedy was lucky)"}</div>
          </div>
          <div style="margin-top: 0.4rem; font-size: 0.8rem; color: #475569;">
            Heuristic Sequence: ${nn.route_names.join(" &rarr; ")}
          </div>
        `;
      } else {
        heurDiv.innerHTML = `
          <div style="color: #991b1b;">
            Nearest-Neighbor greedy heuristic failed to find a complete tour (trapped at a dead end), whereas Branch &amp; Bound successfully discovered the global optimum.
          </div>
        `;
      }

      // Highlight canvas with optimal tour
      if (this.tspRenderer) {
        const edgePairs = [];
        for (let i = 0; i < res.optimal_route_ids.length - 1; i++) {
          edgePairs.push([res.optimal_route_ids[i], res.optimal_route_ids[i + 1]]);
        }
        this.tspRenderer.setHighlight(res.optimal_route_ids, edgePairs, "tsp");
      }

      // Setup State Space Tree Stepper Playback
      if (res.execution_steps && res.execution_steps.length > 0) {
        this.tspExecutionSteps = res.execution_steps;
        this.tspCurrentStepIdx = 0;
        stepperCard.style.display = "block";
        this.renderTspStep(0);
      }

      this.showFeedback(`Optimal TSP Tour found! Total cost: ${res.total_cost}`, "success");
    } catch (err) {
      this.showFeedback(err.message, "error");
    }
  },

  renderTspStep(idx) {
    if (!this.tspExecutionSteps || this.tspExecutionSteps.length === 0) return;
    if (idx < 0) idx = 0;
    if (idx >= this.tspExecutionSteps.length) idx = this.tspExecutionSteps.length - 1;
    this.tspCurrentStepIdx = idx;

    const step = this.tspExecutionSteps[idx];

    // Counter
    document.getElementById("tspStepCounter").textContent = `Step ${idx + 1} of ${this.tspExecutionSteps.length}`;

    // Badge
    const badge = document.getElementById("tspStateBadge");
    const act = (step.action || "EXPLORE").toLowerCase();
    badge.className = `state-badge ${act}`;
    badge.textContent = step.action || "EXPLORE";

    // Step state values
    document.getElementById("tspStepCurrentNode").textContent = `Node ${step.node_id}: ${step.partial_names ? step.partial_names.join(" -> ") : step.current_name}`;
    document.getElementById("tspStepAccumCost").textContent = `${step.accumulated_cost}`;
    document.getElementById("tspStepLowerBound").textContent = `${step.lower_bound}`;
    document.getElementById("tspStepBestCost").textContent = `${step.best_cost_so_far}`;

    // Explanation
    document.getElementById("tspStepReason").innerHTML = `
      <strong>${step.action}:</strong> ${step.reason}
    `;

    // Highlight active partial branch on canvas
    if (this.tspRenderer && step.partial_route && step.partial_route.length > 0) {
      const edgePairs = [];
      for (let i = 0; i < step.partial_route.length - 1; i++) {
        edgePairs.push([step.partial_route[i], step.partial_route[i + 1]]);
      }
      this.tspRenderer.setHighlight(step.partial_route, edgePairs, "tsp");
    }
  },

  tspNextStep() {
    if (this.tspCurrentStepIdx < this.tspExecutionSteps.length - 1) {
      this.renderTspStep(this.tspCurrentStepIdx + 1);
    } else {
      this.tspPause();
    }
  },

  tspPrevStep() {
    if (this.tspCurrentStepIdx > 0) {
      this.renderTspStep(this.tspCurrentStepIdx - 1);
    }
  },

  tspTogglePlay() {
    if (this.tspIsPlaying) {
      this.tspPause();
    } else {
      this.tspPlay();
    }
  },

  tspPlay() {
    this.tspIsPlaying = true;
    const btn = document.getElementById("btnTspPlayPause");
    if (btn) btn.innerHTML = "&#10074;&#10074; Pause";

    const speed = parseInt(document.getElementById("tspPlaySpeed").value, 10) || 700;

    this.tspPlayTimer = setInterval(() => {
      if (this.tspCurrentStepIdx < this.tspExecutionSteps.length - 1) {
        this.renderTspStep(this.tspCurrentStepIdx + 1);
      } else {
        this.tspPause();
      }
    }, speed);
  },

  tspPause() {
    this.tspIsPlaying = false;
    if (this.tspPlayTimer) {
      clearInterval(this.tspPlayTimer);
      this.tspPlayTimer = null;
    }
    const btn = document.getElementById("btnTspPlayPause");
    if (btn) btn.innerHTML = "&#9654; Play";
  },

  tspResetPlayback() {
    this.tspPause();
    this.renderTspStep(0);
  },

  resetTsp() {
    this.tspPause();
    this.selectSampleTspCycle();
    document.getElementById("tspResultsCard").style.display = "none";
    document.getElementById("tspStepperCard").style.display = "none";
    if (this.tspRenderer) {
      this.tspRenderer.clearHighlight();
    }
    this.showFeedback("Route Optimizer reset to default sample warehouse cycle.", "info");
  },

  // -------------------------------------------------------------
  // MODULE B: ADVANCED INVENTORY SEARCH (B+ TREE)
  // -------------------------------------------------------------
  async loadBPlusData() {
    try {
      const data = await API.get("/bplus/products");

      // Update statistics
      if (data.tree_stats) {
        document.getElementById("bplusTotalProducts").textContent = data.tree_stats.total_products;
        document.getElementById("bplusTreeHeight").textContent = data.tree_stats.tree_height;
        document.getElementById("bplusLeafCount").textContent = data.tree_stats.leaf_nodes_count;
        document.getElementById("bplusInternalCount").textContent = data.tree_stats.internal_nodes_count;
        document.getElementById("bplusTreeOrder").textContent = data.tree_stats.order;
      }

      // Populate table of all products
      const tbody = document.getElementById("bplusProductsTableBody");
      if (tbody) {
        tbody.innerHTML = "";
        if (!data.products || data.products.length === 0) {
          tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: #64748b;">No products in B+ Tree index.</td></tr>`;
        } else {
          data.products.forEach(p => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
              <td><span class="badge" style="background-color: #0f172a; color: #ffffff;">${p.product_id}</span></td>
              <td><strong>${p.name}</strong></td>
              <td>${p.category}</td>
              <td>${p.quantity}</td>
              <td>${p.location}</td>
              <td><span class="badge badge-normal">${p.priority}/10</span></td>
              <td>${p.unit_weight} kg</td>
            `;
            tbody.appendChild(tr);
          });
        }
      }

      // Render Tree Diagram
      if (data.tree_hierarchy) {
        this.renderBPlusTree(data.tree_hierarchy);
        this.renderBPlusLeafChain(data.tree_hierarchy);
      }
    } catch (err) {
      console.error("Failed to load B+ Tree data:", err);
    }
  },

  async handleAddBPlusProduct(e) {
    e.preventDefault();
    const payload = {
      product_id: document.getElementById("bpId").value.trim().toUpperCase(),
      name: document.getElementById("bpName").value.trim(),
      category: document.getElementById("bpCategory").value.trim(),
      quantity: parseInt(document.getElementById("bpQuantity").value, 10),
      location: document.getElementById("bpLocation").value.trim(),
      priority: parseInt(document.getElementById("bpPriority").value, 10),
      unit_weight: parseFloat(document.getElementById("bpWeight").value),
    };

    try {
      const res = await API.post("/bplus/product", payload);

      // Handle split event display
      const splitBox = document.getElementById("bplusSplitAlert");
      if (res.split_events && res.split_events.length > 0) {
        splitBox.style.display = "block";
        const eventsDesc = res.split_events.map(ev => `
          <div>&bull; <strong>${ev.type}:</strong> ${ev.description}</div>
        `).join("");
        document.getElementById("bplusSplitTitle").textContent = "B+ Tree Rebalancing Split Occurred!";
        document.getElementById("bplusSplitDesc").innerHTML = eventsDesc;
      } else {
        splitBox.style.display = "none";
      }

      this.showFeedback(res.message, "success");
      document.getElementById("bplusInsertForm").reset();
      this.loadBPlusData();
      this.loadDashboardData();
    } catch (err) {
      this.showFeedback(err.message, "error");
    }
  },

  async handleSearchBPlus() {
    const input = document.getElementById("bplusSearchId");
    const pid = input.value.trim().toUpperCase();
    if (!pid) {
      this.showFeedback("Please enter a Product ID to search.", "error");
      return;
    }

    const resCard = document.getElementById("bplusSearchResultCard");
    const initHint = document.getElementById("bplusSearchInitialHint");

    try {
      const res = await API.get(`/bplus/search/${encodeURIComponent(pid)}`);
      initHint.style.display = "none";
      resCard.style.display = "block";

      document.getElementById("bplusComparisons").textContent = res.comparisons;
      document.getElementById("bplusSearchStatusBadge").className = "badge badge-success";
      document.getElementById("bplusSearchStatusBadge").textContent = "Found in Leaf";

      const p = res.product;
      document.getElementById("bplusSearchProductDetails").innerHTML = `
        <strong>${p.product_id} &ndash; ${p.name}</strong><br>
        Category: ${p.category} | Quantity: ${p.quantity} | Location: ${p.location} | Priority: ${p.priority}/10 | Weight: ${p.unit_weight} kg
      `;

      // Render search path steps through internal nodes
      const pathBox = document.getElementById("bplusSearchPathContainer");
      pathBox.innerHTML = res.search_path.map(step => `
        <div class="search-step-card">
          <strong>${step.type} (Node ${step.node_id}):</strong> Keys [${step.keys.join(", ")}]<br>
          <span style="color: #475569; font-size: 0.8rem;">&rarr; ${step.decision}</span>
        </div>
      `).join("");

      // Visually highlight searched nodes on tree diagram
      document.querySelectorAll(".bplus-node").forEach(nodeEl => {
        nodeEl.classList.remove("highlight-search");
      });
      res.search_path.forEach(step => {
        const el = document.getElementById(`bpNode-${step.node_id}`);
        if (el) el.classList.add("highlight-search");
      });

      this.showFeedback(`Product ${pid} found in B+ Tree leaf! (${res.comparisons} comparisons)`, "success");
    } catch (err) {
      initHint.style.display = "none";
      resCard.style.display = "block";
      document.getElementById("bplusSearchStatusBadge").className = "badge badge-critical";
      document.getElementById("bplusSearchStatusBadge").textContent = "Not Found";
      document.getElementById("bplusSearchProductDetails").innerHTML = `<span style="color: #dc2626;">${err.message}</span>`;
      document.getElementById("bplusSearchPathContainer").innerHTML = "";
      this.showFeedback(err.message, "error");
    }
  },

  async handleRangeBPlus() {
    const minId = document.getElementById("bplusRangeMin").value.trim().toUpperCase();
    const maxId = document.getElementById("bplusRangeMax").value.trim().toUpperCase();

    if (!minId || !maxId) {
      this.showFeedback("Please provide both Min and Max Product IDs.", "error");
      return;
    }

    try {
      const res = await API.post("/bplus/range", {
        min_product_id: minId,
        max_product_id: maxId,
      });

      const container = document.getElementById("bplusRangeResultsContainer");
      container.style.display = "block";

      document.getElementById("bplusRangeCount").textContent = res.count;
      document.getElementById("bplusRangeLeavesCount").textContent = res.leaves_traversed_count;
      document.getElementById("bplusRangeLeavesChain").textContent = `Linked Leaves Scanned: Node ${res.leaves_traversed_ids.join(" &rarr; Node ")}`;

      const tbody = document.getElementById("bplusRangeTableBody");
      tbody.innerHTML = "";

      if (!res.records || res.records.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: #64748b;">No products found in range '${minId}' to '${maxId}'.</td></tr>`;
      } else {
        res.records.forEach(p => {
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td><span class="badge" style="background-color: #0f172a; color: #ffffff;">${p.product_id}</span></td>
            <td><strong>${p.name}</strong></td>
            <td>${p.category}</td>
            <td>${p.quantity}</td>
            <td>${p.location}</td>
            <td><span class="badge badge-normal">${p.priority}/10</span></td>
            <td>${p.unit_weight} kg</td>
          `;
          tbody.appendChild(tr);
        });
      }

      this.showFeedback(`Range query complete: ${res.count} products matched across ${res.leaves_traversed_count} linked leaves.`, "success");
    } catch (err) {
      this.showFeedback(err.message, "error");
    }
  },

  async resetBPlusTree() {
    try {
      await API.post("/bplus/reset");
      document.getElementById("bplusSplitAlert").style.display = "none";
      document.getElementById("bplusSearchResultCard").style.display = "none";
      document.getElementById("bplusSearchInitialHint").style.display = "block";
      document.getElementById("bplusRangeResultsContainer").style.display = "none";
      this.loadBPlusData();
      this.loadDashboardData();
      this.showFeedback("B+ Tree index reset to default sample warehouse inventory.", "success");
    } catch (err) {
      this.showFeedback(err.message, "error");
    }
  },

  renderBPlusTree(hierarchy) {
    const container = document.getElementById("bplusTreeContainer");
    if (!container || !hierarchy || !hierarchy.levels) return;

    container.innerHTML = "";

    hierarchy.levels.forEach((levelNodes, lvlIdx) => {
      const levelDiv = document.createElement("div");
      levelDiv.className = "bplus-level";

      const isRoot = lvlIdx === 0;
      const isLeafLevel = lvlIdx === hierarchy.height - 1;

      const labelDiv = document.createElement("div");
      labelDiv.className = "bplus-level-label";
      labelDiv.textContent = isRoot
        ? (isLeafLevel ? "Level 0: Root (Leaf)" : "Level 0: Root")
        : (isLeafLevel ? `Level ${lvlIdx}: Leaves (Data)` : `Level ${lvlIdx}: Internal (Separators)`);
      levelDiv.appendChild(labelDiv);

      levelNodes.forEach(node => {
        const nodeCard = document.createElement("div");
        nodeCard.id = `bpNode-${node.node_id}`;
        nodeCard.className = `bplus-node ${node.is_leaf ? "leaf-node" : "internal-node"}`;

        // Header
        const header = document.createElement("div");
        header.className = "bplus-node-header";
        header.innerHTML = `
          <span>Node #${node.node_id}</span>
          <span style="color: ${node.is_leaf ? "#059669" : "#2563eb"};">${node.is_leaf ? "LEAF" : "INTERNAL"}</span>
        `;
        nodeCard.appendChild(header);

        // Keys
        const keysDiv = document.createElement("div");
        keysDiv.className = "bplus-node-keys";
        if (node.keys && node.keys.length > 0) {
          node.keys.forEach(k => {
            const span = document.createElement("span");
            span.className = "bplus-key-badge";
            span.textContent = k;
            keysDiv.appendChild(span);
          });
        } else {
          keysDiv.innerHTML = `<span style="color: #94a3b8; font-size: 0.75rem;">(Empty)</span>`;
        }
        nodeCard.appendChild(keysDiv);

        // If Leaf: Show record summary & next link indicator
        if (node.is_leaf) {
          const recCount = (node.records || []).length;
          const info = document.createElement("div");
          info.style.fontSize = "0.7rem";
          info.style.color = "#475569";
          info.style.marginTop = "0.3rem";
          info.style.textAlign = "center";
          info.textContent = `${recCount} record${recCount === 1 ? "" : "s"}`;
          nodeCard.appendChild(info);

          if (node.next_id) {
            const linkInd = document.createElement("div");
            linkInd.className = "leaf-link-indicator";
            linkInd.innerHTML = `&rarr; next: Node #${node.next_id}`;
            nodeCard.appendChild(linkInd);
          } else {
            const linkInd = document.createElement("div");
            linkInd.className = "leaf-link-indicator";
            linkInd.style.color = "#94a3b8";
            linkInd.textContent = "&bull; tail leaf (null)";
            nodeCard.appendChild(linkInd);
          }
        } else {
          // Internal: show child references
          const childInfo = document.createElement("div");
          childInfo.style.fontSize = "0.7rem";
          childInfo.style.color = "#2563eb";
          childInfo.style.marginTop = "0.3rem";
          childInfo.style.textAlign = "center";
          childInfo.textContent = `${(node.children_ids || []).length} children`;
          nodeCard.appendChild(childInfo);
        }

        levelDiv.appendChild(nodeCard);
      });

      container.appendChild(levelDiv);
    });
  },

  renderBPlusLeafChain(hierarchy) {
    const chainBar = document.getElementById("bplusLeafChainBar");
    if (!chainBar || !hierarchy || !hierarchy.leaf_chain_ids) return;

    chainBar.innerHTML = hierarchy.leaf_chain_ids.map((id, idx) => `
      <div style="background-color: #f0fdf4; border: 1px solid #10b981; border-radius: 4px; padding: 0.35rem 0.6rem; font-size: 0.75rem; font-family: var(--font-mono); color: #065f46; white-space: nowrap;">
        <strong>Leaf Node #${id}</strong>
      </div>
      ${idx < hierarchy.leaf_chain_ids.length - 1 ? '<span style="color: #10b981; font-weight: bold;">&rarr; next &rarr;</span>' : '<span style="color: #94a3b8; font-weight: bold;">&rarr; NULL</span>'}
    `).join("");
  },
};


window.App = App;

document.addEventListener("DOMContentLoaded", () => {
  App.init();
});
