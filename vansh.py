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
from database import DatabaseManager


# Fix Unicode output encoding for Windows terminal
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


console = Console()

# In main.py, replace the old function with this one.

import re # Make sure 'import re' is at the top of your file

def extract_json_from_text(text: str):
    """
    Finds and extracts the first valid JSON object from a string.
    It looks for the text between the first '{' and the last '}'.
    """
    try:
        # Find the starting position of the first open curly brace
        start_index = text.find('{')
        # Find the starting position of the last closing curly brace
        end_index = text.rfind('}')
        
        if start_index != -1 and end_index != -1 and end_index > start_index:
            # Extract the substring that should be the JSON
            json_str = text[start_index:end_index+1]
            # Try to parse it to confirm it's valid JSON
            json.loads(json_str)
            return json_str
    except (json.JSONDecodeError, IndexError):
        # If parsing fails or indices are wrong, it's not valid
        return None
    
    return None # Return None if no valid JSON object is found

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

# In your main.py file

def main():
    # (Your agent initializations remain the same)
    scout_agent = ScoutAgent()
    analyst_agent = AnalystAgent()
    db_manager = DatabaseManager("bolt://localhost:7687", "neo4j", "password")
    network_agent = NetworkAnalystAgent(db_manager)

    company_name = "JPMorgan Chase"
    ticker = "JPM"
    console.print("[bold underline]Starting Market Analysis Loop[/bold underline]")

    try:
        while True:
            data_contract = scout_agent.run(company_name=company_name, ticker=ticker)

            if not data_contract or not data_contract.get("news_articles"):
                print("No articles found, waiting...")
                time.sleep(60)
                continue
            
            headline = data_contract["news_articles"][0].get("title", "No headline available")
            console.clear()
            console.print(f"[bold blue]Latest News Headline:[/bold blue] {headline}")

            analysis_text = analyst_agent.analyze_data_contract(data_contract)
            
            analysis_data = None
            try:
                # First, try to parse the entire text as JSON
                analysis_data = json.loads(analysis_text)
            except json.JSONDecodeError:
                # If that fails, try to extract JSON from backticks
                print("Initial parse failed, attempting to extract JSON block...")
                json_str = extract_json_from_text(analysis_text)
                if json_str:
                    try:
                        analysis_data = json.loads(json_str)
                    except json.JSONDecodeError:
                        print("[bold red]Error: Failed to parse the extracted JSON block.[/bold red]")

            # If we successfully got data one way or another, process it
            if analysis_data:
                print_analysis_tables(analysis_data)
                network_agent.process_and_store(analysis_data, company_name)
            else:
                # Fallback if no valid JSON could be found
                console.print("[bold red]Error: Could not find valid JSON in AI response.[/bold red]")
                console.print(Markdown(analysis_text))

            time.sleep(15)

    except KeyboardInterrupt:
        console.print("\n[bold red]Exiting program...[/bold red]")
        db_manager.close()
        
if __name__ == "__main__":
    main()
