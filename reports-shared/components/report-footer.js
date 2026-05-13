// <report-footer></report-footer> — small footer strip with client + date pulled from config.
class ReportFooter extends HTMLElement {
  connectedCallback() {
    window.REPORT_CONFIG_READY.then(cfg => {
      this.innerHTML = `
        <footer>
          ${cfg.client_name || ''} · ${cfg.report_period || ''}
          ${cfg.client_url ? ' · ' + cfg.client_url : ''}
        </footer>`;
    });
  }
}
customElements.define('report-footer', ReportFooter);
