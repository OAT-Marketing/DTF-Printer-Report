// <kpi-grid src="data/audit-summary.csv" cols="4"></kpi-grid>
// CSV schema: label,value,delta,direction,sub
//   - label: KPI title (e.g. "Total clicks")
//   - value: big number (string OK so you can write "1.2K" or "82%")
//   - delta: e.g. "+12%" or "-3" (optional)
//   - direction: "up" | "down" | "" — colors delta green/red
//   - sub: small italic caption under the card (optional)
class KpiGrid extends HTMLElement {
  connectedCallback() {
    const src = this.getAttribute('src');
    const cols = parseInt(this.getAttribute('cols') || '4', 10);
    this.classList.add('rpt-kpi-grid');
    this.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
    if (!src) { window.renderNoData(this, 'No src on <kpi-grid>.'); return; }
    window.loadCSV(src).then(data => {
      if (!data || !data.rows.length) { window.renderNoData(this); return; }
      this.innerHTML = data.rows.map(r => `
        <div class="rpt-kpi">
          <div class="l">${esc(r.label)}</div>
          <div class="n">${esc(r.value)}</div>
          ${r.delta ? `<div class="deltas"><div class="delta-row"><span class="lab">change</span><span class="val ${r.direction || 'placeholder'}">${esc(r.delta)}</span></div></div>` : ''}
          ${r.sub ? `<div class="kpi-sub">${esc(r.sub)}</div>` : ''}
        </div>
      `).join('');
    });
  }
}
function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
customElements.define('kpi-grid', KpiGrid);
