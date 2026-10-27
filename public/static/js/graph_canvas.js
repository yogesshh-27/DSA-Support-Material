/**
 * Academic Warehouse Graph Canvas Visualizer — Modern Dark Cybernetic Edition.
 * Draws vertices, edges, weights, and highlights Dijkstra routes, Prim MST, or TSP tours.
 */

class GraphCanvasRenderer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext("2d");
    this.vertices = [];
    this.edges = [];
    this.highlightEdges = []; // array of [u, v]
    this.highlightNodes = []; // array of node ids
    this.highlightType = null; // 'dijkstra', 'prim', or 'tsp'
    this.setupResize();
  }

  setupResize() {
    const resize = () => {
      if (!this.canvas) return;
      const rect = this.canvas.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) return;
      this.canvas.width = rect.width * window.devicePixelRatio;
      this.canvas.height = rect.height * window.devicePixelRatio;
      this.ctx.setTransform(1, 0, 0, 1, 0, 0);
      this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
      this.render();
    };
    window.addEventListener("resize", resize);
    setTimeout(resize, 50);
  }

  setData(vertices, edges) {
    this.vertices = vertices || [];
    this.edges = edges || [];
    this.render();
  }

  setHighlight(nodeIds = [], edgePairs = [], type = "dijkstra") {
    this.highlightNodes = nodeIds;
    this.highlightEdges = edgePairs;
    this.highlightType = type;
    this.render();
  }

  clearHighlight() {
    this.highlightNodes = [];
    this.highlightEdges = [];
    this.highlightType = null;
    this.render();
  }

  isEdgeHighlighted(u, v) {
    return this.highlightEdges.some(
      (pair) => (pair[0] === u && pair[1] === v) || (pair[0] === v && pair[1] === u)
    );
  }

  render() {
    if (!this.ctx || !this.canvas) return;
    const rect = this.canvas.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;

    // Reset shadow state
    this.ctx.shadowBlur = 0;
    this.ctx.shadowColor = "transparent";

    // 1. Draw Background & Technical Dot Grid
    this.ctx.fillStyle = "#0a0f1d";
    this.ctx.fillRect(0, 0, width, height);

    this.ctx.fillStyle = "rgba(255, 255, 255, 0.04)";
    const gridSize = 24;
    for (let x = gridSize; x < width; x += gridSize) {
      for (let y = gridSize; y < height; y += gridSize) {
        this.ctx.beginPath();
        this.ctx.arc(x, y, 1, 0, 2 * Math.PI);
        this.ctx.fill();
      }
    }

    if (!this.vertices.length) {
      this.ctx.fillStyle = "#64748b";
      this.ctx.font = "600 13px 'Plus Jakarta Sans', sans-serif";
      this.ctx.textAlign = "center";
      this.ctx.fillText("Awaiting warehouse topological network data...", width / 2, height / 2);
      return;
    }

    // Coordinate mapping: find bounds
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    this.vertices.forEach(v => {
      minX = Math.min(minX, v.x);
      maxX = Math.max(maxX, v.x);
      minY = Math.min(minY, v.y);
      maxY = Math.max(maxY, v.y);
    });

    const padding = 65;
    const scaleX = (width - padding * 2) / (maxX - minX || 1);
    const scaleY = (height - padding * 2) / (maxY - minY || 1);

    const getPos = (v) => ({
      x: padding + (v.x - minX) * scaleX,
      y: padding + (v.y - minY) * scaleY,
    });

    const nodePosMap = {};
    this.vertices.forEach(v => {
      nodePosMap[v.id] = getPos(v);
    });

    // 2. Draw Default Inactive Edges
    this.edges.forEach(edge => {
      const p1 = nodePosMap[edge.u];
      const p2 = nodePosMap[edge.v];
      if (!p1 || !p2) return;

      const isHL = this.isEdgeHighlighted(edge.u, edge.v);
      if (isHL) return; // Drawn in highlighted pass

      this.ctx.beginPath();
      this.ctx.moveTo(p1.x, p1.y);
      this.ctx.lineTo(p2.x, p2.y);
      this.ctx.strokeStyle = "rgba(148, 163, 184, 0.2)";
      this.ctx.lineWidth = 1.8;
      this.ctx.stroke();

      this.drawWeightBadge(p1, p2, edge.weight, false);
    });

    // 3. Draw Highlighted Active Edges with Neon Glow
    this.edges.forEach(edge => {
      const isHL = this.isEdgeHighlighted(edge.u, edge.v);
      if (!isHL) return;

      const p1 = nodePosMap[edge.u];
      const p2 = nodePosMap[edge.v];
      if (!p1 || !p2) return;

      let strokeColor = "#10b981";
      if (this.highlightType === "prim") strokeColor = "#f59e0b";
      else if (this.highlightType === "tsp") strokeColor = "#a855f7";

      this.ctx.save();
      this.ctx.shadowColor = strokeColor;
      this.ctx.shadowBlur = 12;

      this.ctx.beginPath();
      this.ctx.moveTo(p1.x, p1.y);
      this.ctx.lineTo(p2.x, p2.y);
      this.ctx.strokeStyle = strokeColor;
      this.ctx.lineWidth = 3.5;
      this.ctx.stroke();
      this.ctx.restore();

      this.drawWeightBadge(p1, p2, edge.weight, true);
    });

    // 4. Draw Vertices (Racks / Zones / Depots)
    this.vertices.forEach(v => {
      const pos = nodePosMap[v.id];
      if (!pos) return;

      const isNodeHL = this.highlightNodes.includes(v.id);

      this.ctx.save();
      this.ctx.beginPath();
      this.ctx.arc(pos.x, pos.y, 18, 0, 2 * Math.PI);

      if (isNodeHL) {
        let fillColor = "#064e3b";
        let strokeColor = "#10b981";
        if (this.highlightType === "prim") {
          fillColor = "#451a03";
          strokeColor = "#f59e0b";
        } else if (this.highlightType === "tsp") {
          fillColor = "#3b0764";
          strokeColor = "#a855f7";
        } else if (this.highlightType !== "dijkstra") {
          fillColor = "#1e1b4b";
          strokeColor = "#6366f1";
        }

        this.ctx.shadowColor = strokeColor;
        this.ctx.shadowBlur = 14;
        this.ctx.fillStyle = fillColor;
        this.ctx.strokeStyle = strokeColor;
        this.ctx.lineWidth = 2.5;
      } else {
        this.ctx.fillStyle = "#111827";
        this.ctx.strokeStyle = "rgba(255, 255, 255, 0.25)";
        this.ctx.lineWidth = 1.8;
      }

      this.ctx.fill();
      this.ctx.stroke();
      this.ctx.restore();

      // Vertex Numerical ID
      this.ctx.fillStyle = "#ffffff";
      this.ctx.font = "bold 12px 'JetBrains Mono', monospace";
      this.ctx.textAlign = "center";
      this.ctx.textBaseline = "middle";
      this.ctx.fillText(v.id.toString(), pos.x, pos.y);

      // Vertex Human Name Label
      this.ctx.font = "600 11px 'Plus Jakarta Sans', sans-serif";
      this.ctx.fillStyle = isNodeHL ? "#ffffff" : "#94a3b8";
      const labelY = pos.y > height - 42 ? pos.y - 28 : pos.y + 28;
      this.ctx.fillText(v.name, pos.x, labelY);
    });
  }

  drawWeightBadge(p1, p2, weight, isHighlighted) {
    const midX = (p1.x + p2.x) / 2;
    const midY = (p1.y + p2.y) / 2;

    const text = weight.toString();
    this.ctx.font = "bold 10px 'JetBrains Mono', monospace";
    const textWidth = this.ctx.measureText(text).width;
    const boxW = Math.max(textWidth + 10, 20);
    const boxH = 15;
    const radius = 3;

    this.ctx.save();
    let bgColor = "rgba(15, 23, 42, 0.9)";
    let borderColor = "rgba(255, 255, 255, 0.15)";
    let textColor = "#cbd5e1";

    if (isHighlighted) {
      if (this.highlightType === "dijkstra") {
        bgColor = "#10b981";
      } else if (this.highlightType === "prim") {
        bgColor = "#f59e0b";
      } else if (this.highlightType === "tsp") {
        bgColor = "#a855f7";
      } else {
        bgColor = "#6366f1";
      }
      borderColor = "#ffffff";
      textColor = "#ffffff";
      this.ctx.shadowColor = bgColor;
      this.ctx.shadowBlur = 8;
    }

    this.ctx.fillStyle = bgColor;
    this.ctx.strokeStyle = borderColor;
    this.ctx.lineWidth = 1;

    // Rounded rectangle
    const x = midX - boxW / 2;
    const y = midY - boxH / 2;
    this.ctx.beginPath();
    this.ctx.moveTo(x + radius, y);
    this.ctx.lineTo(x + boxW - radius, y);
    this.ctx.quadraticCurveTo(x + boxW, y, x + boxW, y + radius);
    this.ctx.lineTo(x + boxW, y + boxH - radius);
    this.ctx.quadraticCurveTo(x + boxW, y + boxH, x + boxW - radius, y + boxH);
    this.ctx.lineTo(x + radius, y + boxH);
    this.ctx.quadraticCurveTo(x, y + boxH, x, y + boxH - radius);
    this.ctx.lineTo(x, y + radius);
    this.ctx.quadraticCurveTo(x, y, x + radius, y);
    this.ctx.closePath();
    this.ctx.fill();
    this.ctx.stroke();

    this.ctx.fillStyle = textColor;
    this.ctx.textAlign = "center";
    this.ctx.textBaseline = "middle";
    this.ctx.fillText(text, midX, midY);
    this.ctx.restore();
  }
}

window.GraphCanvasRenderer = GraphCanvasRenderer;
