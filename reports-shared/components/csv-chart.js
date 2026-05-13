// <csv-chart src="data/gsc-trend.csv" type="line"
//            x="month" y="clicks,impressions"
//            title="Clicks vs impressions"
//            height="320"></csv-chart>
//
// - type: "line" | "bar" | "pie" | "doughnut"
// - x: column name for the x-axis labels
// - y: comma-separated column names for the series
// - colors: optional comma-separated hex list (defaults to a built-in palette)
// - height: chart height in px (default 280)

const PALETTE = ['#F28C28', '#2563eb', '#0a6e3e', '#7a4eb8', '#C0392B', '#0078d4', '#5E8E3E', '#274b6e'];

class CsvChart extends HTMLElement {
  connectedCallback() {
    const src = this.getAttribute('src');
    const type = this.getAttribute('type') || 'line';
    const xCol = this.getAttribute('x') || '';
    const yCols = (this.getAttribute('y') || '').split(',').map(s => s.trim()).filter(Boolean);
    const title = this.getAttribute('title') || '';
    const height = this.getAttribute('height') || '280';
    const colors = (this.getAttribute('colors') || '').split(',').map(s => s.trim()).filter(Boolean);

    if (!src || !xCol || !yCols.length) {
      window.renderNoData(this, 'csv-chart needs src, x, and y attributes.');
      return;
    }

    this.classList.add('chart-wrap');
    this.innerHTML = `
      ${title ? `<div style="font-size:13px;font-weight:700;color:var(--ink);margin-bottom:8px;">${esc(title)}</div>` : ''}
      <div class="chart-canvas-box" style="height:${parseInt(height, 10)}px;"><canvas></canvas></div>
    `;
    const canvas = this.querySelector('canvas');

    Promise.all([window.loadCSV(src), waitForChart()]).then(([data]) => {
      if (!data || !data.rows.length) { window.renderNoData(this); return; }
      const labels = data.rows.map(r => r[xCol]);
      const palette = colors.length ? colors : PALETTE;
      const isPie = type === 'pie' || type === 'doughnut';
      const datasets = yCols.map((c, i) => ({
        label: c,
        data: data.rows.map(r => parseFloat(String(r[c]).replace(/[^0-9.\-]/g, '')) || 0),
        backgroundColor: isPie
          ? data.rows.map((_, j) => palette[j % palette.length])
          : palette[i % palette.length] + (type === 'bar' ? 'cc' : '33'),
        borderColor: palette[i % palette.length],
        borderWidth: 2,
        tension: 0.3,
        fill: type === 'line'
      }));
      new window.Chart(canvas, {
        type: type,
        data: { labels: labels, datasets: datasets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: yCols.length > 1 || isPie, position: 'bottom', labels: { font: { size: 11 } } },
            tooltip: { enabled: true }
          },
          scales: isPie ? {} : {
            x: { grid: { display: false }, ticks: { font: { size: 11 } } },
            y: { beginAtZero: true, ticks: { font: { size: 11 } } }
          }
        }
      });
    });
  }
}
function waitForChart() {
  return new Promise(res => {
    const t = setInterval(() => { if (window.Chart) { clearInterval(t); res(); } }, 30);
    setTimeout(() => { clearInterval(t); res(); }, 5000);
  });
}
function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
customElements.define('csv-chart', CsvChart);
