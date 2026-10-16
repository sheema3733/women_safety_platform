// Analytics Charts using Chart.js with Approved Palette

function initAnalyticsCharts(data) {
  if (!window.Chart) return;

  // 1. SOS Status Doughnut Chart
  const sosCtx = document.getElementById("chart-sos-status");
  if (sosCtx && data.sos_status) {
    new Chart(sosCtx, {
      type: "doughnut",
      data: {
        labels: data.sos_status.labels,
        datasets: [{
          data: data.sos_status.data,
          backgroundColor: data.sos_status.colors,
          borderWidth: 2,
          borderColor: "#FFFFFF"
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: "bottom" }
        }
      }
    });
  }

  // 2. Incident Category Bar Chart
  const incCatCtx = document.getElementById("chart-incident-category");
  if (incCatCtx && data.incident_category) {
    new Chart(incCatCtx, {
      type: "bar",
      data: {
        labels: data.incident_category.labels,
        datasets: [{
          label: "Incident Count",
          data: data.incident_category.data,
          backgroundColor: data.incident_category.colors,
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: { beginAtZero: true, ticks: { precision: 0 } }
        }
      }
    });
  }

  // 3. Incident Severity Doughnut Chart
  const incSevCtx = document.getElementById("chart-incident-severity");
  if (incSevCtx && data.incident_severity) {
    new Chart(incSevCtx, {
      type: "pie",
      data: {
        labels: data.incident_severity.labels,
        datasets: [{
          data: data.incident_severity.data,
          backgroundColor: data.incident_severity.colors,
          borderWidth: 2,
          borderColor: "#FFFFFF"
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: "bottom" }
        }
      }
    });
  }

  // 4. Resources by Category
  const resCatCtx = document.getElementById("chart-resource-category");
  if (resCatCtx && data.resource_category) {
    new Chart(resCatCtx, {
      type: "bar",
      data: {
        labels: data.resource_category.labels,
        datasets: [{
          label: "Resources Registered",
          data: data.resource_category.data,
          backgroundColor: "#734B6D",
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, ticks: { precision: 0 } }
        }
      }
    });
  }
}
