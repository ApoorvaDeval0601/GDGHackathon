# croagent.py
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
 
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file.")
genai.configure(api_key=API_KEY)
 
class CROAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
 
    def assess_risk(self, company_data: dict) -> dict:
        company_name = company_data.get("company_name", "N/A")
        news = company_data.get("news_articles", [])
        market_data = company_data.get("market_data", {})
        risk_score = 0
        summary = "No significant risk detected."
 
        if news:
            headline = news[0].get("title", "").lower()
            if any(word in headline for word in ["crash", "downfall", "lawsuit", "scandal", "loss"]):
                risk_score = 8
                summary = f"High risk detected due to headline: {headline}"
            elif any(word in headline for word in ["drop", "decline", "warning"]):
                risk_score = 5
                summary = f"Medium risk detected due to headline: {headline}"
            else:
                risk_score = 2
                summary = f"Low risk. Latest news headline: {headline}"
 
        if market_data:
            change_percent = market_data.get("change_percent_24h")
            if change_percent and "%" in str(change_percent):
                try:
                    percent = float(change_percent.replace("%", ""))
                    if percent < -5:
                        risk_score = max(risk_score, 9)
                        summary += " Market shows significant downward movement."
                    elif percent < -2:
                        risk_score = max(risk_score, 6)
                        summary += " Market shows moderate decline."
                except ValueError:
                    pass
        return {"company": company_name, "risk_score": risk_score, "summary": summary}
 
    def analyze_company_condition(self, company_data: dict) -> dict:
        try:
            prompt = f"""
            You are a financial risk AI. Analyze the following company information and
            give a concise JSON object with: overall_condition, impact_analysis, and recommendations.
 
            Company data:
            {json.dumps(company_data, indent=2)}
            """
            response = self.model.generate_content(prompt)
            text = response.text
            start_index = text.find("{")
            end_index = text.rfind("}")
            if start_index != -1 and end_index != -1:
                json_str = text[start_index:end_index+1]
                return json.loads(json_str)
            else:
                return {"error": "Could not parse Gemini response."}
        except Exception as e:
            return {"error": f"Gemini API error: {e}"}
 
    def simulate_scenario(self, company_name: str, scenario: str) -> dict:
        try:
            prompt = f"""
            You are a financial risk AI. A scenario is being simulated for {company_name}:
 
            Scenario: {scenario}
 
            Using current market trends and historical data, provide a JSON object with:
            predicted_risk_score (1-10), potential_impact, and suggested_actions.
            """
            response = self.model.generate_content(prompt)
            text = response.text
            start_index = text.find("{")
            end_index = text.rfind("}")
            if start_index != -1 and end_index != -1:
                json_str = text[start_index:end_index+1]
                return json.loads(json_str)
            else:
                return {"error": "Could not parse Gemini response for scenario."}
        except Exception as e:
            return {"error": f"Gemini API error: {e}"}