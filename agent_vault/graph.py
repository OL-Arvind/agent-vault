import re
import json
import shutil
import subprocess
import sys
from pathlib import Path
from collections import Counter
from typing import Dict, Any, List

from agent_vault.config import DEFAULT_CONCEPTS

def slugify(text: str) -> str:
    s = re.sub(r'[^a-zA-Z0-9]+', '_', text.strip().lower())
    s = re.sub(r'_+', '_', s).strip('_')
    return s[:60]

def extract_nodes_and_edges(vault_dir: Path, concepts: List[str] = None) -> Dict[str, Any]:
    """Scans all conv_*.md files in vault_dir and constructs a knowledge graph."""
    if concepts is None:
        concepts = DEFAULT_CONCEPTS

    nodes = {}
    edges = []
    md_files = list(vault_dir.glob("conv_*.md"))

    for fpath in md_files:
        content = fpath.read_text(encoding="utf-8", errors="ignore")
        conv_id = fpath.stem.replace("conv_", "")

        # 1. Title
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else fpath.stem
        title_clean = title.replace('`', '').strip()[:80]

        conv_node_id = f"conv_{slugify(conv_id)[:30]}"
        if conv_node_id not in nodes:
            nodes[conv_node_id] = {
                "id": conv_node_id,
                "label": title_clean,
                "file_type": "document",
                "source_file": str(fpath.resolve()),
                "source_location": None,
                "source_url": None,
                "captured_at": None,
                "author": None,
                "contributor": None
            }

        # 2. Files Referenced
        files_section = re.search(r'### Key Files & Modules Referenced\n(.*?)(?=\n###|\n---|\n##)', content, re.DOTALL)
        if files_section:
            file_lines = re.findall(r'-\s+`([^`]+)`', files_section.group(1))
            for raw_file in file_lines:
                norm_f = raw_file.replace('\\', '/').strip()
                f_name = Path(norm_f).name
                if not f_name or len(f_name) < 2:
                    continue
                file_node_id = f"file_{slugify(norm_f)}"
                if file_node_id not in nodes:
                    nodes[file_node_id] = {
                        "id": file_node_id,
                        "label": f_name,
                        "file_type": "code",
                        "source_file": norm_f,
                        "source_location": None,
                        "source_url": None,
                        "captured_at": None,
                        "author": None,
                        "contributor": None
                    }
                edges.append({
                    "source": conv_node_id,
                    "target": file_node_id,
                    "relation": "references",
                    "confidence": "EXTRACTED",
                    "confidence_score": 1.0,
                    "source_file": str(fpath.resolve()),
                    "source_location": None,
                    "weight": 1.0
                })

        # 3. Concepts
        lower_content = content.lower()
        for concept in concepts:
            pattern = r'\b' + re.escape(concept) + r'\b'
            if re.search(pattern, lower_content):
                concept_node_id = f"concept_{slugify(concept)}"
                if concept_node_id not in nodes:
                    nodes[concept_node_id] = {
                        "id": concept_node_id,
                        "label": concept.title(),
                        "file_type": "concept",
                        "source_file": str(fpath.resolve()),
                        "source_location": None,
                        "source_url": None,
                        "captured_at": None,
                        "author": None,
                        "contributor": None
                    }
                edges.append({
                    "source": conv_node_id,
                    "target": concept_node_id,
                    "relation": "conceptually_related_to",
                    "confidence": "INFERRED",
                    "confidence_score": 0.85,
                    "source_file": str(fpath.resolve()),
                    "source_location": None,
                    "weight": 0.85
                })

    return {
        "nodes": list(nodes.values()),
        "edges": edges,
        "hyperedges": [],
        "input_tokens": 0,
        "output_tokens": 0
    }

def find_graphify_executable() -> Path | None:
    """Finds graphify executable in PATH or via uv tools."""
    cmd = shutil.which("graphify")
    if cmd:
        return Path(cmd)
    
    # Check uv tools on Windows
    home = Path.home()
    uv_candidate = home / "AppData" / "Roaming" / "uv" / "tools" / "graphifyy" / "Scripts" / "graphify.exe"
    if uv_candidate.exists():
        return uv_candidate
        
    return None

def generate_standalone_html(out_dir: Path, nodes: list, edges: list):
    """Generates an embedded interactive D3.js knowledge graph visualizer."""
    html_path = out_dir / "graph.html"
    
    # Cap displayed nodes to 800 for smooth browser rendering if very large
    display_nodes = nodes[:1000]
    node_id_set = {n["id"] for n in display_nodes}
    display_edges = [
        {"source": e["source"], "target": e["target"], "relation": e.get("relation", "relates")}
        for e in edges if e["source"] in node_id_set and e["target"] in node_id_set
    ]

    graph_data_json = json.dumps({"nodes": display_nodes, "links": display_edges}, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Agent-Vault Knowledge Graph</title>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: #0f1117; color: #e1e4ea; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; overflow: hidden; }}
    #header {{ position: absolute; top: 16px; left: 20px; z-index: 10; background: rgba(22, 27, 34, 0.85); backdrop-filter: blur(8px); padding: 12px 20px; border-radius: 12px; border: 1px solid #30363d; display: flex; align-items: center; gap: 16px; }}
    #header h1 {{ font-size: 16px; font-weight: 600; color: #58a6ff; letter-spacing: -0.3px; }}
    #header .stats {{ font-size: 13px; color: #8b949e; }}
    #search {{ background: #0d1117; border: 1px solid #30363d; color: #fff; padding: 6px 12px; border-radius: 6px; font-size: 13px; outline: none; width: 220px; }}
    #search:focus {{ border-color: #58a6ff; }}
    #sidebar {{ position: absolute; top: 16px; right: 20px; width: 340px; max-height: calc(100vh - 32px); overflow-y: auto; background: rgba(22, 27, 34, 0.95); backdrop-filter: blur(10px); padding: 20px; border-radius: 12px; border: 1px solid #30363d; display: none; z-index: 10; font-size: 13px; }}
    #sidebar h3 {{ font-size: 15px; margin-bottom: 8px; color: #58a6ff; word-break: break-word; }}
    #sidebar .type {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; margin-bottom: 12px; }}
    #sidebar .meta {{ color: #8b949e; margin-bottom: 6px; }}
    #sidebar .path {{ word-break: break-all; font-family: monospace; font-size: 11px; color: #79c0ff; background: #0d1117; padding: 6px; border-radius: 6px; }}
    #sidebar button {{ margin-top: 12px; background: #21262d; border: 1px solid #30363d; color: #c9d1d9; padding: 4px 10px; border-radius: 6px; cursor: pointer; }}
    #sidebar button:hover {{ background: #30363d; }}
    svg {{ width: 100vw; height: 100vh; cursor: grab; }}
    svg:active {{ cursor: grabbing; }}
    .link {{ stroke: #30363d; stroke-opacity: 0.6; stroke-width: 1px; }}
    .node {{ stroke: #fff; stroke-width: 1.5px; cursor: pointer; transition: r 0.2s; }}
    .node:hover {{ stroke-width: 3px; stroke: #58a6ff; }}
    .node-label {{ fill: #c9d1d9; font-size: 10px; pointer-events: none; text-shadow: 0 1px 3px rgba(0,0,0,0.8); }}
  </style>
</head>
<body>
  <div id="header">
    <h1>Agent-Vault</h1>
    <div class="stats"><span id="node-count">0</span> nodes &middot; <span id="link-count">0</span> connections</div>
    <input id="search" type="text" placeholder="Filter nodes..." />
  </div>

  <div id="sidebar">
    <h3 id="side-title">Node Title</h3>
    <span id="side-type" class="type">document</span>
    <div class="meta" id="side-id">ID: conv_...</div>
    <div class="path" id="side-file">file/path...</div>
    <button onclick="document.getElementById('sidebar').style.display='none'">Close</button>
  </div>

  <svg id="canvas"></svg>

  <script>
    const data = {graph_data_json};
    document.getElementById("node-count").innerText = data.nodes.length;
    document.getElementById("link-count").innerText = data.links.length;

    const width = window.innerWidth;
    const height = window.innerHeight;

    const colorMap = {{
      document: "#a371f7",
      code: "#58a6ff",
      concept: "#3fb950"
    }};

    const svg = d3.select("#canvas")
      .attr("viewBox", [0, 0, width, height]);

    const g = svg.append("g");

    const zoom = d3.zoom()
      .scaleExtent([0.1, 8])
      .on("zoom", (e) => g.attr("transform", e.transform));

    svg.call(zoom);

    const simulation = d3.forceSimulation(data.nodes)
      .force("link", d3.forceLink(data.links).id(d => d.id).distance(60))
      .force("charge", d3.forceManyBody().strength(-120))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(14));

    const link = g.append("g")
      .selectAll("line")
      .data(data.links)
      .join("line")
      .attr("class", "link");

    const node = g.append("g")
      .selectAll("circle")
      .data(data.nodes)
      .join("circle")
      .attr("class", "node")
      .attr("r", d => d.file_type === "concept" ? 8 : (d.file_type === "code" ? 5 : 7))
      .attr("fill", d => colorMap[d.file_type] || "#8b949e")
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended))
      .on("click", (e, d) => selectNode(d));

    const label = g.append("g")
      .selectAll("text")
      .data(data.nodes)
      .join("text")
      .attr("class", "node-label")
      .attr("dx", 10)
      .attr("dy", 3)
      .text(d => d.label.length > 25 ? d.label.slice(0, 25) + "..." : d.label);

    simulation.on("tick", () => {{
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);

      label
        .attr("x", d => d.x)
        .attr("y", d => d.y);
    }});

    function selectNode(d) {{
      const sb = document.getElementById("sidebar");
      sb.style.display = "block";
      document.getElementById("side-title").innerText = d.label;
      const typeSpan = document.getElementById("side-type");
      typeSpan.innerText = d.file_type;
      typeSpan.style.background = (colorMap[d.file_type] || "#8b949e") + "33";
      typeSpan.style.color = colorMap[d.file_type] || "#8b949e";
      document.getElementById("side-id").innerText = "ID: " + d.id;
      document.getElementById("side-file").innerText = d.source_file || "N/A";
    }}

    document.getElementById("search").addEventListener("input", (e) => {{
      const val = e.target.value.toLowerCase();
      node.style("opacity", d => (d.label.toLowerCase().includes(val) || d.id.includes(val)) ? 1 : 0.15);
      label.style("opacity", d => d.label.toLowerCase().includes(val) ? 1 : 0.15);
    }});

    function dragstarted(event) {{
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }}
    function dragged(event) {{
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }}
    function dragended(event) {{
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }}
  </script>
</body>
</html>
"""
    html_path.write_text(html_content, encoding="utf-8")

def export_html(vault_dir: Path, out_dir: Path, nodes: list = None, edges: list = None):
    """Generates graph.html either via Graphify CLI or through the standalone D3 fallback."""
    # 1. Try Graphify CLI export first
    graphify_bin = find_graphify_executable()
    if graphify_bin:
        try:
            subprocess.run([str(graphify_bin), "export", "html"], cwd=str(vault_dir), capture_output=True)
            if (out_dir / "graph.html").exists():
                return
        except Exception:
            pass

    # 2. Always generate standalone interactive D3 HTML visualizer if graph.html is missing
    if nodes is not None and edges is not None:
        generate_standalone_html(out_dir, nodes, edges)

def build_knowledge_graph(vault_dir: Path, out_dir: Path = None) -> Dict[str, Any]:
    """Compiles extracted nodes/edges into graphify-out artifacts."""
    if out_dir is None:
        out_dir = vault_dir / "graphify-out"
    out_dir.mkdir(parents=True, exist_ok=True)

    extracted = extract_nodes_and_edges(vault_dir)
    extract_path = out_dir / ".graphify_extract.json"
    extract_path.write_text(json.dumps(extracted, indent=2, ensure_ascii=False), encoding="utf-8")

    nodes = extracted["nodes"]
    edges = extracted["edges"]

    # If graphify library is installed in python, use it directly
    try:
        from graphify.build import build_from_json
        from graphify.cluster import cluster, score_all
        from graphify.analyze import god_nodes, surprising_connections, suggest_questions
        from graphify.report import generate
        from graphify.export import to_json

        G = build_from_json(extracted, root=str(vault_dir), directed=False)
        communities = cluster(G)
        cohesion = score_all(G, communities)
        tokens = {'input': 0, 'output': 0}
        gods = god_nodes(G)
        surprises = surprising_connections(G, communities)

        node_map = {n["id"]: n for n in nodes}
        labels = {}
        for cid, node_ids in communities.items():
            comm_nodes = [node_map[nid] for nid in node_ids if nid in node_map]
            concepts = [n["label"] for n in comm_nodes if n.get("file_type") == "concept"]
            if concepts:
                top_concepts = [c for c, _ in Counter(concepts).most_common(2)]
                labels[cid] = " & ".join(top_concepts)
            else:
                labels[cid] = f"Engineering Cluster {cid}"

        questions = suggest_questions(G, communities, labels)
        detection = {"total_files": len(nodes), "total_words": 0, "files": {}}
        report = generate(G, communities, cohesion, labels, gods, surprises, detection, tokens, str(vault_dir), suggested_questions=questions)
        (out_dir / "GRAPH_REPORT.md").write_text(report, encoding="utf-8")
        to_json(G, communities, str(out_dir / "graph.json"), community_labels=labels)

        # Export HTML
        export_html(vault_dir, out_dir, nodes, edges)

        return {
            "nodes": G.number_of_nodes(),
            "edges": G.number_of_edges(),
            "communities": len(communities),
            "status": "success"
        }
    except ImportError:
        # Fallback: simple graph.json output + D3 HTML visualizer
        graph_json = {
            "nodes": nodes,
            "edges": edges
        }
        (out_dir / "graph.json").write_text(json.dumps(graph_json, indent=2), encoding="utf-8")
        
        # Always export HTML even without python graphify library
        export_html(vault_dir, out_dir, nodes, edges)

        return {
            "nodes": len(nodes),
            "edges": len(edges),
            "communities": 0,
            "status": "fallback_no_graphify"
        }
