/* Football card maker for the alumni preview. 1970s-style layout, no card-company marks. */
(function () {
  "use strict";
  var RED = "#A6192E", DARK = "#1A1210", WHITE = "#FFFFFF", CARD = "#EFE8D8";
  var $ = function (id) { return document.getElementById(id); };
  var front = $("al-front"), back = $("al-back");
  if (!front || !back) return;
  var fx = front.getContext("2d"), bx = back.getContext("2d");
  var state = { photo: null, person: null, notes: [], stats: [] };
  var index = [];
  var F = { name: $("f-name"), pos: $("f-pos"), num: $("f-num"), year: $("f-year"), cls: $("f-class"), notes: $("f-notes"), zoom: $("f-zoom"), x: $("f-x"), y: $("f-y") };

  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function reEsc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }
  function fmtDate(d) {
    var m = "Jan Feb Mar Apr May June July Aug Sept Oct Nov Dec".split(" ");
    var p = d.split("-"); return m[+p[1] - 1] + " " + (+p[2]) + ", " + p[0];
  }

  function fit(ctx, text, maxW, size, font) {
    var s = size;
    do { ctx.font = font.replace("{s}", s); s -= 2; } while (ctx.measureText(text).width > maxW && s > 10);
    return s + 2;
  }
  function wrap(ctx, text, x, y, maxW, lh, maxLines) {
    var words = text.split(/\s+/), line = "", n = 0;
    for (var i = 0; i < words.length; i++) {
      var t = line ? line + " " + words[i] : words[i];
      if (ctx.measureText(t).width > maxW && line) {
        if (maxLines && n === maxLines - 1) { ctx.fillText(line + "\u2026", x, y); return y + lh; }
        ctx.fillText(line, x, y); y += lh; n++; line = words[i];
      } else line = t;
    }
    if (line) { ctx.fillText(line, x, y); y += lh; }
    return y;
  }

  function drawPhoto(ctx, x, y, w, h) {
    ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
    var img = state.photo;
    if (img) {
      var z = +F.zoom.value, sc = Math.max(w / img.width, h / img.height) * z;
      var dw = img.width * sc, dh = img.height * sc;
      var ox = (dw - w) / 2 * (+F.x.value), oy = (dh - h) / 2 * (+F.y.value);
      ctx.drawImage(img, x + (w - dw) / 2 - ox, y + (h - dh) / 2 - oy, dw, dh);
    } else {
      var g = ctx.createLinearGradient(0, y, 0, y + h); g.addColorStop(0, "#d9dde3"); g.addColorStop(1, "#9aa3ad");
      ctx.fillStyle = g; ctx.fillRect(x, y, w, h);
      ctx.fillStyle = "rgba(255,255,255,.6)";
      var cx = x + w / 2, cy = y + h * 0.36, r = w * 0.17;
      ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.moveTo(cx - w * 0.36, y + h); ctx.bezierCurveTo(cx - w * 0.36, cy + r * 1.3, cx + w * 0.36, cy + r * 1.3, cx + w * 0.36, y + h); ctx.closePath(); ctx.fill();
      ctx.fillStyle = "#3b434c"; ctx.font = "600 30px Roboto, Arial, sans-serif"; ctx.textAlign = "center";
      ctx.fillText("Add a photo", cx, y + 70); ctx.textAlign = "left";
    }
    ctx.restore();
  }

  function drawFront() {
    var c = fx, W = 750, H = 1050;
    c.fillStyle = WHITE; c.fillRect(0, 0, W, H);
    // outer thin rule
    c.strokeStyle = "#d8d2c4"; c.lineWidth = 2; c.strokeRect(14, 14, W - 28, H - 28);
    // photo with red frame
    var px = 44, py = 44, pw = W - 88, ph = 760;
    drawPhoto(c, px, py, pw, ph);
    c.strokeStyle = RED; c.lineWidth = 8; c.strokeRect(px, py, pw, ph);
    // two-tone banner
    var by = py + ph + 14;
    c.fillStyle = RED; c.fillRect(px, by, pw, 92);
    c.fillStyle = WHITE; c.textBaseline = "middle";
    var team = "REDSKINS";
    fit(c, team, pw - 220, 92, "400 {s}px 'Bebas Neue', Impact, sans-serif");
    c.textAlign = "right"; c.fillText(team, px + pw - 22, by + 50);
    c.fillStyle = WHITE; c.fillRect(px, by + 92, pw, 76);
    c.strokeStyle = RED; c.lineWidth = 4; c.strokeRect(px + 2, by + 92, pw - 4, 74);
    c.fillStyle = DARK;
    var nm = (F.name.value || "Your name").toUpperCase();
    fit(c, nm, pw - 230, 58, "700 {s}px Roboto, Arial, sans-serif");
    c.fillText(nm, px + pw - 22, by + 131);
    c.textAlign = "left";
    // position pennant
    var cx = px + 92, cy = by + 84;
    c.fillStyle = DARK; c.beginPath(); c.arc(cx, cy, 78, 0, Math.PI * 2); c.fill();
    c.fillStyle = WHITE; c.beginPath(); c.arc(cx, cy, 70, 0, Math.PI * 2); c.fill();
    c.fillStyle = RED; c.beginPath(); c.arc(cx, cy, 62, 0, Math.PI * 2); c.fill();
    c.fillStyle = WHITE; c.textAlign = "center";
    var pos = (F.pos.value || "FB").toUpperCase();
    fit(c, pos, 96, 62, "400 {s}px 'Bebas Neue', Impact, sans-serif");
    c.fillText(pos, cx, cy + 4);
    // corner flag: number and season
    var tag = (F.num.value ? "#" + F.num.value : "") + (F.year.value ? (F.num.value ? "  \u2019" : "\u2019") + String(F.year.value).slice(-2) : "");
    if (tag) {
      c.font = "400 46px 'Bebas Neue', Impact, sans-serif";
      var tw = c.measureText(tag).width + 36;
      c.fillStyle = RED; c.beginPath(); c.moveTo(px + pw - tw, py); c.lineTo(px + pw, py); c.lineTo(px + pw, py + 64); c.lineTo(px + pw - tw - 18, py + 64); c.closePath(); c.fill();
      c.fillStyle = WHITE; c.textAlign = "right"; c.fillText(tag, px + pw - 16, py + 35);
    }
    c.textAlign = "left"; c.textBaseline = "alphabetic";
    c.fillStyle = "#6b625c"; c.font = "500 17px Roboto, Arial, sans-serif"; c.textAlign = "center";
    c.fillText("SARANAC LAKE HIGH SCHOOL", W / 2, H - 24); c.textAlign = "left";
  }

  function drawBack() {
    var c = bx, W = 1050, H = 750;
    c.fillStyle = CARD; c.fillRect(0, 0, W, H);
    c.strokeStyle = RED; c.lineWidth = 10; c.strokeRect(22, 22, W - 44, H - 44);
    // header band
    c.fillStyle = RED; c.fillRect(22, 22, W - 44, 112);
    c.fillStyle = WHITE; c.textBaseline = "middle";
    c.font = "400 64px 'Bebas Neue', Impact, sans-serif";
    c.fillText(F.num.value ? F.num.value : "\u2014", 52, 80);
    var nm = (F.name.value || "Your name").toUpperCase();
    fit(c, nm, 640, 60, "400 {s}px 'Bebas Neue', Impact, sans-serif");
    c.fillText(nm, 150, 72);
    c.font = "500 22px Roboto, Arial, sans-serif";
    var sub = [(F.pos.value || "").toUpperCase(), "Saranac Lake Redskins", F.cls.value ? "Class of " + F.cls.value : ""].filter(Boolean).join("  \u2022  ");
    c.fillText(sub, 152, 112);
    c.textAlign = "right"; c.font = "400 54px 'Bebas Neue', Impact, sans-serif";
    c.fillText(F.year.value ? "\u2019" + String(F.year.value).slice(-2) : "", W - 52, 80); c.textAlign = "left";
    c.textBaseline = "alphabetic";
    var y = 180;
    // stat table
    if (state.stats.length) {
      c.fillStyle = RED; c.fillRect(52, y - 30, W - 104, 40);
      c.fillStyle = WHITE; c.font = "700 20px Roboto, Arial, sans-serif";
      c.fillText("RUSHING", 64, y - 3); c.textAlign = "right";
      c.fillText("ATT", 760, y - 3); c.fillText("YDS", 870, y - 3); c.fillText("TD", W - 64, y - 3); c.textAlign = "left";
      y += 40; c.fillStyle = DARK; c.font = "500 22px Roboto, Arial, sans-serif";
      state.stats.forEach(function (r) {
        c.fillText(r.label, 64, y); c.textAlign = "right";
        c.fillText(r.att, 760, y); c.fillText(r.yds, 870, y); c.fillText(r.td, W - 64, y); c.textAlign = "left";
        c.strokeStyle = "rgba(166,25,46,.35)"; c.lineWidth = 1; c.beginPath(); c.moveTo(52, y + 12); c.lineTo(W - 52, y + 12); c.stroke();
        y += 40;
      });
      y += 12;
    }
    c.fillStyle = RED; c.font = "400 34px 'Bebas Neue', Impact, sans-serif"; c.fillText("HIGHLIGHTS", 52, y); y += 34;
    c.fillStyle = DARK; c.font = "400 21px Roboto, Arial, sans-serif";
    var lines = (F.notes.value || "").split(/\n+/).filter(function (s) { return s.trim(); });
    for (var i = 0; i < lines.length && y < H - 90; i++) {
      c.fillStyle = RED; c.fillText("\u25A0", 54, y); c.fillStyle = DARK;
      y = wrap(c, lines[i].trim(), 82, y, W - 140, 27, Math.max(1, Math.floor((H - 90 - y) / 27))) + 6;
    }
    c.fillStyle = "#6b625c"; c.font = "400 16px Roboto, Arial, sans-serif";
    c.fillText("Fan-made card from saranaclakeredskins.com. Facts from the Adirondack Daily Enterprise via NYS Historic Newspapers.", 52, H - 48);
  }

  var raf = 0;
  function draw() { cancelAnimationFrame(raf); raf = requestAnimationFrame(function () { drawFront(); drawBack(); }); }

  function loadImg(src) {
    return new Promise(function (res, rej) { var i = new Image(); i.onload = function () { res(i); }; i.onerror = rej; i.src = src; });
  }

  function setPhotos(list) {
    var box = $("al-photos"); box.innerHTML = "";
    var opts = [{ title: "No photo", src: null }].concat(list || []);
    opts.forEach(function (p, i) {
      var b = document.createElement("button"); b.type = "button";
      b.setAttribute("aria-pressed", i === 0 ? "true" : "false");
      b.setAttribute("aria-label", "Use photo: " + p.title);
      if (p.src) { var im = document.createElement("img"); im.src = p.src; im.alt = ""; b.appendChild(im); }
      else { b.textContent = "None"; b.style.background = "#eee"; b.style.color = DARK; }
      b.addEventListener("click", function () {
        box.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
        b.setAttribute("aria-pressed", "true");
        if (!p.src) { state.photo = null; draw(); return; }
        loadImg(p.src).then(function (img) { state.photo = img; draw(); });
      });
      box.appendChild(b);
    });
  }

  function showPerson(d) {
    state.person = d;
    var v = d.verified;
    F.name.value = v ? v.card_name : d.name.replace(/\s[A-Z]\.\s/, " ");
    F.pos.value = v ? v.position : (d.positions[0] || "");
    F.num.value = v ? v.number : "";
    F.year.value = v ? v.card_year : (d.seasons.length ? d.seasons[d.seasons.length - 1] : (d.mentions.length ? d.mentions[d.mentions.length - 1].date.slice(0, 4) : ""));
    F.cls.value = d.grad_year || (v && v.class_year) || "";
    state.stats = v ? v.stat_rows : [];
    var notes = v ? v.highlights.map(function (h) { return h.text; }) : [];
    if (!v) {
      if (d.honors && d.honors.length) notes = notes.concat(d.honors);
      if (d.bio) notes.push(d.bio);
      if (d.seasons.length) notes.push("Seasons on record: " + d.seasons.join(", ") + ".");
      if (!notes.length && d.mentions.length) notes.push(d.mention_count + " newspaper mentions, " + d.mentions[0].date.slice(0, 4) + "\u2013" + d.mentions[d.mentions.length - 1].date.slice(0, 4) + ".");
    }
    F.notes.value = notes.join("\n");
    setPhotos(d.photos);
    state.photo = null; F.zoom.value = 1; F.x.value = 0; F.y.value = 0;
    var re = new RegExp("(" + reEsc(esc(d.first)) + "\\s+(?:[A-Z]\\.?\\s+)?" + reEsc(esc(d.last)) + "|" + reEsc(esc(d.last)) + ")", "g");
    var h = '<h2>' + esc(d.name) + '</h2><p>' +
      (d.grad_year ? "Class of " + esc(d.grad_year) + ". " : "") +
      (d.positions.length ? "Positions: " + esc(d.positions.join(", ")) + ". " : "") +
      (d.seasons.length ? "Seasons: " + esc(d.seasons.join(", ")) + ". " : "") + "</p>";
    if (v) {
      h += '<h3>Verified stats</h3><table class="al-statrows"><thead><tr><th scope="col">Rushing</th><th scope="col">Att</th><th scope="col">Yds</th><th scope="col">TD</th></tr></thead><tbody>' +
        v.stat_rows.map(function (r) { return "<tr><td><a href=\"" + esc(r.url) + "\" target=\"_blank\" rel=\"noopener\">" + esc(r.label) + "</a></td><td>" + esc(r.att) + "</td><td>" + esc(r.yds) + "</td><td>" + esc(r.td) + "</td></tr>"; }).join("") +
        "</tbody></table><ul>" + v.highlights.map(function (x) { return '<li>' + esc(x.text) + ' <a href="' + esc(x.url) + '" target="_blank" rel="noopener">Source</a></li>'; }).join("") + "</ul><p class=\"al-small\">" + esc(v.team_record) + "</p>";
    }
    if (d.bio) h += "<p>" + esc(d.bio) + "</p>";
    if (d.honors && d.honors.length) h += "<ul>" + d.honors.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul>";
    if (d.sources.length) h += '<h3>Sources</h3><ul>' + d.sources.map(function (s) { return '<li><a href="' + esc(s.url) + '" target="_blank" rel="noopener">' + esc(s.title) + "</a></li>"; }).join("") + "</ul>";
    h += "<h3>Every newspaper mention found (" + d.mention_count + ")</h3>";
    if (d.mention_count > d.mentions.length) h += '<p class="al-small">Showing the first ' + d.mentions.length + ".</p>";
    if (!d.mentions.length) h += '<p class="al-small">No newspaper mentions found in the pages we searched.</p>';
    h += d.mentions.map(function (m) {
      return '<div class="al-mention"><a class="al-md" href="' + esc(m.url) + '" target="_blank" rel="noopener">' + fmtDate(m.date) + "</a>\u2026" + esc(m.snippet).replace(re, "<mark>$1</mark>") + "\u2026</div>";
    }).join("");
    h += '<p class="al-small">Mentions are machine-read (OCR) text from scanned newspapers, so expect typos and mixed-up columns. Open the page to read the original. A name match can also be a different person with the same name.</p>';
    var box = $("al-player"); box.innerHTML = h; box.hidden = false;
    draw();
  }

  function pick(id) {
    return fetch("data/football/" + id + ".json").then(function (r) { return r.json(); }).then(showPerson);
  }

  function search() {
    var q = $("al-q").value.trim().toLowerCase(), ul = $("al-results");
    ul.innerHTML = "";
    if (q.length < 2) return;
    var terms = q.split(/\s+/);
    var hits = index.filter(function (p) { var n = p.name.toLowerCase(); return terms.every(function (t) { return n.indexOf(t) !== -1; }); }).slice(0, 30);
    if (!hits.length) { ul.innerHTML = "<li class=\"al-small\">No player found. You can still type a name on the card.</li>"; return; }
    hits.forEach(function (p) {
      var li = document.createElement("li"), b = document.createElement("button"); b.type = "button";
      var meta = [p.grad_year ? "Class of " + p.grad_year : "", p.seasons.length ? p.seasons[0] + (p.seasons.length > 1 ? "\u2013" + p.seasons[p.seasons.length - 1] : "") : "", p.mentions ? p.mentions + " mentions" : ""].filter(Boolean).join(" \u00b7 ");
      b.innerHTML = "<strong>" + esc(p.name) + "</strong><br><small>" + esc(meta) + "</small>";
      b.addEventListener("click", function () { pick(p.id); });
      li.appendChild(b); ul.appendChild(li);
    });
  }

  function download(cv, which) {
    var n = (F.name.value || "card").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
    cv.toBlob(function (b) {
      var a = document.createElement("a"); a.href = URL.createObjectURL(b); a.download = n + "-" + which + ".png";
      document.body.appendChild(a); a.click(); a.remove(); setTimeout(function () { URL.revokeObjectURL(a.href); }, 2000);
    }, "image/png");
  }

  ["name", "pos", "num", "year", "cls", "notes", "zoom", "x", "y"].forEach(function (k) { F[k].addEventListener("input", draw); });
  $("f-upload").addEventListener("change", function (e) {
    var f = e.target.files && e.target.files[0]; if (!f) return;
    var url = URL.createObjectURL(f);
    loadImg(url).then(function (img) { state.photo = img; document.querySelectorAll("#al-photos button").forEach(function (x) { x.setAttribute("aria-pressed", "false"); }); draw(); });
  });
  $("al-q").addEventListener("input", search);
  $("dl-front").addEventListener("click", function () { download(front, "front"); });
  $("dl-back").addEventListener("click", function () { download(back, "back"); });

  var fontsReady = (document.fonts && document.fonts.load) ? Promise.all([document.fonts.load("400 40px 'Bebas Neue'"), document.fonts.load("700 20px Roboto"), document.fonts.load("400 20px Roboto")]).catch(function () {}) : Promise.resolve();
  fontsReady.then(function () {
    setPhotos([]); draw();
    return fetch("data/football/index.json").then(function (r) { return r.json(); });
  }).then(function (d) {
    index = d;
    var want = new URLSearchParams(location.search).get("player") || "shane-graham";
    if (index.some(function (p) { return p.id === want; })) { $("al-q").value = ""; return pick(want); }
  }).then(function () { window.__cardReady = true; }).catch(function (e) { console.warn("Card data could not load", e); });
})();
