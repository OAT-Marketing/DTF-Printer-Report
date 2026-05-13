// Loads config.json from the client report folder once, exposes via window.REPORT_CONFIG.
// Components await window.REPORT_CONFIG_READY (a Promise) before rendering anything config-dependent.
(function () {
  window.REPORT_CONFIG = null;
  window.REPORT_CONFIG_READY = fetch('config.json', { cache: 'no-store' })
    .then(function (r) {
      if (!r.ok) throw new Error('config.json not found');
      return r.json();
    })
    .then(function (cfg) {
      window.REPORT_CONFIG = cfg;
      if (cfg.primary_color) {
        document.documentElement.style.setProperty('--accent', cfg.primary_color);
      }
      document.title = (cfg.client_name || 'SEO Report') + ' - ' +
        (document.body.dataset.pageTitle || 'Report');
      return cfg;
    })
    .catch(function (err) {
      console.warn('[report] config.json failed to load:', err.message);
      window.REPORT_CONFIG = {
        client_name: 'Client', client_url: '', logo: '', report_period: '',
        report_date: '', primary_color: '#F28C28'
      };
      return window.REPORT_CONFIG;
    });
})();
