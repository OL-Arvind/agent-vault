import os
import sys
import webbrowser
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from agent_vault.config import discover_antigravity_sources, get_default_vault_dir
from agent_vault.extractors.antigravity import AntigravityExtractor
from agent_vault.graph import build_knowledge_graph
from agent_vault.mcp_server import search_vault, run_mcp_server
from agent_vault import __version__

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

console = Console(highlight=False, legacy_windows=False)

@click.group()
@click.version_option(__version__, prog_name="agent-vault")
def main():
    """Agent-Vault: Turn local AI coding agent sessions into a queryable knowledge graph."""
    pass

@main.command()
def scan():
    """Discover AI agent session directories on this machine."""
    console.print(Panel.fit("[bold cyan]Agent-Vault Discovery[/bold cyan]\nScanning local system for agent session directories...", border_style="cyan"))
    
    sources = discover_antigravity_sources()
    if not sources:
        console.print("[yellow]No Antigravity session directories found.[/yellow]")
        console.print("Make sure you have run Antigravity on this machine, or set ANTIGRAVITY_BRAIN_DIR.")
        return

    table = Table(title="Detected Agent Sources", show_header=True, header_style="bold magenta")
    table.add_column("Agent / Surface", style="dim")
    table.add_column("Path")
    table.add_column("Sessions Found", justify="right")

    total_sessions = 0
    for label, path in sources:
        count = sum(1 for item in path.iterdir() if item.is_dir() and (item / ".system_generated" / "logs" / "transcript.jsonl").exists())
        total_sessions += count
        table.add_row(label, str(path), str(count))

    console.print(table)
    console.print(f"[green][+] Found {total_sessions} active agent sessions ready to vault.[/green]")

@main.command()
@click.option("--output", "-o", type=click.Path(), default=None, help="Custom output directory for the vault.")
def build(output):
    """Normalize agent transcripts into Markdown dev cards and build the Knowledge Graph."""
    vault_dir = Path(output) if output else get_default_vault_dir()
    vault_dir.mkdir(parents=True, exist_ok=True)

    console.print(Panel.fit(f"[bold green]Building Agent-Vault[/bold green]\nDestination: [cyan]{vault_dir}[/cyan]\nMode: [bold]Read-Only on source files[/bold]", border_style="green"))

    extractor = AntigravityExtractor()
    sessions = extractor.discover_sessions()

    if not sessions:
        console.print("[red]No sessions found to extract. Run 'agent-vault scan' first.[/red]")
        return

    console.print(f"[*] Processing {len(sessions)} sessions...")
    seen = set()
    processed = 0
    vault_index = []

    with console.status("[bold green]Extracting and cleaning session transcripts...") as status:
        for label, session_dir in sessions:
            conv_id = session_dir.name
            if conv_id in seen:
                continue

            parsed = extractor.parse_session(session_dir)
            if not parsed or not parsed["turns"]:
                continue

            md_content = extractor.render_markdown(conv_id, label, parsed)
            out_file = vault_dir / f"conv_{conv_id}.md"
            out_file.write_text(md_content, encoding="utf-8")

            seen.add(conv_id)
            processed += 1
            first_ts = parsed["turns"][0]["timestamp"] if parsed["turns"] else ""
            vault_index.append({
                "id": conv_id,
                "title": parsed["title"],
                "date": first_ts,
                "file": f"conv_{conv_id}.md",
                "turns": len(parsed["turns"])
            })

    # Master INDEX.md
    vault_index.sort(key=lambda x: x["date"], reverse=True)
    index_md = [
        "# Antigravity Knowledge Vault Index",
        "",
        f"Total indexed engineering conversations: **{len(vault_index)}**",
        "",
        "| Date | Title | Turns | Conversation ID | File |",
        "| :--- | :--- | :--- | :--- | :--- |"
    ]
    for item in vault_index:
        clean_title = item['title'].replace('|', '-').strip()
        cid_short = item['id'][:8] + "..."
        index_md.append(f"| {item['date'][:10]} | {clean_title} | {item['turns']} | `{cid_short}` | [{item['file']}](./{item['file']}) |")

    (vault_dir / "INDEX.md").write_text("\n".join(index_md), encoding="utf-8")
    console.print(f"[green][+] Extracted {processed} conversation cards + INDEX.md[/green]")

    # Build Graph
    with console.status("[bold cyan]Constructing Knowledge Graph & Community Clusters...") as status:
        graph_res = build_knowledge_graph(vault_dir)

    console.print(f"[bold green][+] Knowledge Graph Compiled![/bold green] ({graph_res.get('nodes', 0)} nodes, {graph_res.get('edges', 0)} edges)")
    html_file = vault_dir / "graphify-out" / "graph.html"
    if html_file.exists():
        console.print(f"[green][+] Interactive 3D visualizer saved:[/green] [cyan]{html_file}[/cyan]")
    else:
        console.print("[yellow][!] Graphify was not detected to compile graph.html.[/yellow]")
        console.print("    Please install Graphify: [bold cyan]uv tool install graphifyy[/bold cyan] (or [bold cyan]pip install graphifyy[/bold cyan])")
        console.print("    Then re-run: [bold]agent-vault build[/bold]")
    console.print(f"\n[cyan]Tip: Run [bold]agent-vault view[/bold] to open your interactive graph in the browser.[/cyan]")

@main.command()
@click.option("--dir", "-d", type=click.Path(), default=None, help="Vault directory.")
def view(dir):
    """Open the interactive graph.html visualizer in your default browser."""
    vault_dir = Path(dir) if dir else get_default_vault_dir()
    out_dir = vault_dir / "graphify-out"
    html_file = out_dir / "graph.html"

    if not html_file.exists():
        # Check if vault exists and build visualizer via Graphify
        if (out_dir / "graph.json").exists() or any(vault_dir.glob("conv_*.md")):
            console.print("[yellow]graph.html not found, compiling visualizer with Graphify...[/yellow]")
            build_knowledge_graph(vault_dir, out_dir)
        else:
            console.print(f"[red]No vault data found in {vault_dir}.[/red]")
            console.print("Run 'agent-vault build' first to extract your sessions and compile the graph.")
            return

    if not html_file.exists():
        console.print(f"[red]Graphify is required to generate the interactive graph visualizer.[/red]")
        console.print("Please install Graphify: [bold cyan]uv tool install graphifyy[/bold cyan] (or [bold cyan]pip install graphifyy[/bold cyan])")
        console.print("Then run: [bold]agent-vault build[/bold]")
        return

    console.print(f"[green]Opening Knowledge Graph in your browser:[/green] [cyan]{html_file}[/cyan]")
    webbrowser.open(html_file.resolve().as_uri())

@main.command()
@click.argument("query", nargs=-1, required=True)
@click.option("--limit", "-l", default=5, help="Number of results to show.")
def search(query, limit):
    """Search past agent solutions by keyword or phrase."""
    query_str = " ".join(query).strip()
    results = search_vault(query_str, limit=limit)
    if not results:
        console.print(f"[yellow]No past solutions found matching '{query_str}'.[/yellow]")
        return

    table = Table(title=f"Results for '{query_str}'", show_header=True, header_style="bold green")
    table.add_column("ID", style="bold cyan", width=10)
    table.add_column("Date", style="dim", width=12)
    table.add_column("Conversation Topic", width=36)
    table.add_column("Snippet")

    for r in results:
        table.add_row(r["conversation_id"][:8], r["date"][:10], r["title"][:34], r["snippet"][:100] + "...")

    console.print(table)
    console.print("\n[dim]Tip: Run [bold cyan]agent-vault show <ID>[/bold cyan] to view the full dev card & code solution.[/dim]")

@main.command()
@click.argument("conv_id")
@click.option("--open", "-o", "open_editor", is_flag=True, help="Open dev card file in your default system editor.")
def show(conv_id, open_editor):
    """View the full Markdown dev card and code solution for a conversation ID."""
    vault_dir = get_default_vault_dir()
    clean_id = conv_id.replace("conv_", "").strip().lower()
    
    # Try exact match or partial match
    target = vault_dir / f"conv_{clean_id}.md"
    if not target.exists():
        matches = [f for f in vault_dir.glob("conv_*.md") if clean_id in f.stem.lower()]
        if matches:
            target = matches[0]
        else:
            console.print(f"[red]No dev card found matching ID '{conv_id}' in {vault_dir}[/red]")
            return

    if open_editor:
        import subprocess
        console.print(f"[green]Opening dev card:[/green] [cyan]{target}[/cyan]")
        if sys.platform == "win32":
            os.startfile(str(target))
        else:
            subprocess.run(["xdg-open" if sys.platform != "darwin" else "open", str(target)])
        return

    from rich.markdown import Markdown
    md_text = target.read_text(encoding="utf-8", errors="ignore")
    console.print(Panel(f"[bold cyan]Dev Card:[/bold cyan] {target.name}\n[dim]Path: {target}[/dim]", border_style="cyan"))
    console.print(Markdown(md_text))

@main.command()
def mcp():
    """Start the Model Context Protocol (MCP) server for AI agents."""
    console.print("[bold green]Starting Agent-Vault MCP stdio server...[/bold green]")
    run_mcp_server()

if __name__ == "__main__":
    main()
