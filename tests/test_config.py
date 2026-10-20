from pathlib import Path
from agent_vault.config import get_home_dir, get_default_vault_dir, discover_antigravity_sources, DEFAULT_CONCEPTS

def test_config_paths():
    home = get_home_dir()
    assert isinstance(home, Path)

    vault_dir = get_default_vault_dir()
    assert isinstance(vault_dir, Path)
    assert vault_dir.name == "knowledge_vault"

def test_default_concepts():
    assert len(DEFAULT_CONCEPTS) > 0
    assert "python" in DEFAULT_CONCEPTS
    assert "mcp" in DEFAULT_CONCEPTS
