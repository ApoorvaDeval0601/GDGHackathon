import time
import json
from rich.console import Console
from rich.table import Table
from rich.text import Text
from agents import ScoutAgent
from rohan import AnalystAgent


console = Console()


def print_analysis_report(analysis_json_str):
    """
    Parse the JSON analysis response string from AnalystAgent and print a rich table.
    """
    try:
        analysis = json.loads(analysis_json_str)
    except json.JSONDecodeError:
        console.print("[bold red]Error parsing analysis JSON[/bold red]")
        console.print(analysis_json_str)
        return

    table = Table(title="Analysis Report")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    for key, value in analysis.items():
        if isinstance(value, dict):
            value_str = ", ".join(f"{k}: {v}" for k, v in value.items())
        else:
            value_str = str(value)
        table.add_row(key, value_str)

    # Color code risk level if present
    risk = analysis.get("risk_level", "").lower()
    if risk == "high":
        console.print(table, style="bold red")
    elif risk == "medium":
        console.print(table, style="yellow")
    else:
        console.print(table, style="green")


def main():
    scout_agent = ScoutAgent()
    analyst_agent = AnalystAgent()

    # Company details for example
    company_name = "JPMorgan Chase"
    ticker = "JPM"

    console.print("[bold underline]Starting Market Analysis Loop[/bold underline]")

    try:
        while True:
            # Fetch structured data from ScoutAgent according to data contract
            data_contract = scout_agent.run(company_name=company_name, ticker=ticker)

            # Print latest news headline for quick context
            if data_contract["news_articles"]:
                headline = data_contract["news_articles"][0].get("title", "No headline available")
            else:
                headline = "No news articles found"
            console.clear()
            console.print(f"[bold blue]Latest News Headline:[/bold blue] {headline}")

            # Send structured data contract to AnalystAgent for JSON analysis
            analysis_json_str = analyst_agent.analyze_data_contract(data_contract)

            # Print rich-formatted analysis report
            print_analysis_report(analysis_json_str)

            # Sleep to pace the demo (e.g., 15 sec)
            time.sleep(15)

    except KeyboardInterrupt:
        console.print("\n[bold red]Exiting program...[/bold red]")


if __name__ == "__main__":
    main()
