// <report-nav page="audit"></report-nav>
// Renders the top nav strip. `page` attribute marks the active item.
class ReportNav extends HTMLElement {
  connectedCallback() {
    const current = this.getAttribute('page') || '';
    const pages = (window.REPORT_PAGES || []).filter(p => p.id !== 'index');
    const active = pages.find(p => p.id === current);
    const title = active ? active.label : '';
    this.innerHTML = `
      <nav class="page-nav">
        <div class="nav-left">${title ? `<span class="nav-page-title">${title}</span>` : ''}</div>
        <div class="nav-links">
          <a href="index.html" class="nav-btn${current === 'index' ? ' active' : ''}">Cover</a>
          ${pages.map(p =>
            `<a href="${p.href}" class="nav-btn${p.id === current ? ' active' : ''}">${p.label}</a>`
          ).join('')}
        </div>
      </nav>
    `;
  }
}
customElements.define('report-nav', ReportNav);
