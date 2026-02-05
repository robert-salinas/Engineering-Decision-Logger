import typer
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from .logger.manager import DecisionManager
from .git_integration.git_manager import GitManager
import os

app = typer.Typer(help="Engineering Decision Logger (EDL) CLI")
console = Console()
manager = DecisionManager()
git_manager = GitManager()

@app.command()
def log(
    title: str = typer.Option(..., prompt="Title of the decision"),
    context: str = typer.Option(..., prompt="Context and problem statement"),
    chosen_option: str = typer.Option(..., prompt="Chosen option"),
    rationale: str = typer.Option(..., prompt="Rationale for the decision"),
    status: str = typer.Option("Proposed", prompt="Status (Proposed/Accepted/Deprecated/Superseded)"),
    drivers: str = typer.Option("", help="Comma separated decision drivers"),
    options: str = typer.Option("", help="Comma separated considered options"),
    good: str = typer.Option("", help="Good consequences"),
    bad: str = typer.Option("", help="Bad consequences"),
    no_git: bool = typer.Option(False, "--no-git", help="Do not associate with git commit"),
):
    """Log a new engineering decision."""
    commit_hash = None
    if not no_git:
        commit_hash = git_manager.get_current_commit()

    data = {
        "title": title,
        "context": context,
        "chosen_option": chosen_option,
        "rationale": rationale,
        "status": status,
        "drivers": [d.strip() for d in drivers.split(",")] if drivers else [],
        "options": [o.strip() for o in options.split(",")] if options else [],
        "consequences_good": good,
        "consequences_bad": bad,
        "commit_hash": commit_hash
    }
    
    decision = manager.add_decision(data)
    console.print(f"[green]Decision logged successfully with ID: {decision.id}[/green]")
    if commit_hash:
        console.print(f"Associated with commit: [blue]{commit_hash[:7]}[/blue]")
    console.print(f"ADR file created in docs/ADR/")

@app.command()
def install_hooks():
    """Install Git hooks to help manage decisions."""
    success, message = git_manager.install_hook("pre-commit")
    if success:
        console.print(f"[green]{message}[/green]")
    else:
        console.print(f"[red]{message}[/red]")

@app.command()
def list():
    """List all engineering decisions."""
    decisions = manager.list_decisions()
    if not decisions:
        console.print("[yellow]No decisions found.[/yellow]")
        return

    table = Table(title="Engineering Decisions")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Date", style="blue")

    for d in decisions:
        table.add_row(str(d.id), d.title, d.status, d.date)

    console.print(table)

@app.command()
def search(query: str):
    """Search decisions by title, context, or rationale."""
    decisions = manager.search_decisions(query)
    if not decisions:
        console.print(f"[yellow]No decisions found matching '{query}'.[/yellow]")
        return

    table = Table(title=f"Search Results for '{query}'")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="magenta")
    table.add_column("Status", style="green")

    for d in decisions:
        table.add_row(str(d.id), d.title, d.status)

    console.print(table)

@app.command()
def show(decision_id: int):
    """Show detailed information for a decision."""
    decision = manager.get_decision(decision_id)
    if not decision:
        console.print(f"[red]Decision with ID {decision_id} not found.[/red]")
        return

    console.print(f"[bold magenta]Decision #{decision.id}: {decision.title}[/bold magenta]")
    console.print(f"[cyan]Status:[/cyan] {decision.status}")
    console.print(f"[cyan]Date:[/cyan] {decision.date}")
    console.print(f"[cyan]Commit:[/cyan] {decision.commit_hash or 'N/A'}")
    console.print("\n[bold]Context:[/bold]")
    console.print(decision.context)
    console.print("\n[bold]Decision Drivers:[/bold]")
    console.print(decision.drivers)
    console.print("\n[bold]Chosen Option:[/bold]")
    console.print(f"[green]{decision.chosen_option}[/green]")
    console.print("\n[bold]Rationale:[/bold]")
    console.print(decision.rationale)
    console.print("\n[bold]Consequences:[/bold]")
    console.print(f"[green]Good:[/green] {decision.consequences_good}")
    console.print(f"[red]Bad:[/red] {decision.consequences_bad}")

if __name__ == "__main__":
    app()
