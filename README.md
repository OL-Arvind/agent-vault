# ⚡ Agent-Vault

> **Turn your local AI coding agent sessions into an interactive Knowledge Graph and searchable Second Brain.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Architecture: 100% Local](https://img.shields.io/badge/privacy-100%25%20local-success.svg)]()
[![Supports: Antigravity](https://img.shields.io/badge/agents-Google%20Antigravity-orange.svg)]()
[![Platform: Win | macOS | Linux](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![M8ven Score](https://m8ven.ai/badge/mcp/ol-arvind/agent-vault?variant=verified)](https://m8ven.ai/mcp/ol-arvind/agent-vault)

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

### 3. Graphify CLI (Knowledge Graph & 3D Visualizer Engine)
Agent-Vault uses **Graphify** (`graphifyy`) to detect community clusters, analyze surprising connections, and render the interactive 3D knowledge graph visualizer (`graph.html`):
```bash
# Install Graphify globally via uv (Recommended)
uv tool install graphifyy

# Or install via pip
pip install graphifyy
```

### 4. Package Manager (Recommended)
* **[uv](https://github.com/astral-sh/uv)** (strongly recommended for 10-100x faster execution and automatic venv management):
  ```bash
  # Install uv (Windows)
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

  # Install uv (macOS / Linux)
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
* Standard `pip` and virtual environments (`venv`) are also fully supported.

### 5. AI Agent Sessions Installed
Agent-Vault requires at least one supported AI agent surface with past conversation history on disk:
* **Google Antigravity:**
  * **Desktop App:** `~/.gemini/antigravity/brain`
  * **CLI Harness:** `~/.gemini/antigravity-cli/brain`
  * **IDE Extension:** `~/.gemini/antigravity-ide/brain`
  *(On Windows, `~` corresponds to `C:\Users\<YourUsername>`)*
* *(Optional)* If your agent sessions are in a non-standard directory, you can set the `ANTIGRAVITY_BRAIN_DIR` environment variable.

### 6. Hardware & Web Browser
* **RAM:** Minimum 2 GB of available RAM.
* **Disk Space:** ~50–100 MB of free storage (vault markdown files and graph artifacts are very compact).
* **Web Browser:** Any modern browser with WebGL enabled (Google Chrome, Microsoft Edge, Brave, Firefox, or Safari) to render the interactive 2D/3D knowledge graph visualizer (`graph.html`).

---

## 📦 Installation

### Option A: Install Globally as a CLI Tool (Recommended)
This makes `agent-vault` available globally in your terminal without needing to activate virtual environments:

```bash
# Install directly from the repository with full MCP support
uv tool install "git+https://github.com/OL-Arvind/agent-vault.git" --with "mcp>=1.0.0,<2.0.0"

# Or install locally after cloning
git clone https://github.com/OL-Arvind/agent-vault.git
cd agent-vault
uv tool install ".[all]" --force
```

### Option B: Run Instantly without Installation
Run any command on-the-fly via `uvx`:
```bash
uvx --from git+https://github.com/OL-Arvind/agent-vault.git agent-vault scan
```

### Option C: Developer / Virtual Environment Install
Clone the repository and set up a local editable environment:
```bash
git clone https://github.com/OL-Arvind/agent-vault.git
cd agent-vault

# 1. Create and install in a local virtual environment (editable mode with all extras)
uv venv
uv pip install -e ".[all]"

# 2. Activate the virtual environment:
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows Command Prompt:
.venv\Scripts\activate.bat
# macOS / Linux:
source .venv/bin/activate

# (Alternative) Run without activating by prefixing with 'uv run':
# uv run agent-vault scan
```

### 🔄 Updating to the Latest Version
When you pull new commits from GitHub, ensure the installed package updates:
```bash
git pull origin main

# If you installed globally via 'uv tool install':
uv tool install ".[all]" --force

# If you use a virtual environment (.venv):
uv pip install -e ".[all]"
```

---

## 🚀 Quickstart Guide

> **💡 Note for Virtual Environment Users:** If you used Option C and haven't activated `.venv`, prefix commands with `uv run` (e.g. `uv run agent-vault scan`). If you installed globally via `uv tool install`, you can run `agent-vault` directly anywhere.

### Step 1: Scan Your System
Verify that Agent-Vault detects your agent sessions:
```bash
agent-vault scan
# or: uv run agent-vault scan
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
| `agent-vault build` | `--output, -o <dir>` | Normalizes raw logs into Markdown cards, builds `INDEX.md`, and compiles knowledge graph via Graphify. |
| `agent-vault view` | `--dir, -d <dir>` | Opens the interactive 3D `graph.html` visualizer in your default browser. |
| `agent-vault search` | `<query> [--limit, -l N]` | Instant offline full-text search across past problems, code diffs, and solutions. |
| `agent-vault show` | `<conv_id> [--open, -o]` | Renders the full unabridged Markdown Dev Card in your terminal, or opens it in your editor. |
| `agent-vault ask` | `<query> [-p provider] [-m model]` | Ask natural-language questions and synthesize AI answers across your vault. |
| `agent-vault mcp` | None | Starts the Model Context Protocol (MCP) stdio server for live AI agent integration. |

---

## 🧠 Asking Your Vault: Two Flexible AI Paradigms

Agent-Vault offers two complementary ways to query and synthesize insights across your past sessions:

### Option 1: Connect to Your Existing AI Agents via MCP (Zero API Cost)

If you already use an AI coding agent or personal assistant, you don't need any extra API keys. Agent-Vault includes native **Model Context Protocol (MCP)** support. Your agent uses its own reasoning engine to search and recall past solutions on demand.

Works out of the box with:
* **Google Antigravity** (Desktop & CLI)
* **Claude Code** (Anthropic)
* **Cursor & Windsurf**
* **Meta Muse & Personal AI Assistants** (Any assistant supporting MCP stdio connectors)

#### Adding to your agent's MCP config (`mcp_config.json`):
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

#### What you can ask your agent:
> *"Search my vault: what repeated architectural patterns or attendance features did we build in July?"*
> *"Have we solved a PostgreSQL connection pool leak before? Show me the exact code we used."*

---

### Option 2: Direct Terminal AI (`agent-vault ask`) (Bring Your Own Key or Local LLM)

Prefer staying inside your terminal without opening an IDE? Run `agent-vault ask` to synthesize answers directly in PowerShell or Bash.

Agent-Vault auto-detects your environment key with **zero external dependencies**:

| Provider | Environment Variable | Default Model | Notes |
| :--- | :--- | :--- | :--- |
| **Google Gemini** | `$env:GEMINI_API_KEY` | `gemini-2.0-flash` | Free tier via Google AI Studio |
| **Groq** | `$env:GROQ_API_KEY` | `llama-3.3-70b-versatile` | Ultra-fast & free tier |
| **OpenAI** | `$env:OPENAI_API_KEY` | `gpt-4o-mini` | Standard API key |
| **Anthropic** | `$env:ANTHROPIC_API_KEY` | `claude-3-5-haiku` | Standard API key |
| **Local Ollama** | Run `ollama serve` | Any local model | **100% Offline, Private, 0 Cost** |

#### Example Usage:
```bash
# Windows PowerShell
$env:GEMINI_API_KEY = "AIzaSy..."
agent-vault ask "What are the common bug patterns in my React projects?"

# Or specify provider and model on the fly:
agent-vault ask "Summarize my attendance system design" --provider groq
agent-vault ask "Explain my database migration strategy" --provider ollama --model qwen2.5-coder
```

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
