// Check a built page without a browser: node seite_pruefen.js <page.html>
// Runs the page script against a minimal DOM stand-in, opens every entry of "Historisches" (every land, every league
// and season) and reports exceptions and cells that contain "undefined" or "NaN".
const fs = require('fs'), vm = require('vm');
const html = fs.readFileSync(process.argv[2], 'utf8');
const m = html.match(/<script>([\s\S]*)<\/script>/);
if (!m) { console.error('kein Skript gefunden'); process.exit(1); }

const els = {};
function mk(id) {
  if (els[id]) return els[id];
  const e = { id, hidden: false, value: '', textContent: '', className: '', dataset: {}, style: {}, firstChild: { value: '' }, options: [],
    addEventListener() {}, setAttribute() {}, getAttribute() { return null; }, appendChild() {}, focus() {}, scrollIntoView() {},
    closest() { return mk(id + '>closest'); }, querySelector() { return mk(id + '>q'); }, querySelectorAll() { return []; },
    classList: { add() {}, remove() {}, toggle() {} } };
  let inner = '';
  Object.defineProperty(e, 'innerHTML', { get: () => inner, set(v) {
    inner = String(v);
    e.options = [...inner.matchAll(/<option value="([^"]*)"/g)].map(x => x[1]);
    if (e.options.length && !e.options.includes(e.value)) e.value = e.options[0];
  } });
  return els[id] = e;
}
const ctx = { console, Intl, Math, JSON, parseInt, String, Number, Array, Object, Set, Map,
  document: { getElementById: mk, querySelector: s => mk('q:' + s), querySelectorAll: () => [], addEventListener() {}, createElement: () => mk('neu' + Math.random()) },
  location: { hash: '' }, history: { replaceState() {} }, addEventListener() {} };
vm.createContext(ctx);
const test = `
;(() => {
  const bad = [], seen = [];
  const look = (what) => { for (const id of ['tab', 'wett', 'meister', 'l-tab', 'titles', 'best-hist', 'ewig', 'mgr', 'l-count', 'tab-count']) {
    const h = $(id).innerHTML + ' ' + $(id).textContent; if (/undefined|NaN/.test(h)) bad.push(what + ' -> ' + id + ': ' + h.match(/.{0,60}(undefined|NaN).{0,40}/)[0]); } };
  HIST.forEach((h, i) => {
    const lands = h[3] ? $('h-land').options : [''];
    lands.forEach(l => { if (l) $('h-land').value = l;
      try {
        showHist(i);
        if (h[1] === 'wett') $('w-liste').options.forEach(o => { $('w-liste').value = o; drawWett(); look(h[0] + ' ' + o); });
        if (h[1] === 'liga') $('l-liga').options.forEach(k => { $('l-liga').value = k; ligaSaisons();
          $('l-saison').options.forEach(y => { $('l-saison').value = y; ['g', 'h', 'a'].forEach(a => { $('l-art').value = a; drawLiga(); look(h[0] + ' ' + k + ' ' + y + ' ' + a); }); }); });
        if (h[1] === 'tab' && VARIANTEN[h[2]]) $('tab-var').options.forEach(v => { $('tab-var').value = v; showHist(i); look(h[0] + ' ' + l + ' ' + v);
          if (!$('tab').innerHTML.includes('<td class="num">')) bad.push(h[0] + ' ' + l + ' ' + v + ': leer'); });
        look(h[0] + ' ' + l);
        const body = ['tab', 'wett', 'meister', 'l-tab', 'titles', 'best-hist', 'ewig'].map(id => $(id).innerHTML).join('');
        seen.push(h[0] + (l ? ' ' + l : '') + ': ' + h[1] + (h[1] === 'tab' ? ' ' + ((D.tab[h[3] ? h[2] + '-' + l : h[2]] || {rows: []}).rows.length) + ' Zeilen' : ''));
      } catch (e) { bad.push(h[0] + ' ' + l + ': ' + e.stack.split('\\n').slice(0, 2).join(' | ')); }
    });
  });
  return { bad, seen, offen: HIST.filter(h => h[1] === 'offen').map(h => h[0]), n: HIST.length };
})()`;
let r;
try { r = vm.runInContext(m[1] + test, ctx); } catch (e) { console.error('FEHLER beim Start:', e.stack.split('\n').slice(0, 4).join('\n')); process.exit(1); }
if (process.argv.includes('-v')) r.seen.forEach(s => console.log('  ' + s));
console.log(`${r.n} Einträge in Historisches, noch offen: ${r.offen.join(', ') || 'keiner'}`);
console.log(r.bad.length ? `${r.bad.length} FEHLER:\n  ` + r.bad.slice(0, 30).join('\n  ') : 'keine Fehler, kein "undefined"/"NaN"');
if (process.argv[3] && !process.argv[3].startsWith('-')) { const [id] = process.argv.slice(3); console.log(els[id] ? els[id].innerHTML.replace(/<\/tr>/g, '\n').replace(/<[^>]+>/g, ' ').slice(0, 3000) : 'kein Element ' + id); }
process.exit(r.bad.length ? 1 : 0);
