# In agents.py

import os
import requests
import yfinance as yf  # <-- NEW IMPORT
from dotenv import load_dotenv

load_dotenv()

class ScoutAgent:
    def __init__(self):
        self.news_api_key = os.getenv("NEWS_API_KEY")
        # NOTE: We no longer need any other API keys

    def fetch_news(self, company_name: str):
        # This function for news remains the same
        print(f"Scout Agent: Fetching news for {company_name}...")
        url = (f"https://newsapi.org/v2/everything?qInTitle={company_name}&language=en&sortBy=publishedAt&pageSize=5&apiKey={self.news_api_key}")
        try:
            response = requests.get(url)
            response.raise_for_status()
            articles = response.json().get("articles", [])
            cleaned_articles = [{"source": a.get("source", {}).get("name"), "title": a.get("title"), "content": a.get("description") or a.get("content", "")} for a in articles]
            return cleaned_articles
        except requests.exceptions.RequestException as e:
            print(f"Scout Agent: Error fetching news: {e}")
            return []

    def fetch_market_data(self, ticker: str):
        # --- THIS IS THE NEW, MORE RELIABLE VERSION using yfinance ---
        print(f"Scout Agent: Fetching market data for {ticker} from yfinance...")
        try:
            stock = yf.Ticker(ticker)
            # Get the most recent trading day's data
            hist = stock.history(period="1d")

            if hist.empty:
                print(f"Scout Agent: No data found for ticker {ticker} using yfinance.")
                return None

            # Extract the latest price and calculate the change from the day's open
            last_price = hist['Close'].iloc[-1]
            day_open = hist['Open'].iloc[-1]
            change = last_price - day_open
            percent_change = (change / day_open) * 100

            market_data = {
                "current_price": round(last_price, 2),
                "price_change_24h": round(change, 2),
                "change_percent_24h": f"{round(percent_change, 2)}%"
            }
            return market_data

        except Exception as e:
            print(f"Scout Agent: Error fetching data from yfinance: {e}")
            return None
        # ----------------------------------------------------------------

    def run(self, company_name: str, ticker: str):
        news_articles = self.fetch_news(company_name)
        market_data = self.fetch_market_data(ticker)
        return {"company_name": company_name, "ticker": ticker, "news_articles": news_articles, "market_data": market_data}