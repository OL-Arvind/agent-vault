# ⚡ Agent-Vault

> **Turn your local AI coding agent sessions into an interactive Knowledge Graph and searchable Second Brain.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Architecture: 100% Local](https://img.shields.io/badge/privacy-100%25%20local-success.svg)]()
[![Supports: Antigravity](https://img.shields.io/badge/agents-Google%20Antigravity-orange.svg)]()
[![Platform: Win | macOS | Linux](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

---

## 📖 Table of Contents
- [The Problem](#-the-problem)
- [The Solution](#-the-solution)
- [System & Device Prerequisites](#-system--device-prerequisites)
- [Installation](#-installation)
- [Quickstart Guide](#-quickstart-guide)
- [CLI Command Reference](#-cli-command-reference)
- [Connecting to AI Agents (MCP)](#-connecting-to-ai-agents-mcp)
- [Privacy & Data Integrity Guarantees](#-privacy--data-integrity-guarantees)
- [Troubleshooting & FAQ](#-troubleshooting--faq)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🛑 The Problem

Developers pair with AI coding agents every single day. Over weeks and months of development, your agents solve hundreds of obscure compiler errors, craft complex database queries, and design modular architectures.

**The catch:** That valuable engineering knowledge is trapped in ephemeral chat tabs or buried inside gigabytes of raw, escaped JSON log files (`~/.gemini/antigravity`, `~/.cursor`, etc.). Month after month, you end up re-explaining the exact same bugs, conventions, and database schemas to your agents from scratch.

---

## 💡 The Solution

**Agent-Vault** is an open-source, 100% local CLI tool that:
1. **Safely Scans:** Discovers and reads your local agent sessions in strictly read-only mode (never modifies or deletes original chat logs).
2. **Normalizes:** Strips terminal noise, compiler dumps, and JSON escapes into clean, structured **Markdown Dev Cards**.
3. **GraphRAG & Community Detection:** Discovers relationships across all your projects and compiles an interactive 2D/3D knowledge graph via Graphify.
4. **Connects Back to Agents:** Exposes a native Model Context Protocol (MCP) server so your agents can automatically recall past solutions when you're coding.

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

## 🖥️ System & Device Prerequisites

Before installing Agent-Vault, ensure your system meets the following requirements:

### 1. Operating System
* **Windows:** Windows 10 or Windows 11 (64-bit).
* **macOS:** macOS 12 (Monterey) or later (Apple Silicon M-series or Intel).
* **Linux:** Any modern Linux distribution (Ubuntu 20.04+, Debian 11+, Fedora, Arch, etc.).

### 2. Python Environment
* **Python Version:** **Python 3.10** or higher (Python 3.11 or 3.12 recommended).
* Verify your Python version:
  ```bash
  python --version
  ```

### 3. Package Manager (Recommended)
* **[uv](https://github.com/astral-sh/uv)** (strongly recommended for 10-100x faster execution and automatic venv management):
  ```bash
  # Install uv (Windows)
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

  # Install uv (macOS / Linux)
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
* Standard `pip` and virtual environments (`venv`) are also fully supported.

### 4. AI Agent Sessions Installed
Agent-Vault requires at least one supported AI agent surface with past conversation history on disk:
* **Google Antigravity:**
  * **Desktop App:** `~/.gemini/antigravity/brain`
  * **CLI Harness:** `~/.gemini/antigravity-cli/brain`
  * **IDE Extension:** `~/.gemini/antigravity-ide/brain`
  *(On Windows, `~` corresponds to `C:\Users\<YourUsername>`)*
* *(Optional)* If your agent sessions are in a non-standard directory, you can set the `ANTIGRAVITY_BRAIN_DIR` environment variable.

### 5. Hardware & Web Browser
* **RAM:** Minimum 2 GB of available RAM.
* **Disk Space:** ~50–100 MB of free storage (vault markdown files and graph artifacts are very compact).
* **Web Browser:** Any modern browser with WebGL enabled (Google Chrome, Microsoft Edge, Brave, Firefox, or Safari) to render the interactive 2D/3D knowledge graph visualizer (`graph.html`).

---

## 📦 Installation

### Option A: Via `uv` (Recommended)
Run without installation:
```bash
uvx agent-vault --help
```
Or install globally as a tool:
```bash
uv tool install agent-vault
```

### Option B: Via `pip`
```bash
pip install agent-vault
```

### Option C: Developer / Source Install
Clone the repository and install in editable mode:
```bash
git clone https://github.com/arvin/agent-vault.git
cd agent-vault
uv venv
uv pip install -e .
```

---

## 🚀 Quickstart Guide

### Step 1: Scan Your System
Verify that Agent-Vault detects your agent sessions:
```bash
agent-vault scan
```
**Example output:**
```
+--------------------------------------------------------+
| Agent-Vault Discovery                                  |
| Scanning local system for agent session directories... |
+--------------------------------------------------------+
                            Detected Agent Sources                             
+-----------------------------------------------------------------------------+
| Agent / Surface     | Path                                 | Sessions Found |
|---------------------+--------------------------------------+----------------|
| antigravity-desktop | C:\Users\arvin\.gemini\antigravity   |            268 |
| antigravity-cli     | C:\Users\arvin\.gemini\antigravity-cli|             21 |
| antigravity-ide     | C:\Users\arvin\.gemini\antigravity-ide|            326 |
+-----------------------------------------------------------------------------+
[+] Found 615 active agent sessions ready to vault.
```

### Step 2: Build the Vault & Knowledge Graph
Extract all sessions into clean Markdown dev cards and compile the knowledge graph:
```bash
agent-vault build
```
*(Optionally specify a custom folder: `agent-vault build --output ./my-vault`)*

### Step 3: Open the Interactive Graph Visualizer
Open the interactive 2D/3D visualizer in your browser:
```bash
agent-vault view
```

### Step 4: Search Solutions from Your Terminal
Quickly search across past solutions by keyword:
```bash
agent-vault search "postgres connection pool"
```

---

## 🛠️ CLI Command Reference

| Command | Arguments / Flags | Description |
| :--- | :--- | :--- |
| `agent-vault scan` | None | Scans your local machine for agent session directories across Windows, macOS, and Linux. |
| `agent-vault build` | `--output, -o <dir>` | Normalizes raw logs into Markdown cards, builds `INDEX.md`, and compiles `graph.json`. |
| `agent-vault view` | `--dir, -d <dir>` | Opens the standalone interactive `graph.html` visualizer in your default browser. |
| `agent-vault search` | `<query> [--limit, -l N]` | Fast full-text search across past problems, code diffs, and solutions. |
| `agent-vault mcp` | None | Starts the Model Context Protocol (MCP) stdio server for live AI agent integration. |

---

## 🤖 Connecting to AI Agents (MCP)

Agent-Vault comes with native **Model Context Protocol (MCP)** support. Connecting it allows your AI coding agents to search and recall past solutions on demand.

### Adding to Google Antigravity or Claude Code (`mcp_config.json`):

Add the following to your agent's MCP configuration:

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

### Available MCP Tools:
* **`search_past_solutions(query, limit)`**: Natural-language search across past sessions, returning matching problem cards, dates, and code snippets.
* **`get_past_solution_details(conversation_id)`**: Retrieves the complete, unabridged Markdown dev card and solution details for any past session.

---

## 🔒 Privacy & Data Integrity Guarantees

* **100% Offline & Private:** Agent-Vault runs completely on your local machine. No session data, prompts, or code snippets are ever transmitted to any cloud or third-party server.
* **Strictly Read-Only on Agent Logs:** Agent-Vault opens original `.gemini` and agent session files strictly in read-only mode (`r`). Your original chat databases, logs, and IDE sessions are completely untouched.
* **Deterministic Storage:** Extracted files are saved as standard Markdown files (`~/knowledge_vault/conv_<id>.md`), ensuring you can view, edit, or back them up using Obsidian, VS Code, or Git.

---

## ❓ Troubleshooting & FAQ

#### Q: "agent-vault scan finds 0 sessions."
**A:** Ensure your AI agent has been run on the current user account. If your agent stores data in a non-standard location, define the environment variable:
```bash
# Windows PowerShell
$env:ANTIGRAVITY_BRAIN_DIR = "D:\CustomPath\.gemini\antigravity\brain"

# macOS / Linux
export ANTIGRAVITY_BRAIN_DIR="/custom/path/.gemini/antigravity/brain"
```

#### Q: "Does this slow down my IDE or agent while running?"
**A:** No. Agent-Vault is an offline indexer that runs only when you invoke it or when an agent queries it via MCP. It has zero runtime overhead on your IDE.

#### Q: "Can I open the generated vault in Obsidian?"
**A:** Yes! The generated `knowledge_vault/` folder is a standard Markdown vault containing internal links, YAML frontmatter, and an `INDEX.md` table of contents that works natively in Obsidian.

---

## 🗺️ Roadmap

- [x] Google Antigravity Desktop, CLI, and IDE support
- [x] Zero-token local extraction & normalizer
- [x] Graphify knowledge graph & community detection integration
- [x] Standalone interactive HTML visualizer (`graph.html`)
- [x] Fast MCP stdio server integration
- [ ] Cursor chat database (`state.vscdb`) support
- [ ] Claude Code session log support
- [ ] Aider chat history support
- [ ] Export to Obsidian canvas graphs

---

## 🤝 Contributing

Contributions from the developer community are warmly welcomed!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/cursor-extractor`)
3. Commit your changes (`git commit -m 'Add Cursor session extractor'`)
4. Push to the branch (`git push origin feature/cursor-extractor`)
5. Open a Pull Request

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for more information.

Built with ❤️ for the agent-first developer era.
