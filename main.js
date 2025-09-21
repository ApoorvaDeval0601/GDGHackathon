// main.js

const DEFAULT_COMPANY = "Microsoft"; // default company
let currentCompany = DEFAULT_COMPANY;

// ---------- GRAPH DRAWING ----------
async function drawGraph() {
  try {
    console.log("Fetching graph data...");
    const response = await fetch('http://localhost:8000/api/graph_data');
    const data = await response.json();
    console.log("Graph data received:", data);

    const container = document.getElementById('mynetwork');

    const graphData = {
      nodes: new vis.DataSet(data.nodes),
      edges: new vis.DataSet(data.edges),
    };

    const options = {
      nodes: {
        shape: 'dot',
        size: 18,
        font: { size: 14, color: '#ffffff' },
        borderWidth: 2
      },
      edges: {
        width: 2,
        color: { inherit: 'from' },
        arrows: { to: { enabled: true, scaleFactor: 0.8 } },
        font: { color: '#ffffff', align: 'top' }
      },
      physics: {
        enabled: true,
        solver: 'barnesHut',
        barnesHut: { gravitationalConstant: -3000 }
      },
    };

    new vis.Network(container, graphData, options);

  } catch (error) {
    console.error("Failed to draw graph:", error);
  }
}

// ---------- CRO ALERTS ----------
async function fetchRiskAlerts() {
  try {
    const response = await fetch("/api/risk_alerts");
    const data = await response.json();
    document.getElementById("cro-text").innerText = JSON.stringify(data.risk_report, null, 2);
  } catch (error) {
    console.error("Failed to fetch CRO alerts:", error);
  }
}

// ---------- COMPANY CONDITION ----------
async function fetchCompanyCondition(company) {
  try {
    const response = await fetch(`/api/company_condition/${company}`);
    const data = await response.json();

    currentCompany = company; // update current company

    document.getElementById("company-name").innerText = data.company;

    // News
    const newsElem = document.getElementById("company-news");
    newsElem.innerHTML = "";
    if (Array.isArray(data.news)) {
      data.news.forEach(article => {
        const div = document.createElement("div");
        div.innerHTML = `<b>${article.title}</b> - ${article.source}<br>${article.content || ""}<hr>`;
        newsElem.appendChild(div);
      });
    } else {
      newsElem.innerText = "No news available.";
    }

    // Market data
    const marketElem = document.getElementById("company-market");
    const md = data.market_data || {};
    marketElem.innerHTML = `
      Current Price: $${md.current_price || "N/A"} <br>
      Change (24h): $${md.price_change_24h || "N/A"} (${md.change_percent_24h || "N/A"})
    `;

    // Gemini analysis / report
    document.getElementById("company-report").innerText = data.report || "No report available.";

  } catch (error) {
    console.error(`Failed to fetch condition for ${company}:`, error);
  }
}

// ---------- SIMULATION ----------
async function runSimulation() {
  try {
    const scenario = document.getElementById("scenario-input").value;
    const company = currentCompany;

    const response = await fetch(`/api/simulate/${company}`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({scenario})
    });
    const data = await response.json();

    document.getElementById("simulation-result").innerText = JSON.stringify(data.simulation, null, 2);

  } catch (error) {
    console.error("Simulation failed:", error);
  }
}

// ---------- INITIALIZATION ----------
document.addEventListener("DOMContentLoaded", () => {
  // Initial graph and data load
  drawGraph();
  fetchRiskAlerts();
  fetchCompanyCondition(DEFAULT_COMPANY);

  // Auto-refresh intervals
  setInterval(drawGraph, 15000);           // Graph every 15s
  setInterval(fetchRiskAlerts, 60000);     // CRO alerts every 60s
  setInterval(() => fetchCompanyCondition(currentCompany), 15000); // Company condition every 15s
});
