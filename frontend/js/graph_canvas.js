/**
 * Academic Warehouse Graph Canvas Visualizer.
 * Draws vertices, edges, weights, and highlights Dijkstra routes or Prim MST edges.
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
    this.highlightType = null; // 'dijkstra' or 'prim'
    this.setupResize();
  }

  setupResize() {
    const resize = () => {
      const rect = this.canvas.getBoundingClientRect();
      this.canvas.width = rect.width * window.devicePixelRatio;
      this.canvas.height = rect.height * window.devicePixelRatio;
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
    if (!this.ctx) return;
    const rect = this.canvas.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;

    this.ctx.clearRect(0, 0, width, height);

    if (!this.vertices.length) {
      this.ctx.fillStyle = "#64748b";
      this.ctx.font = "14px -apple-system, sans-serif";
      this.ctx.textAlign = "center";
      this.ctx.fillText("Loading warehouse graph network...", width / 2, height / 2);
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

    const padding = 60;
    const scaleX = (width - padding * 2) / (maxX - minX || 1);
    const scaleY = (height - padding * 2) / (maxY - minY || 1);

    const getPos = (v) => {
      return {
        x: padding + (v.x - minX) * scaleX,
        y: padding + (v.y - minY) * scaleY,
      };
    };

    const nodePosMap = {};
    this.vertices.forEach(v => {
      nodePosMap[v.id] = getPos(v);
    });

    // 1. Draw Default Edges
    this.edges.forEach(edge => {
      const p1 = nodePosMap[edge.u];
      const p2 = nodePosMap[edge.v];
      if (!p1 || !p2) return;

      const isHL = this.isEdgeHighlighted(edge.u, edge.v);
      if (isHL) return; // Draw highlighted edges in second pass

      this.ctx.beginPath();
      this.ctx.moveTo(p1.x, p1.y);
      this.ctx.lineTo(p2.x, p2.y);
      this.ctx.strokeStyle = "#cbd5e1";
      this.ctx.lineWidth = 2;
      this.ctx.stroke();

      // Draw weight badge
      this.drawWeightBadge(p1, p2, edge.weight, false);
    });

    // 2. Draw Highlighted Edges
    this.edges.forEach(edge => {
      const isHL = this.isEdgeHighlighted(edge.u, edge.v);
      if (!isHL) return;

      const p1 = nodePosMap[edge.u];
      const p2 = nodePosMap[edge.v];
      if (!p1 || !p2) return;

      this.ctx.beginPath();
      this.ctx.moveTo(p1.x, p1.y);
      this.ctx.lineTo(p2.x, p2.y);
      this.ctx.strokeStyle = this.highlightType === "dijkstra" ? "#16a34a" : "#d97706";
      this.ctx.lineWidth = 4;
      this.ctx.stroke();

      this.drawWeightBadge(p1, p2, edge.weight, true);
    });

    // 3. Draw Vertices
    this.vertices.forEach(v => {
      const pos = nodePosMap[v.id];
      if (!pos) return;

      const isNodeHL = this.highlightNodes.includes(v.id);

      this.ctx.beginPath();
      this.ctx.arc(pos.x, pos.y, 18, 0, 2 * Math.PI);

      if (isNodeHL) {
        this.ctx.fillStyle = this.highlightType === "dijkstra" ? "#dcfce7" : "#fef3c7";
        this.ctx.strokeStyle = this.highlightType === "dijkstra" ? "#16a34a" : "#d97706";
        this.ctx.lineWidth = 3;
      } else {
        this.ctx.fillStyle = "#ffffff";
        this.ctx.strokeStyle = "#0f172a";
        this.ctx.lineWidth = 2;
      }
      this.ctx.fill();
      this.ctx.stroke();

      // Vertex ID text
      this.ctx.fillStyle = "#0f172a";
      this.ctx.font = "bold 12px monospace";
      this.ctx.textAlign = "center";
      this.ctx.textBaseline = "middle";
      this.ctx.fillText(v.id.toString(), pos.x, pos.y);

      // Vertex Name Label below or above
      this.ctx.font = "600 11px -apple-system, sans-serif";
      this.ctx.fillStyle = isNodeHL ? "#0f172a" : "#334155";
      const labelY = pos.y > height - 40 ? pos.y - 28 : pos.y + 28;
      this.ctx.fillText(v.name, pos.x, labelY);
    });
  }

  drawWeightBadge(p1, p2, weight, isHighlighted) {
    const midX = (p1.x + p2.x) / 2;
    const midY = (p1.y + p2.y) / 2;

    const text = weight.toString();
    this.ctx.font = "bold 10px monospace";
    const textWidth = this.ctx.measureText(text).width;
    const boxW = Math.max(textWidth + 8, 18);
    const boxH = 14;

    this.ctx.fillStyle = isHighlighted
      ? (this.highlightType === "dijkstra" ? "#16a34a" : "#d97706")
      : "#ffffff";
    this.ctx.strokeStyle = isHighlighted ? "#ffffff" : "#94a3b8";
    this.ctx.lineWidth = 1;

    this.ctx.fillRect(midX - boxW / 2, midY - boxH / 2, boxW, boxH);
    this.ctx.strokeRect(midX - boxW / 2, midY - boxH / 2, boxW, boxH);

    this.ctx.fillStyle = isHighlighted ? "#ffffff" : "#0f172a";
    this.ctx.textAlign = "center";
    this.ctx.textBaseline = "middle";
    this.ctx.fillText(text, midX, midY);
  }
}

window.GraphCanvasRenderer = GraphCanvasRenderer;
