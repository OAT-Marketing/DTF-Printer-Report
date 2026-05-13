// <cards-grid src="data/roadmap.csv" cols="3" variant="phase"></cards-grid>
//
// CSV schema (variant="phase" — roadmap-style):
//   header,phase,bullets       — bullets is "|" separated
// CSV schema (variant="card" — default note/alert cards):
//   title,body,tone            — tone = "" | "warn" | "alert"
//
// cols: number of grid columns (default 3)
class CardsGrid extends HTMLElement {
  connectedCallback() {
    const src = this.getAttribute('src');
    const cols = parseInt(this.getAttribute('cols') || '3', 10);
    const variant = this.getAttribute('variant') || 'card';
    if (!src) { window.renderNoData(this, 'No src on <cards-grid>.'); return; }
    window.loadCSV(src).then(data => {
      if (!data || !data.rows.length) { window.renderNoData(this); return; }
      this.style.display = 'grid';
      this.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
      this.style.gap = '12px';
      this.innerHTML = data.rows.map(r => {
        if (variant === 'phase') {
          const phaseClass = (r.phase || 'p1').toLowerCase();
          const bullets = (r.bullets || '').split('|').map(b => b.trim()).filter(Boolean);
          return `
            <div class="phase">
              <div class="phase-header ${phaseClass}">${esc(r.header || '')}</div>
              <div class="phase-body"><ul>${bullets.map(b => `<li>${esc(b)}</li>`).join('')}</ul></div>
            </div>`;
        }
        const toneCls = r.tone === 'warn' ? 'warn' : r.tone === 'alert' ? 'alert' : '';
        return `
          <div class="card ${toneCls}">
            <h3>${esc(r.title || '')}</h3>
            <p>${esc(r.body || '')}</p>
          </div>`;
      }).join('');
    });
  }
}
function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
customElements.define('cards-grid', CardsGrid);
