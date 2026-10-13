# ⚡ Agent-Vault

> **Turn your local AI coding agent sessions into an interactive Knowledge Graph and searchable Second Brain.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Architecture: 100% Local](https://img.shields.io/badge/privacy-100%25%20local-success.svg)]()
[![Supports: Antigravity](https://img.shields.io/badge/agents-Google%20Antigravity-orange.svg)]()

---

## The Problem

Developers pair with AI coding agents every single day. Over months of building, your agents solve hundreds of obscure compiler errors, design complex schemas, and write tricky glue code.

**The catch:** That knowledge is trapped in ephemeral chat tabs or buried inside gigabytes of raw, escaped JSON log files (`~/.gemini/antigravity`, `~/.cursor`, etc.). Month after month, you end up re-explaining the exact same bugs and conventions to your agents from scratch.

## The Solution

**Agent-Vault** is an open-source, 100% local CLI tool that:
1. **Safely Scans:** Reads your local agent sessions in strictly read-only mode (never touches or deletes original chats).
2. **Normalizes:** Filters out terminal spam, compiler noise, and JSON escapes into clean, structured **Markdown Dev Cards**.
3. **GraphRAG & Community Detection:** Discovers relationships across all your projects and compiles an interactive 2D/3D knowledge graph via Graphify.
4. **Connects Back to Agents:** Exposes an MCP (Model Context Protocol) server so your agents can automatically recall past solutions when you're coding.

---

```
                       ┌─────────────────────────┐
                       │  Raw Agent Session Logs │
                       │ (~/.gemini/antigravity) │
                       └────────────┬────────────┘
                                    │ (Read-Only)
                                    ▼
                       ┌─────────────────────────┐
                       │   Agent-Vault Extractor │
                       └────────────┬────────────┘
                                    │
                                    ▼
               ┌───────────────────────────────────────────┐
               │    Clean Markdown Dev Cards & Index       │
               │   (Problem -> Solution -> Files Touched)  │
               └────────────┬─────────────────┬────────────┘
                            │                 │
                            ▼                 ▼
             ┌─────────────────────┐   ┌─────────────────────┐
             │ Interactive 3D/2D   │   │  Local MCP Server   │
             │ Knowledge Graph     │   │ (Antigravity/Cursor/│
             │ (graph.html)        │   │  Claude Integration)│
             └─────────────────────┘   └─────────────────────┘
```

---

## 🚀 Quickstart

### 1. Installation

Install via `pip` or run instantly with `uv`:

```bash
# Via uv (recommended, instant)
uv tool install agent-vault

# Via pip
pip install agent-vault
```

### 2. Scan Your Local System

Discover all agent conversations on your machine:

```bash
agent-vault scan
```

### 3. Build Your Knowledge Vault & Graph

Normalize all conversations into clean Markdown cards and compile the knowledge graph:

```bash
agent-vault build
```

### 4. Explore Visually

Open your interactive 3D knowledge graph directly in your browser:

```bash
agent-vault view
```

### 5. Search from Terminal

Search across your entire history of solved bugs and code snippets:

```bash
agent-vault search "postgres connection pool timeout"
```

---

## 🤖 Connect to AI Agents (MCP Support)

Agent-Vault includes native **Model Context Protocol (MCP)** support. When connected, your AI agents gain access to tools like `search_past_solutions` and `get_past_solution_details`.

### Add to Google Antigravity or Claude Code (`mcp_config.json`):

```json
{
  "mcpServers": {
    "agent-vault": {
      "command": "agent-vault",
      "args": ["mcp"]
    }
  }
}
```

Now, whenever you ask your agent:
> *"How did we implement the registry fees audit in the Real Estate project?"*

The agent queries Agent-Vault and pulls the exact past code files and architectural decisions into its context.

---

## 🛠️ CLI Reference

| Command | Description |
| :--- | :--- |
| `agent-vault scan` | Auto-detects agent session folders on Windows, macOS, and Linux. |
| `agent-vault build` | Extracts turn pairs into `~/knowledge_vault` and builds `graph.json`. |
| `agent-vault view` | Opens `graph.html` in your default web browser. |
| `agent-vault search <query>` | Performs instant keyword search across past solutions. |
| `agent-vault mcp` | Launches the Model Context Protocol stdio server. |

---

## 🗺️ Roadmap

- [x] Google Antigravity Desktop & CLI support
- [x] Markdown Dev Card extraction & master `INDEX.md`
- [x] Graphify knowledge graph & community detection integration
- [x] Fast MCP stdio server
- [ ] Cursor chat database (`state.vscdb`) support
- [ ] Claude Code session log support
- [ ] Aider chat history support
- [ ] Export to Obsidian canvas & markdown vault

---

## 🤝 Contributing

Contributions are warmly welcomed! 

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/cursor-extractor`)
3. Commit your changes (`git commit -m 'Add Cursor SQLite extractor'`)
4. Push to the branch (`git push origin feature/cursor-extractor`)
5. Open a Pull Request

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details. Built with ❤️ for the agent-first developer era.
