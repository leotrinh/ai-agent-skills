// Draws the step pill and the spotlight frame around the target. Returns false when the target is missing.
([target, badge, label, title]) => {
  document.querySelectorAll('#gv-frame,#gv-pill').forEach(e => e.remove());
  if (label || title) {
    const pill = document.createElement('div'); pill.id = 'gv-pill';
    pill.innerHTML = (label ? `<b>${label}</b>` : '') + `<span>${title || ''}</span>`;
    document.body.appendChild(pill);
  }
  if (!target) return true;
  let el = null;
  if (target.css) el = document.querySelector(target.css);
  else {
    const walker = document.createTreeWalker(document.querySelector('main') || document.body, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) if (walker.currentNode.textContent.includes(target.text)) { el = walker.currentNode.parentElement; break; }
    while (el && el.getBoundingClientRect().width < (target.minW || 0)) el = el.parentElement;
  }
  if (!el) return false;
  const r = el.getBoundingClientRect(), pad = 8;
  const x = Math.max(r.left - pad, 30), y = Math.max(r.top - pad, 30);
  const w = Math.min(r.right + pad, innerWidth - 12) - x, h = Math.min(r.bottom + pad, innerHeight - 12) - y;
  const f = document.createElement('div'); f.id = 'gv-frame';
  Object.assign(f.style, {left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px'});
  if (badge) f.innerHTML = `<div id="gv-badge">${badge}</div>`;
  document.body.appendChild(f);
  return true;
}
