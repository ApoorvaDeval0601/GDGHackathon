# agents.py

import os
import requests
import json
from dotenv import load_dotenv

# This loads the variables from your .env file
load_dotenv()

class ScoutAgent:
    """
    This agent is responsible for fetching raw data from external APIs.
    """
    def __init__(self):
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")

    def fetch_news(self, company_name: str):
        """Fetches and cleans recent news articles for a given company."""
        print(f"Scout Agent: Fetching news for {company_name}...")
        url = (f"https://newsapi.org/v2/everything?"
               f"qInTitle={company_name}&"  # Searching in title for more relevance
               f"language=en&"
               f"sortBy=publishedAt&"
               f"pageSize=5&" # Limit to 5 articles
               f"apiKey={self.news_api_key}")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            articles = response.json().get("articles", [])
            
            # Clean the articles to only include the data we need
            cleaned_articles = []
            for article in articles:
                cleaned_articles.append({
                    "source": article.get("source", {}).get("name"),
                    "title": article.get("title"),
                    "content": article.get("description") or article.get("content", "")
                })
            return cleaned_articles
            
        except requests.exceptions.RequestException as e:
            print(f"Scout Agent: Error fetching news: {e}")
            return []

    def fetch_market_data(self, ticker: str):
        """Fetches the latest stock price and change for a given ticker."""
        print(f"Scout Agent: Fetching market data for {ticker}...")
        url = (f"https://www.alphavantage.co/query?"
               f"function=GLOBAL_QUOTE&"
               f"symbol={ticker}&"
               f"apikey={self.alpha_vantage_key}")

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json().get("Global Quote", {})
            
            if not data:
                print("Scout Agent: Market data not found for ticker.")
                return None
                
            # Clean the market data into a more user-friendly format
            market_data = {
                "current_price": float(data.get("05. price", 0)),
                "price_change_24h": float(data.get("09. change", 0)),
                "change_percent_24h": data.get("10. change percent", "0.0%")
            }
            return market_data
            
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"Scout Agent: Error fetching market data: {e}")
            return None

    def run(self, company_name: str, ticker: str):
        """Runs all fetching tasks and combines the data into the final contract."""
        news_articles = self.fetch_news(company_name)
        market_data = self.fetch_market_data(ticker)

        # Assemble the final data object according to the contract
        final_data_object = {
            "company_name": company_name,
            "ticker": ticker,
            "news_articles": news_articles,
            "market_data": market_data
        }
        
        print("Scout Agent: Data fetching complete.")
        return final_data_object

# --- How to Test Your Agent ---
# You can run this file directly to test your ScoutAgent independently.
if __name__ == '__main__':
    # Initialize your agent
    scout = ScoutAgent()
    
    # Run the agent for your target company
    jpmorgan_data = scout.run(company_name="JPMorgan Chase", ticker="JPM")
    
    # Pretty-print the final result to see if it works
    if jpmorgan_data:
        print("\n--- SCOUT AGENT TEST RESULT ---")
        print(json.dumps(jpmorgan_data, indent=2))
        print("----------------------------")