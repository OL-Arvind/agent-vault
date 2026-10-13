import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from agent_vault.config import get_default_vault_dir

def search_vault(query: str, vault_dir: Path = None, limit: int = 5) -> List[Dict[str, Any]]:
    """Searches past sessions for matching terms."""
    if vault_dir is None:
        vault_dir = get_default_vault_dir()

    results = []
    tokens = [t.lower() for t in query.split() if len(t) > 2]
    if not tokens:
        tokens = [query.lower()]

    for fpath in vault_dir.glob("conv_*.md"):
        try:
            content = fpath.read_text(encoding="utf-8", errors="ignore")
            lower_content = content.lower()
            
            # Simple scoring by token match count
            score = sum(lower_content.count(tok) for tok in tokens)
            if score > 0:
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else fpath.stem
                
                date_match = re.search(r'\*\*Date:\*\*\s*(.+)$', content, re.MULTILINE)
                date_val = date_match.group(1).strip() if date_match else "Unknown"

                # Extract excerpt
                idx = min((lower_content.find(tok) for tok in tokens if tok in lower_content), default=0)
                start = max(0, idx - 100)
                end = min(len(content), idx + 300)
                snippet = content[start:end].replace('\n', ' ')

                results.append({
                    "conversation_id": fpath.stem.replace("conv_", ""),
                    "title": title,
                    "date": date_val,
                    "score": score,
                    "snippet": f"...{snippet}...",
                    "file_path": str(fpath.resolve())
                })
        except Exception:
            continue

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]

import sys

def run_mcp_server():
    """Runs standard input/output MCP server for AI agents."""
    FastMCP = None
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        try:
            from fastmcp import FastMCP
        except ImportError:
            pass

    if FastMCP is None:
        sys.stderr.write(
            "Error: MCP Python SDK (v1.x) is not installed.\n"
            "Install with: pip install 'agent-vault[mcp]' or pip install 'mcp>=1.0.0,<2.0.0'\n"
        )
        sys.stderr.flush()
        sys.exit(1)

    try:
        mcp = FastMCP("agent-vault")

        @mcp.tool()
        def search_past_solutions(query: str, limit: int = 5) -> str:
            """Search your past engineering conversations and agent solutions by keyword or topic."""
            res = search_vault(query, limit=limit)
            if not res:
                return f"No past sessions found matching: '{query}'"
            out = []
            for r in res:
                out.append(f"### [{r['date'][:10]}] {r['title']}\nID: `{r['conversation_id']}`\nSnippet: {r['snippet']}\nPath: {r['file_path']}\n")
            return "\n---\n".join(out)

        @mcp.tool()
        def get_past_solution_details(conversation_id: str) -> str:
            """Retrieve the complete markdown dev card and code solutions for a specific past conversation ID."""
            vault_dir = get_default_vault_dir()
            clean_id = conversation_id.replace("conv_", "").strip().lower()
            fpath = vault_dir / f"conv_{clean_id}.md"
            if not fpath.exists():
                # Try finding by partial ID
                matches = [f for f in vault_dir.glob("conv_*.md") if clean_id in f.stem.lower()]
                if matches:
                    fpath = matches[0]
                else:
                    return f"Conversation '{conversation_id}' not found in vault."
            return fpath.read_text(encoding="utf-8", errors="ignore")

        mcp.run()
    except Exception as e:
        sys.stderr.write(f"MCP server runtime error: {e}\n")
        sys.stderr.flush()
        sys.exit(1)
