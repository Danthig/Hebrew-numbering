/* ===== מנוע גימטריה (פורט ל-JS לתצוגה מקדימה מיידית) ===== */
const ONES = ['', 'א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט'];
const TENS = ['', 'י', 'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ'];
const HUNDREDS = ['', 'ק', 'ר', 'ש', 'ת', 'תק', 'תר', 'תש', 'תת', 'תתק'];
const TEENS = ['י', 'יא', 'יב', 'יג', 'יד', 'טו', 'טז', 'יז', 'יח', 'יט'];
const DEFAULT_CLEAN = { 'שד': 'דש' };
const EXTRA_CLEAN = { 'רע': 'ער', 'שמד': 'דמש' };

function chunkRaw(n) {
  let r = '';
  if (n >= 100) { r += HUNDREDS[Math.floor(n / 100)]; n %= 100; }
  if (n >= 10) {
    const t = Math.floor(n / 10), o = n % 10;
    if (t === 1) r += TEENS[o];
    else { r += TENS[t]; if (o > 0) r += ONES[o]; }
  } else if (n > 0) r += ONES[n];
  return r;
}
function geresh(t) {
  if (!t) return t;
  if (t.length === 1) return t + "'";
  return t.slice(0, -1) + '"' + t.slice(-1);
}
function fmtChunk(n, g, subs) {
  let raw = chunkRaw(n);
  if (subs[raw]) raw = subs[raw];
  return g ? geresh(raw) : raw;
}
function thousandsWords(t, g, subs) {
  if (t === 1) return 'אלף';
  if (t === 2) return 'אלפיים';
  return fmtChunk(t, g, subs) + ' אלפים';
}
function numberToHebrew(n, g, thStyle, clean, extra) {
  if (n < 1 || n > 999999) return String(n);
  let subs = {};
  if (clean) { subs = Object.assign({}, DEFAULT_CLEAN); if (extra) Object.assign(subs, EXTRA_CLEAN); }
  if (n >= 1000) {
    const th = Math.floor(n / 1000), rem = n % 1000;
    const parts = [thStyle === 'words' ? thousandsWords(th, g, subs) : fmtChunk(th, g, subs)];
    if (rem) parts.push(fmtChunk(rem, g, subs));
    return parts.filter(Boolean).join(' ');
  }
  return fmtChunk(n, g, subs);
}
function formatNumber(n, type, g, thStyle, pad, clean, extra) {
  if (type === 'hebrew') return numberToHebrew(n, g, thStyle, clean, extra);
  let s = pad ? String(n).padStart(pad, '0') : String(n);
  return type === 'numeric' ? s + '.' : s;
}
function splitName(name) {
  const i = name.lastIndexOf('.');
  if (i <= 0) return [name, ''];
  return [name.slice(0, i), name.slice(i)];
}
function buildNewName(name, numStr, prefix, sep, mode) {
  const [stem, ext] = splitName(name);
  const label = prefix ? `${prefix}${sep}${numStr}` : numStr;
  let newStem;
  if (mode === 'prepend') newStem = `${label}${sep}${stem}`;
  else if (mode === 'append') newStem = `${stem}${sep}${label}`;
  else newStem = label;
  return newStem + ext;
}

/* ===== מצב ===== */
const state = {
  type: 'hebrew', geresh: true, thousands: 'letters', pad: 0,
  clean: false, cleanExtra: false, mode: 'replace',
  prefix: 'קובץ', separator: '_', start: 1,
  sort: 'natural', subfolders: false,
  files: [], hasSelection: false,
};
const SAMPLE = ['IMG_1023.jpg', 'IMG_1024.jpg', 'סריקה.pdf', 'הקלטה 5.mp3', 'מסמך חשוב.docx'];
const hasBridge = () => typeof window.pywebview !== 'undefined' && window.pywebview.api;

/* ===== עזרי DOM ===== */
const $ = s => document.querySelector(s);
const el = (t, c) => { const e = document.createElement(t); if (c) e.className = c; return e; };

function bindSeg(id, key, after) {
  const seg = $(id);
  seg.querySelectorAll('button').forEach(b => b.onclick = () => {
    seg.querySelectorAll('button').forEach(x => x.classList.remove('on'));
    b.classList.add('on');
    let v = b.dataset.v;
    state[key] = (key === 'pad') ? parseInt(v) : v;
    if (after) after(v);
    render();
  });
}
function bindSwitch(id, key, after) {
  const sw = $(id);
  sw.onclick = () => {
    if (sw.classList.contains('disabled')) return;
    const on = sw.dataset.on === '1' ? '0' : '1';
    sw.dataset.on = on; sw.classList.toggle('on', on === '1');
    state[key] = on === '1';
    if (after) after(on === '1');
    render();
  };
}
function bindCheck(id, key, after) {
  const c = $(id);
  c.onclick = () => {
    const on = c.dataset.on === '1' ? '0' : '1';
    c.dataset.on = on; c.classList.toggle('on', on === '1');
    state[key] = on === '1';
    if (after) after(on === '1');
  };
}

/* ===== תצוגה מקדימה ===== */
function computeRows(names) {
  const rows = [];
  const seen = {};
  const base = parseInt(state.start, 10) || 1;
  names.forEach((name, i) => {
    const num = base + i;
    const numStr = formatNumber(num, state.type, state.geresh, state.thousands, state.pad, state.clean, state.cleanExtra);
    const nn = buildNewName(name, numStr, state.prefix, state.separator, state.mode);
    rows.push({ old: name, neu: nn, idx: num, conflict: false, reason: '' });
    seen[nn] = (seen[nn] || 0) + 1;
  });
  rows.forEach(r => { if (seen[r.neu] > 1) { r.conflict = true; r.reason = 'שם כפול'; } });
  return rows;
}
function render() {
  const names = state.hasSelection ? state.files : SAMPLE;
  const rows = computeRows(names);
  const box = $('#preview');
  box.innerHTML = '';
  if (!names.length) {
    box.innerHTML = `<div class="empty"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7a2 2 0 0 1 2-2h4l2 2h6a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2Z"/></svg><p>אין קבצים</p><span>בחר תיקייה או קבצים</span></div>`;
  } else {
    rows.forEach((r, i) => {
      const row = el('div', 'prow' + (r.conflict ? ' conflict' : ''));
      row.style.animationDelay = (i * 0.018) + 's';
      row.innerHTML =
        `<span class="idx">${r.idx}</span>` +
        `<span class="old">${esc(r.old)}</span>` +
        `<span class="arrow"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><path d="M12 5l-7 7 7 7"/></svg></span>` +
        `<span class="new">${esc(r.neu)}</span>` +
        (r.conflict ? `<span class="reason">${r.reason}</span>` : '');
      box.appendChild(row);
    });
  }
  const conf = rows.filter(r => r.conflict).length;
  const sub = $('#previewSub');
  if (!state.hasSelection) sub.textContent = 'דוגמה חיה — בחר תיקייה כדי לראות את הקבצים שלך';
  else sub.textContent = `${names.length} קבצים` + (conf ? ` · ${conf} התנגשויות` : '');
  setStatus(conf ? `${conf} התנגשויות` : (state.hasSelection ? `${names.length} קבצים מוכנים` : 'מוכן'), conf ? 'warn' : 'ok');
}
function esc(s) { return s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }

/* ===== UI helpers ===== */
function setStatus(text, kind) {
  $('#statusText').textContent = text;
  $('#statusDot').className = 'dot' + (kind === 'warn' ? ' warn' : '');
}
function toast(msg, kind = 'info') {
  const t = el('div', 'toast ' + kind);
  const icons = {
    ok: '<path d="M20 6L9 17l-5-5"/>', err: '<path d="M18 6L6 18M6 6l12 12"/>',
    info: '<path d="M12 16v-4M12 8h.01"/><circle cx="12" cy="12" r="9"/>'
  };
  t.innerHTML = `<span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">${icons[kind]}</svg></span><span>${esc(msg)}</span>`;
  $('#toasts').appendChild(t);
  setTimeout(() => { t.style.transition = '.3s'; t.style.opacity = '0'; t.style.transform = 'translateY(10px)'; setTimeout(() => t.remove(), 300); }, 2600);
}
function busy(on) { $('#overlay').classList.toggle('show', on); }
async function refreshUndo() {
  if (!hasBridge()) return;
  try { $('#undoBtn').disabled = !(await window.pywebview.api.can_undo()); } catch (e) {}
}

/* ===== פעולות מול ה-bridge ===== */
function options() {
  return {
    prefix: state.prefix, separator: state.separator, start_number: parseInt(state.start) || 1,
    numbering_type: state.type, with_geresh: state.geresh, thousands_style: state.thousands,
    numeric_padding: state.pad, rename_mode: state.mode,
    clean_language: state.clean, clean_extra: state.cleanExtra,
    sort: state.sort, recursive: state.subfolders,
  };
}
async function applySelection(res) {
  if (!res || !res.ok) { if (res && res.error) toast(res.error, 'err'); return; }
  state.files = res.files || [];
  state.hasSelection = state.files.length > 0;
  $('#pathbox').textContent = res.label || 'נבחר';
  $('#pathbox').classList.add('active');
  render();
}
async function pickFolder() {
  if (!hasBridge()) { toast('מצב תצוגה בלבד (ללא חיבור)', 'info'); return; }
  const res = await window.pywebview.api.pick_folder(options());
  applySelection(res);
}
async function pickFiles() {
  if (!hasBridge()) { toast('מצב תצוגה בלבד (ללא חיבור)', 'info'); return; }
  const res = await window.pywebview.api.pick_files(options());
  applySelection(res);
}
async function relist() {
  if (!hasBridge() || !state.hasSelection) return;
  const res = await window.pywebview.api.relist(options());
  if (res && res.ok) { state.files = res.files || []; render(); }
}
async function doRename() {
  if (!state.hasSelection) { toast('אנא בחר תיקייה או קבצים', 'err'); return; }
  if (!hasBridge()) { toast('מצב תצוגה בלבד — אין ביצוע אמיתי', 'info'); return; }
  busy(true);
  try {
    const res = await window.pywebview.api.rename(options());
    busy(false);
    if (res.error) { toast(res.error, 'err'); return; }
    if (res.fail > 0) toast(`בוצע ${res.success}/${res.total} · ${res.fail} בעיות`, res.success ? 'info' : 'err');
    else toast(`בוצע בהצלחה! ${res.success} קבצים`, 'ok');
    if (res.files) { state.files = res.files; render(); }
    refreshUndo();
  } catch (e) { busy(false); toast('שגיאה: ' + e, 'err'); }
}
async function undo() {
  if (!hasBridge()) return;
  busy(true);
  try {
    const res = await window.pywebview.api.undo();
    busy(false);
    if (res && res.ok) { toast(`בוטלו ${res.count} קבצים`, 'ok'); state.files = res.files || []; state.hasSelection = state.files.length > 0; render(); }
    else toast('אין מה לבטל', 'info');
    refreshUndo();
  } catch (e) { busy(false); toast('שגיאה: ' + e, 'err'); }
}

/* ===== חיווט ===== */
function init() {
  bindSeg('#sortSeg', 'sort', relist);
  bindSeg('#typeSeg', 'type', v => {
    $('#hebrewOpts').style.display = v === 'hebrew' ? '' : 'none';
    $('#cleanRow').style.display = v === 'hebrew' ? '' : 'none';
    $('#padSeg').closest('.opt-row').style.display = v === 'hebrew' ? 'none' : '';
  });
  bindSeg('#thousandsSeg', 'thousands');
  bindSeg('#padSeg', 'pad');
  bindSeg('#modeSeg', 'mode');
  bindSwitch('#geresh', 'geresh');
  bindSwitch('#clean', 'clean', on => {
    const ex = $('#cleanExtra');
    ex.classList.toggle('disabled', !on);
    if (!on) { ex.dataset.on = '0'; ex.classList.remove('on'); state.cleanExtra = false; }
  });
  bindSwitch('#cleanExtra', 'cleanExtra');
  bindCheck('#subfolders', 'subfolders', relist);

  ['prefix', 'separator', 'start'].forEach(id => {
    $('#' + id).addEventListener('input', e => { state[id === 'start' ? 'start' : id] = e.target.value; render(); });
  });

  $('#pickFolder').onclick = pickFolder;
  $('#pickFiles').onclick = pickFiles;
  $('#doRename').onclick = doRename;
  $('#undoBtn').onclick = undo;
  $('#refreshBtn').onclick = () => { relist(); render(); };
  $('#pathbox').onclick = () => { if (hasBridge() && state.hasSelection) window.pywebview.api.open_location(); };
  $('#exitBtn').onclick = () => { if (hasBridge()) window.pywebview.api.exit_app(); };

  // theme
  const themeBtn = $('#themeBtn');
  const setTheme = t => {
    document.documentElement.dataset.theme = t;
    $('#themeIcon').innerHTML = t === 'dark'
      ? '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z"/>'
      : '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>';
    try { localStorage.setItem('hrn-theme', t); } catch (e) {}
  };
  let saved = 'light';
  try { saved = localStorage.getItem('hrn-theme') || 'light'; } catch (e) {}
  setTheme(saved);
  themeBtn.onclick = () => setTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');

  render();
  // ה-bridge עשוי להיטען מעט אחרי ה-DOM
  window.addEventListener('pywebviewready', refreshUndo);
  setTimeout(refreshUndo, 600);
}
document.addEventListener('DOMContentLoaded', init);
