import time
import json
import re
import sys
import io
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from agents import ScoutAgent
from rohan import AnalystAgent
from NetworkAnalystAgent import NetworkAnalystAgent


# Fix Unicode output encoding for Windows terminal
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


console = Console()

def extract_json_from_text(text):
    """
    Extract JSON string wrapped in `````` from Gemini markdown output.
    Returns JSON string or None if not found.
    """
    match = re.search(r"``````", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def print_analysis_tables(data):
    analysis = data.get("analysis", {})
    key_figures = data.get("key_figures_mentioned", {})
    market_impact_score = data.get("market_impact_score", "N/A")

    console.print("[bold underline]Analysis Summary[/bold underline]")
    summary_table = Table(show_header=False, box=None)
    summary_table.add_row("Company:", analysis.get("company_name", "N/A"))
    summary_table.add_row("Ticker:", analysis.get("ticker", "N/A"))
    summary_table.add_row("Summary:", analysis.get("summary", "N/A"))
    summary_table.add_row("Market Impact Score:", str(market_impact_score))
    console.print(summary_table)
    console.print()

    console.print("[bold underline]News Sentiment[/bold underline]")
    sentiment = analysis.get("news_sentiment", {})
    sentiment_table = Table(show_header=True, header_style="bold magenta")
    sentiment_table.add_column("Aspect", style="dim")
    sentiment_table.add_column("Description")
    sentiment_table.add_row("Direct Impact on JPM", sentiment.get("direct_impact_on_jpm", "N/A"))
    sentiment_table.add_row("Indirect Impact on JPM", sentiment.get("indirect_impact_on_jpm", "N/A"))
    console.print(sentiment_table)
    console.print()

    console.print("[bold underline]Market Data Summary[/bold underline]")
    console.print(analysis.get("market_data_summary", "N/A"))
    console.print()

    console.print("[bold underline]JPM Market Data[/bold underline]")
    jpm_data = key_figures.get("jpm_market_data", {})
    jpm_table = Table(show_header=True, header_style="bold cyan")
    jpm_table.add_column("Metric")
    jpm_table.add_column("Value")
    jpm_table.add_row("Current Price", f"${jpm_data.get('current_price', 'N/A')}")
    jpm_table.add_row("Price Change (24h)", f"${jpm_data.get('price_change_24h', 'N/A')}")
    jpm_table.add_row("Change Percent (24h)", jpm_data.get("change_percent_24h", "N/A"))
    console.print(jpm_table)
    console.print()

    console.print("[bold underline]Other Company Targets by JPMorgan Chase[/bold underline]")
    targets = key_figures.get("other_company_targets_by_jpm", [])
    if targets:
        targets_table = Table(show_header=True, header_style="bold green")
        targets_table.add_column("Company")
        targets_table.add_column("Rating")
        targets_table.add_column("Price Target")
        targets_table.add_column("Previous Price Target")
        for t in targets:
            company = t.get("company", "N/A")
            rating = t.get("rating", "N/A")
            price_target = str(t.get("price_objective") or t.get("price_target") or t.get("target_price") or "")
            previous_price = str(t.get("previous_price_target", ""))
            targets_table.add_row(company, rating, price_target, previous_price)
        console.print(targets_table)
    else:
        console.print("No targets data available.")

def main():
    scout_agent = ScoutAgent()
    analyst_agent = AnalystAgent()

    network_agent = NetworkAnalystAgent("bolt://localhost:7687", "neo4j", "password")

    company_name = "JPMorgan Chase"
    ticker = "JPM"

    console.print("[bold underline]Starting Market Analysis Loop[/bold underline]")

    try:
        while True:
            data_contract = scout_agent.run(company_name=company_name, ticker=ticker)

            if data_contract["news_articles"]:
                headline = data_contract["news_articles"][0].get("title", "No headline available")
            else:
                headline = "No news articles found"
            console.clear()
            console.print(f"[bold blue]Latest News Headline:[/bold blue] {headline}")

            analysis_text = analyst_agent.analyze_data_contract(data_contract)

            console.print("\n[bold yellow]Received AI analysis output:[/bold yellow]\n")
            console.print(analysis_text)

            raw_json_str = extract_json_from_text(analysis_text)
            if raw_json_str:
                try:
                    analysis_data = json.loads(raw_json_str)

                    if not analysis_data.get("institutions"):
                        console.print("[bold red]Warning: No institutions found in AI output.[/bold red]")
                    if not analysis_data.get("company_relationships"):
                        console.print("[bold red]Warning: No company relationships found in AI output.[/bold red]")

                    print_analysis_tables(analysis_data)

                    console.print("\n[bold green]Neo4j Graph Update Details:[/bold green]")
                    for inst in analysis_data.get("institutions", []):
                        console.print(f" - Institution node will be created: {inst.get('name')}")
                    for rel in analysis_data.get("company_relationships", []):
                        console.print(f" - Relationship: {rel.get('source')} -[{rel.get('type')}]-> {rel.get('target')}")

                    network_agent.process_analysis(raw_json_str)

                except json.JSONDecodeError:
                    console.print("[bold red]Failed to decode extracted JSON from AI output.[/bold red]")
                    console.print(Markdown(analysis_text))
            else:
                # If no embedded JSON block, just print raw Markdown analysis
                console.print(Markdown(analysis_text))

            time.sleep(15)

    except KeyboardInterrupt:
        console.print("\n[bold red]Exiting program...[/bold red]")
        network_agent.close()

if __name__ == "__main__":
    main()
