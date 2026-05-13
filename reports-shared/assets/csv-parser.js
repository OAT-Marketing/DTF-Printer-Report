// Tiny RFC-4180-ish CSV parser. Handles quoted fields with embedded commas/quotes/newlines.
// Returns { headers: string[], rows: Array<Record<string, string>> }.
window.parseCSV = function (text) {
  if (!text) return { headers: [], rows: [] };
  text = text.replace(/^﻿/, '');
  var rows = [];
  var field = '';
  var row = [];
  var inQuotes = false;
  for (var i = 0; i < text.length; i++) {
    var c = text[i];
    if (inQuotes) {
      if (c === '"') {
        if (text[i + 1] === '"') { field += '"'; i++; }
        else { inQuotes = false; }
      } else {
        field += c;
      }
    } else {
      if (c === '"') { inQuotes = true; }
      else if (c === ',') { row.push(field); field = ''; }
      else if (c === '\n' || c === '\r') {
        if (c === '\r' && text[i + 1] === '\n') i++;
        row.push(field); field = '';
        if (row.length > 1 || row[0] !== '') rows.push(row);
        row = [];
      } else {
        field += c;
      }
    }
  }
  if (field !== '' || row.length) { row.push(field); rows.push(row); }
  if (!rows.length) return { headers: [], rows: [] };
  var headers = rows.shift().map(function (h) { return h.trim(); });
  var out = rows.map(function (r) {
    var o = {};
    headers.forEach(function (h, i) { o[h] = r[i] != null ? r[i] : ''; });
    return o;
  });
  return { headers: headers, rows: out };
};

// fetch + parse in one call. Returns Promise<{headers, rows}> or null on error.
window.loadCSV = function (path) {
  return fetch(path, { cache: 'no-store' })
    .then(function (r) {
      if (!r.ok) throw new Error(r.status + ' ' + path);
      return r.text();
    })
    .then(window.parseCSV)
    .catch(function (err) {
      console.warn('[loadCSV] ' + err.message);
      return null;
    });
};

// Helper: render a "no data" placeholder consistently.
window.renderNoData = function (el, msg) {
  el.innerHTML =
    '<div style="padding:20px;background:var(--surface);border:1px dashed var(--line);' +
    'border-radius:8px;color:var(--muted);font-size:13px;text-align:center;">' +
    (msg || 'No data file found. Drop the required CSV into the data/ folder.') +
    '</div>';
};
