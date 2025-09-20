import time
import json
import re
import sys
import io
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

# --- Agent and Database Imports ---
# Make sure your file names match your project structure
from agents import ScoutAgent
from rohan import AnalystAgent
from NetworkAnalystAgent import NetworkAnalystAgent
from database import DatabaseManager

# Fix for potential Unicode output errors on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

console = Console()

def extract_json_from_text(text: str):
    """
    Finds and extracts the first valid JSON object from a string.
    """
    try:
        start_index = text.find('{')
        end_index = text.rfind('}')
        if start_index != -1 and end_index != -1 and end_index > start_index:
            json_str = text[start_index:end_index+1]
            json.loads(json_str)
            return json_str
    except (json.JSONDecodeError, IndexError):
        return None
    return None

def print_analysis_tables(data):
    """
    The robust version of your display function.
    """
    analysis = data.get("analysis", {})
    key_figures = data.get("key_figures_mentioned") or {}
    market_impact_score = data.get("market_impact_score", "N/A")

    # Summary Table
    console.print("[bold underline]Analysis Summary[/bold underline]")
    summary_table = Table(show_header=False, box=None)
    summary_table.add_row("Company:", analysis.get("company_name", "N/A"))
    summary_table.add_row("Ticker:", analysis.get("ticker", "N/A"))
    summary_table.add_row("Summary:", analysis.get("summary", "N/A"))
    summary_table.add_row("Market Impact Score:", str(market_impact_score))
    console.print(summary_table)
    console.print()

    # News Sentiment Table
    console.print("[bold underline]News Sentiment[/bold underline]")
    sentiment = analysis.get("news_sentiment", {})
    sentiment_table = Table(show_header=True, header_style="bold magenta")
    sentiment_table.add_column("Aspect", style="dim")
    sentiment_table.add_column("Description")
    sentiment_table.add_row("Direct Impact", sentiment.get("direct_impact_on_jpm", "N/A"))
    sentiment_table.add_row("Indirect Impact", sentiment.get("indirect_impact_on_jpm", "N/A"))
    console.print(sentiment_table)
    console.print()

    # Market data summary
    console.print("[bold underline]Market Data Summary[/bold underline]")
    console.print(analysis.get("market_data_summary", "N/A"))
    console.print()

    # JPM Market Data Table
    console.print("[bold underline]Market Data[/bold underline]")
    jpm_data = key_figures.get("jpm_market_data") or {}
    jpm_table = Table(show_header=True, header_style="bold cyan")
    jpm_table.add_column("Metric")
    jpm_table.add_column("Value")
    jpm_table.add_row("Current Price", f"${jpm_data.get('current_price', 'N/A')}")
    jpm_table.add_row("Price Change (24h)", f"${jpm_data.get('price_change_24h', 'N/A')}")
    jpm_table.add_row("Change Percent (24h)", jpm_data.get("change_percent_24h", "N/A"))
    console.print(jpm_table)
    console.print()

    # Other Company Targets Table
    console.print("[bold underline]Other Company Targets Mentioned[/bold underline]")
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
        console.print("No other targets data available in this analysis.")


def main():
    # --- Initialize all agents and the database manager ---
    scout_agent = ScoutAgent()
    analyst_agent = AnalystAgent()
    db_manager = DatabaseManager("bolt://localhost:7687", "neo4j", "password")
    network_agent = NetworkAnalystAgent(db_manager)

    # --- Ask the user for input at the start ---
    company_name = input("Enter the full company name to monitor (e.g., Microsoft): ")
    ticker = input(f"Enter the stock ticker for {company_name} (e.g., MSFT): ")
    # -------------------------------------------

    console.print(f"[bold underline]Starting Market Analysis Loop for {company_name}[/bold underline]")

    try:
        while True:
            # Step 1: Scout fetches raw data
            data_contract = scout_agent.run(company_name=company_name, ticker=ticker)

            if not data_contract or not data_contract.get("news_articles"):
                print(f"No new articles found for {company_name}, waiting...")
                time.sleep(60)
                continue
            
            headline = data_contract["news_articles"][0].get("title", "No headline available")
            console.clear()
            console.print(f"[bold blue]Latest News Headline for {company_name}:[/bold blue] {headline}")

            # Step 2: Analyst processes data with Gemini
            analysis_text = analyst_agent.analyze_data_contract(data_contract)

            # Step 3: Parse the AI's response and process it
            analysis_data = None
            try:
                analysis_data = json.loads(analysis_text)
            except json.JSONDecodeError:
                json_str = extract_json_from_text(analysis_text)
                if json_str:
                    try:
                        analysis_data = json.loads(json_str)
                    except json.JSONDecodeError:
                        pass 

            if analysis_data:
                print_analysis_tables(analysis_data)
                network_agent.process_and_store(analysis_data, company_name)
            else:
                console.print("[bold red]Error: Could not find valid JSON in AI response.[/bold red]")
                console.print(Markdown(analysis_text))

            print("\n" + "="*80 + "\n")
            time.sleep(61)

    except KeyboardInterrupt:
        console.print("\n[bold red]Exiting program...[/bold red]")
        db_manager.close()


if __name__ == "__main__":
    main()