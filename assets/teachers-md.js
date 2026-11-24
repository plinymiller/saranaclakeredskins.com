/* Safe Markdown for teacher pages. Escapes all HTML first, then adds a small set of tags.
   No raw HTML, no scripts, no images; links must be http(s). */
(function (w) {
  "use strict";
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function inline(s) {
    s = esc(s);
    s = s.replace(/\[([^\]\n]{1,200})\]\((https?:\/\/[^\s)"]{1,500})\)/g, function (m, t, u) {
      return '<a href="' + u + '" rel="nofollow noopener" target="_blank">' + t + "</a>";
    });
    s = s.replace(/\*\*([^*\n]+)\*\*/g, "<strong>$1</strong>");
    s = s.replace(/(^|[^*\w])\*([^*\n]+)\*(?![*\w])/g, "$1<em>$2</em>");
    return s;
  }
  function render(md) {
    var lines = String(md || "").replace(/\r\n?/g, "\n").split("\n");
    var out = [], para = [], list = null, quote = [];
    function flushPara() { if (para.length) { out.push("<p>" + inline(para.join(" ")) + "</p>"); para = []; } }
    function flushList() { if (list) { out.push("<" + list.tag + ">" + list.items.map(function (i) { return "<li>" + inline(i) + "</li>"; }).join("") + "</" + list.tag + ">"); list = null; } }
    function flushQuote() { if (quote.length) { out.push("<blockquote><p>" + inline(quote.join(" ")) + "</p></blockquote>"); quote = []; } }
    function flushAll() { flushPara(); flushList(); flushQuote(); }
    lines.forEach(function (raw) {
      var line = raw.replace(/\s+$/, ""), m;
      if (!line.trim()) { flushAll(); return; }
      if ((m = line.match(/^\s{0,3}(#{1,4})\s+(.*)$/))) { flushAll(); var lv = Math.min(Math.max(m[1].length, 2), 3); out.push("<h" + lv + ">" + inline(m[2].replace(/\s*#+\s*$/, "")) + "</h" + lv + ">"); return; }
      if (/^\s{0,3}([-*_])(\s*\1){2,}\s*$/.test(line)) { flushAll(); out.push("<hr>"); return; }
      if ((m = line.match(/^\s{0,3}>\s?(.*)$/))) { flushPara(); flushList(); quote.push(m[1]); return; }
      if ((m = line.match(/^\s{0,3}[-*+]\s+(.*)$/))) { flushPara(); flushQuote(); if (!list || list.tag !== "ul") { flushList(); list = { tag: "ul", items: [] }; } list.items.push(m[1]); return; }
      if ((m = line.match(/^\s{0,3}\d{1,3}[.)]\s+(.*)$/))) { flushPara(); flushQuote(); if (!list || list.tag !== "ol") { flushList(); list = { tag: "ol", items: [] }; } list.items.push(m[1]); return; }
      if (list && /^\s{2,}\S/.test(line)) { list.items[list.items.length - 1] += " " + line.trim(); return; }
      flushList(); flushQuote(); para.push(line.trim());
    });
    flushAll();
    return out.join("\n");
  }
  function plain(md, n) {
    var t = String(md || "").replace(/^#+\s.*$/gm, "").replace(/^\s*(?:[-*+]|\d{1,3}[.)])\s+/gm, "").replace(/\[([^\]]+)\]\([^)]+\)/g, "$1").replace(/[*_>#`]/g, "").replace(/\s+/g, " ").trim();
    return n && t.length > n ? t.slice(0, n).replace(/\s+\S*$/, "") + "\u2026" : t;
  }
  function okImg(s) { return typeof s === "string" && /^data:image\/(jpeg|webp);base64,[A-Za-z0-9+\/=]+$/.test(s); }
  w.TeacherMD = { render: render, esc: esc, plain: plain, okImg: okImg };
})(window);
