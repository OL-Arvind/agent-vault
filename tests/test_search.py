import pytest
from pathlib import Path
from agent_vault.mcp_server import search_vault

def test_search_vault_empty(tmp_path: Path):
    results = search_vault("python", vault_dir=tmp_path)
    assert results == []

def test_search_vault_matches(tmp_path: Path):
    doc1 = tmp_path / "conv_abc123.md"
    doc1.write_text(
        "# Fix Docker Compose Network Issue\n\n**Date:** 2026-10-18\n\nSolved container port binding in Docker.\n",
        encoding="utf-8"
    )

    doc2 = tmp_path / "conv_def456.md"
    doc2.write_text(
        "# Optimize PostgreSQL Queries\n\n**Date:** 2026-10-19\n\nAdded indexes to PostgreSQL database.\n",
        encoding="utf-8"
    )

    # Search for docker
    res_docker = search_vault("docker container", vault_dir=tmp_path)
    assert len(res_docker) == 1
    assert res_docker[0]["conversation_id"] == "abc123"
    assert "Docker" in res_docker[0]["title"]
    assert res_docker[0]["date"] == "2026-10-18"

    # Search for postgres
    res_pg = search_vault("postgresql database", vault_dir=tmp_path)
    assert len(res_pg) == 1
    assert res_pg[0]["conversation_id"] == "def456"

def test_search_vault_limits_and_scoring(tmp_path: Path):
    for i in range(10):
        doc = tmp_path / f"conv_session_{i}.md"
        doc.write_text(
            f"# Test Session {i}\n\n**Date:** 2026-10-0{i}\n\nKey term repeated: {'react ' * (i + 1)}\n",
            encoding="utf-8"
        )

    res = search_vault("react", vault_dir=tmp_path, limit=3)
    assert len(res) == 3
    # Highest score should be session 9
    assert res[0]["conversation_id"] == "session_9"
