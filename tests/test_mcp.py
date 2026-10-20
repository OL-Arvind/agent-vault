import pytest
import asyncio
from pathlib import Path
from unittest.mock import patch
from agent_vault.mcp_server import create_mcp_server, READ_ONLY_TOOL_ANNOTATIONS

def test_read_only_tool_annotations_constant():
    """Ensure standard MCP security hints are defined with required boolean values."""
    assert READ_ONLY_TOOL_ANNOTATIONS["readOnlyHint"] is True
    assert READ_ONLY_TOOL_ANNOTATIONS["destructiveHint"] is False
    assert READ_ONLY_TOOL_ANNOTATIONS["idempotentHint"] is True
    assert READ_ONLY_TOOL_ANNOTATIONS["openWorldHint"] is False

def test_create_mcp_server_and_tool_annotations():
    """Verify FastMCP server initializes and exposes both declared tools with all 4 hints."""
    server = create_mcp_server()
    assert server is not None

    async def verify_tools():
        tools = await server.list_tools()
        tool_map = {t.name: t for t in tools}

        assert "search_past_solutions" in tool_map
        assert "get_past_solution_details" in tool_map

        for tool_name in ["search_past_solutions", "get_past_solution_details"]:
            tool = tool_map[tool_name]
            assert tool.annotations is not None
            assert tool.annotations.readOnlyHint is True
            assert tool.annotations.destructiveHint is False
            assert tool.annotations.idempotentHint is True
            assert tool.annotations.openWorldHint is False

    asyncio.run(verify_tools())

def test_mcp_tool_execution(tmp_path: Path):
    """Test invoking the declared MCP tools with mock knowledge vault files."""
    doc = tmp_path / "conv_deploy99.md"
    doc_content = "# Docker Production Setup\n\n**Date:** 2026-10-15\n\nFull deployment configuration details."
    doc.write_text(doc_content, encoding="utf-8")

    with patch("agent_vault.mcp_server.get_default_vault_dir", return_value=tmp_path):
        server = create_mcp_server()
        assert server is not None

        search_tool = server._tool_manager.get_tool("search_past_solutions")
        assert search_tool is not None

        # Test search_past_solutions with match
        search_res = search_tool.fn(query="Docker", limit=5)
        assert "Docker Production Setup" in search_res
        assert "deploy99" in search_res

        # Test search_past_solutions with no match
        empty_search = search_tool.fn(query="nonexistent_xyz", limit=5)
        assert "No past sessions found matching" in empty_search

        # Test get_past_solution_details with valid ID
        detail_tool = server._tool_manager.get_tool("get_past_solution_details")
        assert detail_tool is not None

        detail_res = detail_tool.fn(conversation_id="deploy99")
        assert "Full deployment configuration details" in detail_res

        # Test get_past_solution_details with unknown ID
        missing_res = detail_tool.fn(conversation_id="missing_id_404")
        assert "not found in vault" in missing_res
