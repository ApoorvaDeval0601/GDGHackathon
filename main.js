// main.js

async function drawGraph() {
  try {
    console.log("Fetching graph data...");
    // This calls the backend API created by Person 1
    const response = await fetch('http://localhost:8000/api/graph_data');
    const data = await response.json();
    console.log("Data received:", data);

    const container = document.getElementById('mynetwork');

    const graphData = {
      nodes: new vis.DataSet(data.nodes),
      edges: new vis.DataSet(data.edges),
    };

    // Options for the graph visualization
    const options = {
      nodes: {
        shape: 'dot',
        size: 18,
        font: {
            size: 14,
            color: '#ffffff'
        },
        borderWidth: 2
      },
      edges: {
        width: 2,
        color: { inherit: 'from' },
        arrows: { to: { enabled: true, scaleFactor: 0.8 } },
        font: {
          color: '#ffffff',
          align: 'top'
        }
      },
      physics: {
        enabled: true,
        solver: 'barnesHut',
        barnesHut: {
          gravitationalConstant: -3000
        }
      },
    };

    // Initialize your network!
    const network = new vis.Network(container, graphData, options);

  } catch (error) {
    console.error("Failed to draw graph:", error);
    // You could display an error message on the page here
  }
}

// Initial draw when the page loads
drawGraph();

// Optional: Redraw the graph every 15 seconds to get live updates
setInterval(drawGraph, 15000);