# In your rohan.py file

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file.")
genai.configure(api_key=API_KEY)

class AnalystAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze_data_contract(self, data_contract: dict) -> str:
        print("Analyst Agent: Analyzing data contract with master prompt...")
        
        # This master prompt forces the AI to be much more reliable.
        prompt = f"""
        You are a financial analysis AI. Your sole job is to return a single, clean JSON object with no extra text, explanations, or markdown.

        Analyze the provided data contract for {data_contract.get('company_name', 'the company')} and populate the following JSON schema.
        The "relationships" list should contain any financial connections found in the news. If none are found, return an empty list [].

        JSON SCHEMA:
        {{
            "analysis": {{
                "company_name": "{data_contract.get('company_name', 'N/A')}",
                "ticker": "{data_contract.get('ticker', 'N/A')}",
                "summary": "A concise one to two-sentence summary of the most critical news.",
                "news_sentiment": {{
                    "direct_impact_on_jpm": "Analyze the direct impact of the news on the company.",
                    "indirect_impact_on_jpm": "Analyze any indirect or broader market impacts."
                }},
                "market_data_summary": "A brief summary of the provided market data."
            }},
            "key_figures_mentioned": {{
                "jpm_market_data": {json.dumps(data_contract.get('market_data'))},
                "other_company_targets_by_jpm": []
            }},
            "relationships": [
                {{
                    "source_entity": "The company initiating an action",
                    "target_entity": "The company being acted upon",
                    "relationship_type": "The type of relationship (e.g., acquired, invested in)"
                }}
            ],
            "market_impact_score": "A numerical score from 1 (low impact) to 10 (high impact) based on the news."
        }}

        ---
        DATA CONTRACT TO ANALYZE:
        {json.dumps(data_contract, indent=2)}
        ---
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Analyst Agent: An error occurred during Gemini API call: {e}")
            return "{{}}"