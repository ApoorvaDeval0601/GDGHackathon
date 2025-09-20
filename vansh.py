# main.py
import time
import json
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()

# Placeholder ScoutAgent
class ScoutAgent:
    def fetch_data(self):
        # Mock data - replace with real API data fetching later
        return {
            "headline": "Market Rally Today",
            "content": "Stocks surged with major gains in tech sector.",
            "timestamp": "2025-09-20T12:00:00Z"
        }

# Placeholder AnalystAgent
class AnalystAgent:
    def analyze(self, data):
        # Mock analysis - replace with Gemini prompt output later
        return {
            "summary": "Positive sentiment with potential growth.",
            "risk_level": "low",
            "market_impact_score": 7,
            "key_figures": {"Tech Growth": "5%"},
        }

def print_analysis_report(analysis):
    table = Table(title="Analysis Report")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    for key, value in analysis.items():
        if isinstance(value, dict):
            # Format nested dict nicely
            value_str = ", ".join(f"{k}: {v}" for k, v in value.items())
        else:
            value_str = str(value)
        table.add_row(key, value_str)

    # Color code the risk level
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

    console.print("[bold underline]Starting Market Analysis Loop[/bold underline]")

    try:
        while True:
            # Fetch data from ScoutAgent
            news_data = scout_agent.fetch_data()

            # Pass data to AnalystAgent to get analysis
            analysis = analyst_agent.analyze(news_data)

            # Clear screen and print fresh report
            console.clear()
            console.print(f"[bold blue]Latest News Headline:[/bold blue] {news_data['headline']}")
            print_analysis_report(analysis)

            # Sleep for demo pacing (e.g., 10 seconds)
            time.sleep(10)

    except KeyboardInterrupt:
        console.print("\n[bold red]Exiting program...[/bold red]")

if __name__ == "__main__":
    main()
