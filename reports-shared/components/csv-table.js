// <csv-table src="data/audit-issues.csv" cols="category,issue,severity,fix"
//            labels="Category,Issue,Priority,Recommendation"
//            sortable paginate="20" badge-col="severity"></csv-table>
//
// - cols: ordered subset of CSV columns to display (default = all)
// - labels: optional matching display headers (default = column name)
// - sortable: click headers to sort
// - paginate: rows per page (default = show all)
// - badge-col: column whose value is rendered as a coloured pill (high/medium/low/etc)
// - num-cols: comma-separated columns that should right-align + tabular-nums

class CsvTable extends HTMLElement {
  connectedCallback() {
    const src = this.getAttribute('src');
    if (!src) { window.renderNoData(this, 'No src on <csv-table>.'); return; }
    window.loadCSV(src).then(data => {
      if (!data || !data.rows.length) { window.renderNoData(this); return; }
      this._data = data;
      this._sortKey = null;
      this._sortDir = 1;
      this._page = 0;
      this._render();
    });
  }
  _render() {
    const data = this._data;
    const cols = (this.getAttribute('cols') || data.headers.join(',')).split(',').map(s => s.trim());
    const labels = (this.getAttribute('labels') || cols.join(',')).split(',').map(s => s.trim());
    const sortable = this.hasAttribute('sortable');
    const paginate = parseInt(this.getAttribute('paginate') || '0', 10);
    const badgeCol = this.getAttribute('badge-col') || '';
    const numCols = (this.getAttribute('num-cols') || '').split(',').map(s => s.trim()).filter(Boolean);

    let rows = data.rows.slice();
    if (this._sortKey) {
      const k = this._sortKey, dir = this._sortDir;
      rows.sort((a, b) => {
        const av = a[k] || '', bv = b[k] || '';
        const an = parseFloat(av.replace(/[^0-9.\-]/g, ''));
        const bn = parseFloat(bv.replace(/[^0-9.\-]/g, ''));
        if (!isNaN(an) && !isNaN(bn)) return (an - bn) * dir;
        return av.localeCompare(bv) * dir;
      });
    }
    const total = rows.length;
    const pageSize = paginate || total;
    const pageRows = rows.slice(this._page * pageSize, (this._page + 1) * pageSize);
    const totalPages = Math.max(1, Math.ceil(total / pageSize));

    const th = cols.map((c, i) =>
      `<th data-col="${esc(c)}" ${sortable ? 'style="cursor:pointer;user-select:none;"' : ''}${numCols.includes(c) ? ' class="r"' : ''}>${esc(labels[i] || c)}${sortable && this._sortKey === c ? (this._sortDir > 0 ? ' ▲' : ' ▼') : ''}</th>`
    ).join('');

    const trs = pageRows.map(r => {
      const tds = cols.map(c => {
        const v = r[c] != null ? r[c] : '';
        if (c === badgeCol && v) {
          const cls = String(v).toLowerCase().replace(/[^a-z0-9]/g, '');
          return `<td><span class="badge ${cls}">${esc(v)}</span></td>`;
        }
        if (numCols.includes(c)) return `<td class="num">${esc(v)}</td>`;
        return `<td>${esc(v)}</td>`;
      }).join('');
      return `<tr>${tds}</tr>`;
    }).join('');

    this.innerHTML = `
      <table>
        <thead><tr>${th}</tr></thead>
        <tbody>${trs}</tbody>
      </table>
      ${paginate && totalPages > 1 ? `
        <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 4px;font-size:12px;color:var(--muted);">
          <span>Showing ${this._page * pageSize + 1}–${Math.min((this._page + 1) * pageSize, total)} of ${total}</span>
          <span>
            <button data-pg="prev" ${this._page === 0 ? 'disabled' : ''} class="nav-btn">Prev</button>
            <button data-pg="next" ${this._page >= totalPages - 1 ? 'disabled' : ''} class="nav-btn">Next</button>
          </span>
        </div>` : ''}
    `;

    if (sortable) {
      this.querySelectorAll('th[data-col]').forEach(th => {
        th.addEventListener('click', () => {
          const k = th.dataset.col;
          if (this._sortKey === k) this._sortDir = -this._sortDir;
          else { this._sortKey = k; this._sortDir = 1; }
          this._page = 0;
          this._render();
        });
      });
    }
    if (paginate) {
      this.querySelectorAll('button[data-pg]').forEach(b => {
        b.addEventListener('click', () => {
          this._page += b.dataset.pg === 'next' ? 1 : -1;
          this._render();
        });
      });
    }
  }
}
function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
customElements.define('csv-table', CsvTable);
