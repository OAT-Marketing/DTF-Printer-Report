// <section-heading number="06" title="On-Page Audit" subtitle="May 2026"></section-heading>
class SectionHeading extends HTMLElement {
  connectedCallback() {
    const num = this.getAttribute('number') || '';
    const title = this.getAttribute('title') || '';
    const subtitle = this.getAttribute('subtitle') || '';
    this.innerHTML = `
      <div class="page-hero">
        <span class="accent-bar"></span>
        <h1>${num ? `<span style="color:var(--page-accent);margin-right:14px;">${num}</span>` : ''}${title}</h1>
        ${subtitle ? `<div class="sub">${subtitle}</div>` : ''}
      </div>
    `;
  }
}
customElements.define('section-heading', SectionHeading);
