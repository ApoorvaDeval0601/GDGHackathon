// main.js
const DEFAULT_COMPANY = "Microsoft";
let currentCompany = DEFAULT_COMPANY;
 
// --- Draw Graph ---
async function drawGraph() {
  try {
    const response = await fetch('http://localhost:8000/api/graph_data');
    const data = await response.json();
    const container = document.getElementById('mynetwork');
 
    const graphData = {
      nodes: new vis.DataSet(data.nodes),
      edges: new vis.DataSet(data.edges),
    };
 
    const options = {
      nodes: { shape: 'dot', size: 18, font: { size: 14, color: '#ffffff' }, borderWidth: 2 },
      edges: { width: 2, color: { inherit: 'from' }, arrows: { to: { enabled: true, scaleFactor: 0.8 } }, font: { color: '#ffffff', align: 'top' } },
      physics: { enabled: true, solver: 'barnesHut', barnesHut: { gravitationalConstant: -3000 } },
    };
    new vis.Network(container, graphData, options);
  } catch (error) {
    console.error("Failed to draw graph:", error);
  }
}
 
// --- Fetch Risk Alerts ---
async function fetchRiskAlerts() {
  try {
    const response = await fetch(`http://localhost:8000/api/risk_alerts/${currentCompany}`);
    const data = await response.json();
    document.getElementById("risk-alerts").value = JSON.stringify(data.risk_report, null, 2);
  } catch (error) {
    console.error("Failed to fetch CRO alerts:", error);
  }
}
 
// --- Fetch Company Condition ---
async function fetchCompanyCondition(company) {
  try {
    const response = await fetch(`http://localhost:8000/api/company_condition/${company}`);
    const data = await response.json();
    currentCompany = company;
 
    document.getElementById("company-name").innerText = data.company;
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
 
    const marketElem = document.getElementById("company-market");
    const md = data.market_data || {};
    marketElem.innerHTML = `
      Current Price: $${md.current_price || "N/A"} <br>
      Change (24h): $${md.price_change_24h || "N/A"} (${md.change_percent_24h || "N/A"})
    `;
 
    document.getElementById("company-report").innerText = data.report ? JSON.stringify(data.report, null, 2) : "No report available.";
  } catch (error) {
    console.error(`Failed to fetch condition for ${company}:`, error);
  }
}
 
// --- Run Simulation ---
async function runSimulation() {
  try {
    const scenario = document.getElementById("scenario-input").value;
    const company = currentCompany;
    if (!scenario) return alert("Please enter a scenario!");
 
    const response = await fetch(`http://localhost:8000/api/simulate/${company}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario: scenario })
    });
    const data = await response.json();
    document.getElementById("simulation-result").innerText = JSON.stringify(data.simulation, null, 2);
  } catch (error) {
    console.error("Simulation failed:", error);
  }
}
 
// --- INITIALIZATION ---
document.addEventListener("DOMContentLoaded", () => {
    drawGraph();
    fetchRiskAlerts();
    fetchCompanyCondition(DEFAULT_COMPANY);
 
    setInterval(drawGraph, 15000);
    setInterval(fetchRiskAlerts, 60000);
    setInterval(() => fetchCompanyCondition(currentCompany), 15000);
});