// Runs inside the page (print media, page-sized viewport). Returns what the PDF can't tell us:
// which letters form one text block, how each block is aligned, and the data-ai-* tags.
// Coordinates are CSS px from the page's top left; export_ai.py converts them to points.
(() => {
  const blocks = new Map();   // container element -> {parts, el}
  const order = [];
  const first = new Map();    // container element -> [text node, offset] of its first visible letter

  const isSvg = el => typeof SVGElement !== "undefined" && el instanceof SVGElement;
  function container(node) {
    // HTML: the nearest ancestor that isn't inline. SVG: the <text> element.
    let el = node.nodeType === 1 ? node : node.parentElement;
    while (el && el !== document.documentElement) {
      if (isSvg(el)) {
        if (el.tagName.toLowerCase() === "text") return el;
      } else {
        const d = getComputedStyle(el).display;
        if (d !== "inline" && d !== "contents") return el;
      }
      el = el.parentElement;
    }
    return el;
  }
  function add(el, text) {
    if (!blocks.has(el)) { blocks.set(el, { el, parts: [] }); order.push(el); }
    blocks.get(el).parts.push(text);
  }
  function transform(text, style) {
    switch (style.textTransform) {
      case "uppercase": return text.toUpperCase();
      case "lowercase": return text.toLowerCase();
      case "capitalize": return text.replace(/(^|[\s\u00a0])(\S)/g, (m, a, b) => a + b.toUpperCase());
      default: return text;
    }
  }
  function collapse(text, style) {
    const ws = style.whiteSpace;
    if (ws === "pre" || ws === "pre-wrap" || ws === "break-spaces") return text;
    if (ws === "pre-line") return text.replace(/[ \t]+/g, " ");
    return text.replace(/[ \t\r\n]+/g, " ");
  }
  function pseudo(el, which) {
    const c = getComputedStyle(el, which).content;
    if (!c || c === "none" || c === "normal") return;
    const m = c.match(/^"(.*)"$/);
    if (m) add(container(el), transform(m[1].replace(/\\"/g, '"'), getComputedStyle(el, which)));
  }
  function walk(node) {
    if (node.nodeType === 3) {
      const parent = node.parentElement;
      if (!parent || !node.data.length) return;
      const range = document.createRange();
      range.selectNodeContents(node);
      if (!range.getClientRects().length && node.data.trim()) return;   // not rendered
      const style = getComputedStyle(parent);
      if (style.visibility === "hidden") return;
      const c = container(node);
      if (!first.has(c) && node.data.trim()) first.set(c, [node, node.data.search(/\S/)]);
      add(c, transform(collapse(node.data, style), style));
      return;
    }
    if (node.nodeType !== 1) return;
    const el = node, tag = el.tagName.toLowerCase();
    if (["script", "style", "template", "noscript", "title", "head"].includes(tag)) return;
    if (!isSvg(el) && getComputedStyle(el).display === "none") return;
    if (tag === "br") { add(container(el), "\n"); return; }
    if (!isSvg(el)) pseudo(el, "::before");
    for (const child of el.childNodes) walk(child);
    if (!isSvg(el)) pseudo(el, "::after");
  }
  walk(document.body || document.documentElement);

  function nameOf(el) {
    const own = el.getAttribute("data-ai-name");
    const outer = el.parentElement && el.parentElement.closest("[data-ai-name]");
    const cls = (el.getAttribute("class") || "").trim().split(/\s+/)[0];
    if (own) return outer ? outer.getAttribute("data-ai-name") + " - " + own : own;
    if (outer) return outer.getAttribute("data-ai-name") + " - " + (cls || el.tagName.toLowerCase());
    return null;
  }
  function alignOf(el) {
    const s = getComputedStyle(el);
    if (isSvg(el)) return { start: "left", middle: "center", end: "right" }[s.textAnchor] || "left";
    const rtl = s.direction === "rtl";
    const a = s.textAlign;
    if (a === "center" || a === "-webkit-center") return "center";
    if (a === "justify") return "justify";
    if (a === "right" || a === "-webkit-right" || (a === "end" && !rtl) || (a === "start" && rtl)) return "right";
    return "left";
  }

  const out = { blocks: [], tags: [] };
  for (const el of order) {
    let text = blocks.get(el).parts.join("");
    text = text.replace(/ {2,}/g, " ").replace(/ ?\n ?/g, "\n").replace(/^[ \n]+|[ \n]+$/g, "");
    if (!text.replace(/\s/g, "")) continue;
    const layerEl = el.closest("[data-ai-text-layer]");
    let firstBox = null;
    if (first.has(el)) {
      const [node, i] = first.get(el), r = document.createRange();
      r.setStart(node, i); r.setEnd(node, i + 1);
      const b = r.getBoundingClientRect();
      firstBox = [b.left + scrollX, b.top + scrollY, b.right + scrollX, b.bottom + scrollY];
    }
    out.blocks.push({ text, align: alignOf(el), name: nameOf(el), first: firstBox,
                      size: parseFloat(getComputedStyle(el).fontSize),
                      letterSpacing: parseFloat(getComputedStyle(el).letterSpacing) || 0,
                      lineHeight: parseFloat(getComputedStyle(el).lineHeight) || null,
                      layer: layerEl ? layerEl.getAttribute("data-ai-text-layer") : null });
  }
  for (const el of document.querySelectorAll("[data-ai-layer],[data-ai-name]")) {
    const layerEl = el.closest("[data-ai-layer]"), nameEl = el.closest("[data-ai-name]");
    const inline = !isSvg(el) && getComputedStyle(el).display === "inline";
    const rects = Array.from(inline ? el.getClientRects() : [el.getBoundingClientRect()])
      .filter(r => r.width > 0 || r.height > 0)
      .map(r => [r.left + scrollX, r.top + scrollY, r.right + scrollX, r.bottom + scrollY]);
    if (rects.length) out.tags.push({ layer: layerEl ? layerEl.getAttribute("data-ai-layer") : null,
                                      group: nameEl ? nameEl.getAttribute("data-ai-name") : null, rects });
  }
  return JSON.stringify(out);
})()
