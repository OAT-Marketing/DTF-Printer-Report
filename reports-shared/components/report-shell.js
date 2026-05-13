// <report-shell page="audit" accent="#C0392B">...page content...</report-shell>
// Wraps a page in nav + .wrap container + footer. Sets per-page accent CSS variable.
// Loads all child components on first use.
(function () {
  const SHARED = '../../reports-shared/';

  // Inject font + chart CDN + style.css + scale.js exactly once.
  function injectHead() {
    if (document.getElementById('rpt-style')) return;
    const head = document.head;
    const link1 = document.createElement('link');
    link1.rel = 'preconnect'; link1.href = 'https://fonts.googleapis.com';
    head.appendChild(link1);
    const link2 = document.createElement('link');
    link2.rel = 'preconnect'; link2.href = 'https://fonts.gstatic.com';
    link2.crossOrigin = ''; head.appendChild(link2);
    const fonts = document.createElement('link');
    fonts.rel = 'stylesheet';
    fonts.href = 'https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800;900&family=Work+Sans:wght@400;600;700&display=swap';
    head.appendChild(fonts);
    const css = document.createElement('link');
    css.id = 'rpt-style'; css.rel = 'stylesheet';
    css.href = SHARED + 'assets/style.css';
    head.appendChild(css);
    const scale = document.createElement('script');
    scale.src = SHARED + 'assets/scale.js'; scale.defer = true;
    head.appendChild(scale);
  }

  // Load Chart.js + datalabels only if any <csv-chart> exists on the page.
  function maybeInjectChartJS() {
    if (!document.querySelector('csv-chart')) return;
    if (window.Chart) return;
    const s1 = document.createElement('script');
    s1.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js';
    document.head.appendChild(s1);
    const s2 = document.createElement('script');
    s2.src = 'https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js';
    document.head.appendChild(s2);
  }

  // Dependency scripts in dependency order. All share-folder paths.
  const DEPS = [
    'components/_pages.js',
    'assets/config-loader.js',
    'assets/csv-parser.js',
    'components/report-nav.js',
    'components/report-footer.js',
    'components/section-heading.js',
    'components/kpi-grid.js',
    'components/csv-table.js',
    'components/csv-chart.js',
    'components/cards-grid.js'
  ];
  function injectDeps() {
    DEPS.forEach(p => {
      if (document.querySelector(`script[data-rpt="${p}"]`)) return;
      const s = document.createElement('script');
      s.src = SHARED + p; s.dataset.rpt = p; s.async = false; // preserve order
      document.head.appendChild(s);
    });
  }

  class ReportShell extends HTMLElement {
    connectedCallback() {
      injectHead();
      injectDeps();

      const page = this.getAttribute('page') || '';
      const accent = this.getAttribute('accent');
      if (accent) {
        this.style.setProperty('--page-accent', accent);
        // build a soft variant from the hex
        this.style.setProperty('--page-accent-soft', hexToSoft(accent));
      }
      document.body.dataset.pageTitle = page;

      const inner = this.innerHTML;
      this.innerHTML = `
        <report-nav page="${page}"></report-nav>
        <div class="wrap">${inner}</div>
        <report-footer></report-footer>
      `;

      // After deps load, Chart.js if needed.
      setTimeout(maybeInjectChartJS, 0);
    }
  }

  function hexToSoft(hex) {
    const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    if (!m) return 'rgba(242,140,40,0.10)';
    return `rgba(${parseInt(m[1], 16)},${parseInt(m[2], 16)},${parseInt(m[3], 16)},0.10)`;
  }

  customElements.define('report-shell', ReportShell);
})();
