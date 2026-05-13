// Proportional viewport scaling for report pages.
// Base design width: 1280px. Scales up on wider screens (max 1.6x), never below 1x.
(function () {
  function applyZoom() {
    var vw = window.innerWidth;
    var z = Math.min(Math.max(vw / 1280, 1), 1.6);
    document.documentElement.style.zoom = z;
  }
  applyZoom();
  window.addEventListener('resize', applyZoom);
})();
