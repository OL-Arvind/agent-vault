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
    """Finds graphify executable in PATH, active Python environment, or uv tool directories."""
    # 1. System PATH
    cmd = shutil.which("graphify")
    if cmd:
        return Path(cmd)
    
    # 2. Same environment as running python interpreter
    bin_name = "graphify.exe" if sys.platform == "win32" else "graphify"
    py_dir = Path(sys.executable).parent
    env_candidate = py_dir / bin_name
    if env_candidate.exists():
        return env_candidate
    
    for sub in ["Scripts", "bin"]:
        sub_candidate = py_dir / sub / bin_name
        if sub_candidate.exists():
            return sub_candidate

    # 3. Standard uv tools location
    home = Path.home()
    if sys.platform == "win32":
        candidates = [
            home / "AppData" / "Roaming" / "uv" / "tools" / "graphifyy" / "Scripts" / "graphify.exe",
            home / ".local" / "bin" / "graphify.exe",
        ]
    else:
        candidates = [
            home / ".local" / "bin" / "graphify",
            home / ".cargo" / "bin" / "graphify",
        ]
    for c in candidates:
        if c.exists():
            return c
        
    return None

def export_html(vault_dir: Path, out_dir: Path) -> bool:
    """Invokes Graphify CLI to export the native interactive 3D graph.html."""
    graphify_bin = find_graphify_executable()
    if not graphify_bin:
        return False
    
    try:
        subprocess.run([str(graphify_bin), "export", "html"], cwd=str(vault_dir), capture_output=True, text=True)
        return (out_dir / "graph.html").exists()
    except Exception:
        return False

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

        # Export HTML via Graphify
        export_html(vault_dir, out_dir)

        return {
            "nodes": G.number_of_nodes(),
            "edges": G.number_of_edges(),
            "communities": len(communities),
            "status": "success"
        }
    except ImportError:
        # Save graph.json
        graph_json = {
            "nodes": nodes,
            "edges": edges
        }
        (out_dir / "graph.json").write_text(json.dumps(graph_json, indent=2), encoding="utf-8")
        
        # Export HTML via Graphify CLI
        exported = export_html(vault_dir, out_dir)

        return {
            "nodes": len(nodes),
            "edges": len(edges),
            "communities": 0,
            "status": "success" if exported else "missing_graphify"
        }
