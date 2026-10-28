import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from pathlib import Path

from config import DEFAULT_EXCLUDE_PATTERNS, list_baselines, get_baseline_path
from core.scanner import scan_directory
from core.baseline import create_baseline, load_baseline, compare_with_baseline
from core.reporter import print_integrity_report, generate_markdown_report

app = typer.Typer(help="File Integrity Checker (Basic FIM Tool)")
console = Console()


@app.command()
def main():
    console.print(Panel.fit(
        "[bold green]File Integrity Checker (Basic FIM)[/bold green]\n"
        "Monitor multiple directories with named baselines",
        title="🔐 Welcome",
        border_style="blue"
    ))

    while True:
        console.print("\n[bold]What would you like to do?[/bold]\n")
        console.print("1. Create new baseline (from a directory/multiple directories)")
        console.print("2. Check integrity (compare current files vs baseline)")
        console.print("3. Show baseline information")
        console.print("4. Manage baselines (Delete / Reset)")
        console.print("5. Exit\n")

        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5"], default="2")

        if choice == "1":
            create_new_baseline()
        elif choice == "2":
            check_integrity()
        elif choice == "3":
            show_baseline_info()
        elif choice == "4":
            manage_baselines()
        elif choice == "5":
            console.print("[green]Goodbye! Stay secure.[/green]")
            break


def create_new_baseline():
    console.print("\n[cyan]Create New Baseline[/cyan]")
    name = Prompt.ask("Enter a name for this baseline (e.g. work, scripts)")
    directory = Prompt.ask("Enter directory path to monitor")

    dir_path = Path(directory).resolve()
    if not dir_path.exists():
        console.print(f"[red]Error: Directory does not exist.[/red]")
        return

    exclude_str = Prompt.ask(
        "Exclude patterns (comma separated) or press Enter for defaults",
        default=",".join(DEFAULT_EXCLUDE_PATTERNS)
    )
    exclude_patterns = [p.strip() for p in exclude_str.split(",") if p.strip()]

    console.print(f"[cyan]Scanning {dir_path}...[/cyan]")
    files = scan_directory(dir_path, exclude_patterns)

    if not files:
        console.print("[yellow]No files found.[/yellow]")
        return

    baseline_path = get_baseline_path(name)
    create_baseline(dir_path, files, baseline_path)

    console.print(f"[bold green]✅ Baseline '{name}' created successfully![/bold green]")
    console.print(f"   • Directory: {dir_path}")
    console.print(f"   • Files tracked: {len(files)}")


def check_integrity():
    baselines = list_baselines()
    if not baselines:
        console.print("[red]No baselines found. Create one first.[/red]")
        return

    console.print("\n[cyan]Available Baselines:[/cyan]")
    for i, name in enumerate(baselines, 1):
        console.print(f"{i}. {name}")

    choice = Prompt.ask("Choose baseline to check (or type 'all')", default="all")

    if choice.lower() == "all":
        for name in baselines:
            console.print(f"\n[bold]Checking: {name}[/bold]")
            check_single_baseline(name)
    else:
        try:
            idx = int(choice) - 1
            check_single_baseline(baselines[idx])
        except:
            console.print("[red]Invalid choice.[/red]")


def check_single_baseline(name: str):
    baseline_path = get_baseline_path(name)
    baseline_data = load_baseline(baseline_path)

    if not baseline_data:
        console.print(f"[red]Failed to load '{name}'.[/red]")
        return

    base_dir = Path(baseline_data["base_directory"])
    exclude_patterns = baseline_data.get("exclude_patterns", DEFAULT_EXCLUDE_PATTERNS)

    console.print(f"[cyan]Scanning: {base_dir}[/cyan]")
    current_files = scan_directory(base_dir, exclude_patterns)

    changes = compare_with_baseline(baseline_data, current_files)
    print_integrity_report(changes, name)

    report_path = generate_markdown_report(changes, base_dir, name)
    console.print(f"[green]Report saved: {report_path}[/green]")


def show_baseline_info():
    baselines = list_baselines()
    if not baselines:
        console.print("[yellow]No baselines found yet.[/yellow]")
        return

    console.print("\n[bold]Available Baselines:[/bold]")
    for i, name in enumerate(baselines, 1):
        console.print(f"{i}. {name}")

    choice = Prompt.ask("Which baseline do you want to see?", default="1")
    try:
        idx = int(choice) - 1
        name = baselines[idx]
        baseline_path = get_baseline_path(name)
        data = load_baseline(baseline_path)

        console.print(Panel(
            f"[bold]Baseline: {name}[/bold]\n"
            f"Directory     : {data.get('base_directory')}\n"
            f"Created       : {data.get('created_at')}\n"
            f"Files Tracked : {data.get('total_files', 0)}",
            title="📋 Baseline Details",
            border_style="blue"
        ))
    except:
        console.print("[red]Invalid choice.[/red]")


def manage_baselines():
    """Delete or reset baselines"""
    baselines = list_baselines()
    if not baselines:
        console.print("[yellow]No baselines to manage.[/yellow]")
        return

    console.print("\n[bold]Manage Baselines[/bold]")
    console.print("1. Delete specific baseline")
    console.print("2. Delete ALL baselines (Reset everything)")
    console.print("3. Back to main menu")

    choice = Prompt.ask("Enter choice", choices=["1", "2", "3"], default="3")

    if choice == "1":
        console.print("\nExisting baselines:")
        for i, name in enumerate(baselines, 1):
            console.print(f"{i}. {name}")

        try:
            idx = int(Prompt.ask("Enter number to delete")) - 1
            name = baselines[idx]
            confirm = Prompt.ask(f"Delete '{name}'? (yes/no)", default="no")
            if confirm.lower() == "yes":
                get_baseline_path(name).unlink(missing_ok=True)
                console.print(f"[green]✅ Baseline '{name}' deleted.[/green]")
        except:
            console.print("[red]Invalid choice.[/red]")

    elif choice == "2":
        confirm = Prompt.ask("[bold red]Delete ALL baselines? This cannot be undone! (yes/no)[/bold red]", default="no")
        if confirm.lower() == "yes":
            for name in baselines:
                get_baseline_path(name).unlink(missing_ok=True)
            console.print("[green]✅ All baselines have been deleted.[/green]")


if __name__ == "__main__":
    app()