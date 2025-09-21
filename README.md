# Systemic Risk Sentinel

A comprehensive financial risk monitoring and analysis system that leverages AI agents to track company performance, assess systemic risks, and provide real-time insights through an interactive web interface.

## Overview

Systemic Risk Sentinel is a sophisticated financial intelligence platform that combines multiple AI agents to monitor companies, analyze market data, assess risks, and visualize financial relationships. The system uses Neo4j for graph database storage, FastAPI for the backend, and a modern web interface for visualization.

## Architecture

The system consists of several specialized AI agents working together:

### Core Components

  - **ScoutAgent** (`agents.py`) - Fetches real-time news and market data
  - **CROAgent** (`croagent.py`) - Chief Risk Officer agent for risk assessment and scenario simulation
  - **AnalystAgent** (`rohan.py`) - Analyzes financial data and generates insights
  - **NetworkAnalystAgent** (`NetworkAnalystAgent.py`) - Processes and stores relationship data in Neo4j
  - **DatabaseManager** (`database.py`) - Handles Neo4j database operations

### Backend & Frontend

  - **FastAPI Server** (`api.py`) - RESTful API providing endpoints for data access
  - **Web Interface** (`index.html` + `main.js`) - Interactive visualization dashboard
  - **Main Application** (`main.py`) - Entry point for the system

-----

## Features

### Real-time Monitoring

  - **News Aggregation**: Fetches latest news articles using NewsAPI
  - **Market Data**: Retrieves real-time stock prices and market metrics via Yahoo Finance
  - **Risk Assessment**: AI-powered analysis of news sentiment and market impact

### Risk Analysis

  - **Automated Risk Scoring**: Calculates risk scores (1-10) based on news and market data
  - **Company Condition Analysis**: Detailed AI-generated reports on company health
  - **Scenario Simulation**: Hypothetical scenario modeling for risk assessment

### Data Visualization

  - **Network Graph**: Interactive visualization of company relationships using Vis.js
  - **Real-time Updates**: Live data refresh for continuous monitoring
  - **Multi-panel Dashboard**: Comprehensive view of risk alerts, company conditions, and simulations

### Database Integration

  - **Neo4j Graph Database**: Stores company relationships and institutional connections
  - **Relationship Mapping**: Tracks competitor relationships, partnerships, and market connections

-----

## Installation

### Prerequisites

  - Python 3.8+
  - Neo4j Database (running on localhost:7687)
  - Required API keys (NewsAPI, Gemini AI)

### Setup

1.  **Clone the repository**

    ```bash
    git clone <repository-url>
    cd GDGHackathon
    ```

2.  **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Configuration**
    Create a `.env` file with your API keys:

    ```
    NEWS_API_KEY=your_newsapi_key
    GEMINI_API_KEY=your_gemini_api_key
    ```

4.  **Start Neo4j Database**

    ```bash
    # Using Docker
    docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
    ```

5.  **Run the application**

    ```bash
    # Start the FastAPI server
    uvicorn api:app --reload --host 0.0.0.0 --port 8000

    # In another terminal, run the monitoring system
    python vansh.py
    ```

6.  **Access the web interface**
    Open your browser and navigate to `http://localhost:8000` or open `index.html` directly.

-----

## Usage

### Web Interface

1.  **Graph Visualization**: View company relationships and institutional connections
2.  **Risk Alerts**: Monitor real-time risk assessments for companies
3.  **Company Analysis**: Get detailed condition reports with news and market data
4.  **Scenario Simulation**: Test hypothetical scenarios and their potential impacts

### Command Line Interface

Run the monitoring system:

```bash
python vansh.py
```

Enter the company name and ticker when prompted to start monitoring.

### API Endpoints

  - `GET /api/graph_data` - Retrieve network graph data
  - `GET /api/risk_alerts/{company}` - Get risk assessment for a company
  - `GET /api/company_condition/{company}` - Get detailed company analysis
  - `POST /api/simulate/{company}` - Run scenario simulation

-----

## Project Structure

```
GDGHackathon/
├── api.py                   # FastAPI server
├── agents.py                # ScoutAgent for data fetching
├── croagent.py              # CROAgent for risk analysis
├── database.py              # Neo4j database manager
├── index.html               # Web interface
├── main.js                  # Frontend JavaScript
├── main.py                  # Application entry point
├── NetworkAnalystAgent.py   # Network analysis agent
├── requirements.txt         # Python dependencies
├── rohan.py                 # AnalystAgent for data analysis
├── vansh.py                 # Main monitoring application
└── README.md                # This file
```

## Key Technologies

  - **Backend**: FastAPI, Python 3.8+
  - **Database**: Neo4j Graph Database
  - **AI/ML**: Google Gemini AI, Yahoo Finance API, NewsAPI
  - **Frontend**: HTML5, JavaScript, Vis.js
  - **Data Processing**: Pandas, NumPy
  - **Visualization**: Vis.js Network Graph

## Configuration

### API Keys Required

  - **NewsAPI**: For fetching news articles
  - **Gemini AI**: For natural language processing and analysis

### Database Configuration

  - **Neo4j URI**: `bolt://localhost:7687`
  - **Username**: `neo4j`
  - **Password**: `password`

## Contributing

1.  Fork the repository
2.  Create a feature branch
3.  Make your changes
4.  Add tests if applicable
5.  Submit a pull request

## License

This project is part of a hackathon submission and is available under standard open-source terms.

## Support

For issues and questions, please refer to the individual agent files or create an issue in the repository.

-----

**Note**: This system is designed for financial analysis and risk assessment. Always verify results with professional financial advice before making investment decisions.
