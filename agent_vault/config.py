import os
from pathlib import Path
from typing import List, Tuple

def get_home_dir() -> Path:
    """Returns the user home directory cross-platform."""
    return Path.home()

def get_default_vault_dir() -> Path:
    """Returns default destination path for the normalized knowledge vault."""
    return get_home_dir() / "knowledge_vault"

def discover_antigravity_sources() -> List[Tuple[str, Path]]:
    """
    Auto-detects Antigravity desktop and CLI session directories across Windows, macOS, and Linux.
    Returns a list of (label, path) tuples that actually exist.
    """
    home = get_home_dir()
    candidates = [
        ("antigravity-desktop", home / ".gemini" / "antigravity" / "brain"),
        ("antigravity-cli", home / ".gemini" / "antigravity-cli" / "brain"),
        ("antigravity-ide", home / ".gemini" / "antigravity-ide" / "brain"),
    ]
    
    # Also support custom environment variable overrides
    env_custom = os.environ.get("ANTIGRAVITY_BRAIN_DIR")
    if env_custom:
        custom_path = Path(env_custom)
        if custom_path.exists():
            candidates.insert(0, ("antigravity-custom", custom_path))

    return [(label, p) for label, p in candidates if p.exists() and p.is_dir()]

DEFAULT_CONCEPTS = [
    "react", "nextjs", "next.js", "typescript", "javascript", "python",
    "supabase", "postgresql", "postgres", "docker", "prisma", "fastapi",
    "tailwind", "css", "html", "git", "github", "graphql", "api", "rest",
    "auth", "authentication", "jwt", "database", "sql", "redis",
    "graphify", "ast", "tree-sitter", "rag", "knowledge graph", "mcp",
    "real estate", "ledger", "pdf", "report", "figma", "ui", "ux", "design",
    "jest", "pytest", "playwright", "cypress", "ci/cd", "kubernetes"
]
