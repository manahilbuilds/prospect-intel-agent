"""CLI entry point for prospect-intel-agent."""

import argparse
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.agent import analyze_prospect
from src.schemas import ProspectReport
from src.scraper import extract_domain, scrape_website

console = Console()


def render_report(report: ProspectReport, url: str) -> None:
    """Display the structured prospect brief in the terminal."""
    console.print()
    console.print(
        Panel.fit(
            f"[bold cyan]{report.company_name}[/bold cyan]  |  [green]{report.industry}[/green]\n"
            f"[dim]{url}[/dim]\n\n"
            f"[bold]Target Audience:[/bold] {report.target_audience}\n"
            f"[bold]Core Offer:[/bold] {report.core_offer}",
            title="Prospect Intelligence Brief",
            border_style="cyan",
        )
    )

    table = Table(title="Identified Automation Opportunities", show_lines=True)
    table.add_column("Pain Point", style="bold yellow", width=24)
    table.add_column("Evidence on Site", width=36)
    table.add_column("AI Automation Pitch", style="green", width=38)

    for item in report.likely_pain_points:
        table.add_row(item.title, item.evidence, item.automation_opportunity)

    console.print(table)
    console.print(
        Panel(
            report.cold_outreach_hook,
            title="Personalized Outreach Hook",
            border_style="green",
        )
    )


def save_report(report: ProspectReport, url: str, output_dir: Path) -> Path:
    """Save the structured report as a JSON file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    domain = extract_domain(url)
    output_path = output_dir / f"{domain}.json"
    output_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    return output_path


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Scrape a company URL and generate a structured AI prospect brief."
    )
    parser.add_argument("url", help="Target company website URL (e.g. https://stripe.com)")
    parser.add_argument(
        "--model",
        default="gemini-3.8-flash",
        help="Gemini model to use (default: gemini-3.8-flash)",
    )
    args = parser.parse_args()

    with console.status(f"[bold cyan]Scraping {args.url}..."):
        scraped = scrape_website(args.url)

    with console.status(f"[bold green]Analyzing with {args.model}..."):
        report = analyze_prospect(scraped, model=args.model)

    render_report(report, scraped["url"])

    saved_path = save_report(report, scraped["url"], Path("outputs"))
    console.print(f"\n[dim]Saved structured JSON report to:[/dim] [bold]{saved_path}[/bold]")


if __name__ == "__main__":
    main()
