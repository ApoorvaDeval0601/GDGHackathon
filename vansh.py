import time
import json
from rich.console import Console
from rich.markdown import Markdown
from agents import ScoutAgent
from rohan import AnalystAgent


console = Console()


def format_nested_output(data, indent=0):
    """
    Recursively format any nested dict or list into indented paragraphs and bullet points.
    """
    indent_str = "  " * indent
    output_lines = []
    if isinstance(data, dict):
        for key, value in data.items():
            heading = f"{indent_str}**{key.replace('_', ' ').title()}**"
            if isinstance(value, (dict, list)):
                output_lines.append(heading + ":")
                output_lines.append(format_nested_output(value, indent + 1))
            else:
                output_lines.append(f"{heading}: {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data, 1):
            if isinstance(item, (dict, list)):
                output_lines.append(f"{indent_str}- Item {i}:")
                output_lines.append(format_nested_output(item, indent + 1))
            else:
                output_lines.append(f"{indent_str}- {item}")
    else:
        output_lines.append(f"{indent_str}{data}")
    return "\n".join(output_lines)


def print_any_output(data):
    """
    Print any JSON-like data with rich Markdown formatting and indentation.
    """
    formatted_text = format_nested_output(data)
    console.print(Markdown(formatted_text))


def main():
    scout_agent = ScoutAgent()
    analyst_agent = AnalystAgent()

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

            # Get textual Gemini response
            analysis_text = analyst_agent.analyze_data_contract(data_contract)

            # Display Gemini's textual Markdown response directly
            console.print(Markdown(analysis_text))

            time.sleep(15)

    except KeyboardInterrupt:
        console.print("\n[bold red]Exiting program...[/bold red]")


if __name__ == "__main__":
    main()
