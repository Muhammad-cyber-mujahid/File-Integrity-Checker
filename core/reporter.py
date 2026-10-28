from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table

console = Console()

def print_integrity_report(changes: dict, baseline_name: str = ""):
    console.print(f"\n[bold cyan]🔍 Integrity Check Results - {baseline_name}[/bold cyan]\n")

    total_changes = len(changes["new"]) + len(changes["modified"]) + len(changes["deleted"])

    if total_changes == 0:
        console.print("[bold green]✅ No changes detected. All files are intact.[/bold green]")
        return

    summary_table = Table(title="Summary")
    summary_table.add_column("Status", style="cyan")
    summary_table.add_column("Count", justify="right", style="bold")

    summary_table.add_row("🟢 Unchanged", str(changes["unchanged"]), style="green")
    summary_table.add_row("🟡 New", str(len(changes["new"])), style="yellow")
    summary_table.add_row("🔴 Modified", str(len(changes["modified"])), style="red")
    summary_table.add_row("🟡 Deleted", str(len(changes["deleted"])), style="yellow")

    console.print(summary_table)

    if changes["modified"]:
        console.print("\n[bold red]🔴 Modified Files:[/bold red]")
        for item in changes["modified"]:
            console.print(f"   • [red]{item['path']}[/red]")
            console.print(f"     Summary: {item.get('summary', 'File changed')}")
            console.print("")

    if changes["new"]:
        console.print("\n[bold yellow]🟡 New Files:[/bold yellow]")
        for item in changes["new"]:
            console.print(f"   • [yellow]{item['path']}[/yellow]")

    if changes["deleted"]:
        console.print("\n[bold yellow]🟡 Deleted Files:[/bold yellow]")
        for item in changes["deleted"]:
            console.print(f"   • [yellow]{item['path']}[/yellow]")


def generate_markdown_report(changes: dict, base_dir: Path, baseline_name: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = Path("reports") / f"integrity_report_{baseline_name}_{timestamp}.md"
    report_path.parent.mkdir(exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Integrity Report - {baseline_name}\n\n")
        f.write(f"**Scan Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Base Directory:** {base_dir}\n\n")

        total_changes = len(changes["new"]) + len(changes["modified"]) + len(changes["deleted"])

        if total_changes == 0:
            f.write("## ✅ No Changes Detected\n")
        else:
            f.write("## Summary\n")
            f.write(f"- Unchanged: {changes['unchanged']}\n")
            f.write(f"- New: {len(changes['new'])}\n")
            f.write(f"- Modified: {len(changes['modified'])}\n")
            f.write(f"- Deleted: {len(changes['deleted'])}\n\n")

            if changes["modified"]:
                f.write("## 🔴 Modified Files\n")
                for item in changes["modified"]:
                    f.write(f"- **{item['path']}**\n")
                    f.write(f"  - {item.get('summary', 'File changed')}\n\n")

            if changes["new"]:
                f.write("## 🟡 New Files\n")
                for item in changes["new"]:
                    f.write(f"- {item['path']}\n")

            if changes["deleted"]:
                f.write("## 🟡 Deleted Files\n")
                for item in changes["deleted"]:
                    f.write(f"- {item['path']}\n")

    return report_path