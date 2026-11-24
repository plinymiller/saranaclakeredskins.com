/* Redskins Store: variant pickers, bag drawer (localStorage), checkout summary.
   No payment code: checkout ends in a disabled "Checkout opens soon" state. */
(function () {
  "use strict";
  var S = window.SLR_STORE || { catalog: {}, ben: {} };
  var CAT = S.catalog, KEY = "slr-store-bag-v1", SHIP = 8;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var money = function (n) { return "$" + (Math.round(n * 100) / 100).toFixed(n % 1 ? 2 : 0); };
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };

  function load() { try { var b = JSON.parse(localStorage.getItem(KEY) || "[]"); return Array.isArray(b) ? b.filter(function (l) { return CAT[l.slug]; }) : []; } catch (e) { return []; } }
  function save(b) { try { localStorage.setItem(KEY, JSON.stringify(b)); } catch (e) {} render(); }
  function unit(l) {
    var p = CAT[l.slug]; if (!p) return 0;
    if (p.type === "poster") return (p.sizes[l.size] || 0) + (l.frame ? p.frame : 0);
    return p.price + (p.sizes[l.size] || 0);
  }
  function lineKey(l) { return [l.slug, l.color || "", l.size || "", l.logo || "", l.frame ? 1 : 0, l.ben].join("|"); }
  function thumb(l) {
    var p = CAT[l.slug];
    if (p.type === "poster") return '<img src="' + esc(p.img) + '" alt="">';
    var c = p.colors[l.color] || {};
    var svg = p.svg.replace(/UID/g, "t" + Math.random().toString(36).slice(2, 7))
      .replace(/--c1:[^;]+;--c2:[^"]+"/, "--c1:" + c.c1 + ";--c2:" + c.c2 + '"')
      .replace(/aria-label="[^"]*"/, 'aria-hidden="true"').replace('role="img"', "");
    if (l.logo === "mark") svg = svg.replace(/href="[^"]*badge\.webp"/, 'href="' + c.mark + '"').replace(/href="[^"]*mark-[a-z]+\.webp"/, 'href="' + c.mark + '"');
    else if (l.logo === "badge") svg = svg.replace(/href="[^"]*mark-(gold|burgundy|white)\.webp"/, 'href="../assets/store/badge.webp"');
    return svg;
  }
  function desc(l) {
    var p = CAT[l.slug], bits = [];
    if (p.type === "poster") { bits.push(p.labels[l.size]); bits.push(l.frame ? "Black frame" : "Print only"); }
    else { if (p.colors[l.color]) bits.push(p.colors[l.color].name); if (l.size) bits.push(l.size); if (l.logo) bits.push(l.logo === "badge" ? "Round badge" : "Chief mark"); }
    return bits.join(" · ");
  }
  function splitHTML(bag) {
    var t = {}; bag.forEach(function (l) { t[l.ben] = (t[l.ben] || 0) + unit(l) * l.qty; });
    return Object.keys(t).map(function (k) { return "<div><span>For " + esc(S.ben[k] || k) + "</span><b>" + money(t[k]) + "</b></div>"; }).join("");
  }
  function subtotal(bag) { return bag.reduce(function (a, l) { return a + unit(l) * l.qty; }, 0); }
  function count(bag) { return bag.reduce(function (a, l) { return a + l.qty; }, 0); }

  function lineHTML(l, i, editable) {
    var ctl = editable
      ? '<div class="st-qty" role="group" aria-label="Quantity for ' + esc(CAT[l.slug].name) + '"><button type="button" data-lq="' + i + '" data-d="-1" aria-label="Decrease">&minus;</button><span aria-live="polite">' + l.qty + '</span><button type="button" data-lq="' + i + '" data-d="1" aria-label="Increase">+</button></div><button type="button" class="st-rm" data-rm="' + i + '">Remove</button>'
      : "<small>Qty " + l.qty + "</small>";
    return '<div class="st-line"><span class="st-line-img">' + thumb(l) + "</span><div><b>" + esc(CAT[l.slug].name) + "</b><small>" + esc(desc(l)) + '</small><span class="st-for">For ' + esc(S.ben[l.ben] || "") + '</span></div><div class="st-line-r"><b>' + money(unit(l) * l.qty) + "</b>" + ctl + "</div></div>";
  }

  function render() {
    var bag = load(), n = count(bag), sub = subtotal(bag);
    $$("[data-bag-count]").forEach(function (el) { el.textContent = n; el.setAttribute("aria-label", n + (n === 1 ? " item" : " items")); });
    var lines = $("[data-bag-lines]");
    if (lines) lines.innerHTML = bag.length ? bag.map(function (l, i) { return lineHTML(l, i, true); }).join("") : '<p class="st-empty">Your bag is empty. Pick something burgundy and gold.</p>';
    var st = $("[data-bag-subtotal]"); if (st) st.textContent = money(sub);
    var sp = $("[data-bag-split]"); if (sp) sp.innerHTML = splitHTML(bag);
    var co = $("[data-bag-checkout]"); if (co) { co.setAttribute("aria-disabled", bag.length ? "false" : "true"); co.style.opacity = bag.length ? "" : ".5"; co.style.pointerEvents = bag.length ? "" : "none"; }
    renderCheckout(bag);
  }

  /* drawer */
  var drawer = $("#st-bag"), scrim = $(".st-scrim"), lastFocus = null;
  function openBag() {
    if (!drawer) return; lastFocus = document.activeElement;
    drawer.hidden = false; scrim.hidden = false; document.body.classList.add("st-lock");
    requestAnimationFrame(function () { drawer.classList.add("on"); scrim.classList.add("on"); drawer.focus(); });
  }
  function closeBag() {
    if (!drawer || drawer.hidden) return;
    drawer.classList.remove("on"); scrim.classList.remove("on"); document.body.classList.remove("st-lock");
    setTimeout(function () { drawer.hidden = true; scrim.hidden = true; }, 280);
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  document.addEventListener("click", function (e) {
    var t = e.target.closest ? e.target : e.target.parentNode;
    if (t.closest("[data-open-bag]")) { e.preventDefault(); openBag(); return; }
    if (t.closest("[data-close-bag]")) { e.preventDefault(); closeBag(); return; }
    var q = t.closest("[data-lq]"); if (q) { var b = load(), i = +q.getAttribute("data-lq"); b[i].qty = Math.max(1, Math.min(20, b[i].qty + (+q.getAttribute("data-d")))); save(b); return; }
    var rm = t.closest("[data-rm]"); if (rm) { var b2 = load(); b2.splice(+rm.getAttribute("data-rm"), 1); save(b2); toast("Removed from bag"); return; }
  });
  document.addEventListener("keydown", function (e) {
    if (!drawer || drawer.hidden) return;
    if (e.key === "Escape") { closeBag(); return; }
    if (e.key === "Tab") {
      var f = $$('a[href],button:not([disabled]),input,[tabindex="0"]', drawer).filter(function (x) { return x.offsetParent !== null; });
      if (!f.length) return; var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && (document.activeElement === first || document.activeElement === drawer)) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });
  var toastEl = $("[data-toast]"), tt;
  function toast(m, quiet) { if (!toastEl) return; toastEl.textContent = m; if (quiet) return; toastEl.classList.add("on"); clearTimeout(tt); tt = setTimeout(function () { toastEl.classList.remove("on"); }, 2600); }

  /* filters */
  $$("[data-filter]").forEach(function (a) {
    a.addEventListener("click", function (e) {
      e.preventDefault(); var f = a.getAttribute("data-filter"), shown = 0;
      $$("[data-filter]").forEach(function (b) { if (b.hasAttribute("aria-pressed")) b.setAttribute("aria-pressed", b === a ? "true" : "false"); });
      $$("[data-grid] .st-card").forEach(function (c) { var on = f === "all" || c.getAttribute("data-cat") === f; c.hidden = !on; if (on) shown++; });
      var s = $("[data-filter-status]"); if (s) s.textContent = shown + " products shown";
    });
  });

  /* product form */
  var form = $("[data-buy]");
  if (form) {
    var slug = form.getAttribute("data-slug"), P = CAT[slug], stage = $("[data-stage]");
    var val = function (n) { var el = form.querySelector('input[name="' + n + '"]:checked'); return el ? el.value : ""; };
    var qtyIn = form.querySelector('input[name="qty"]');
    function update() {
      var q = Math.max(1, Math.min(20, parseInt(qtyIn.value, 10) || 1)); qtyIn.value = q;
      var u;
      if (P.type === "poster") {
        u = (P.sizes[val("size")] || 0) + (val("frame") === "1" ? P.frame : 0);
        var pf = stage && stage.querySelector(".st-poster"); if (pf) pf.classList.toggle("noframe", val("frame") !== "1");
      } else {
        var c = P.colors[val("color")], svg = stage.querySelector("svg");
        if (c && svg) {
          svg.style.setProperty("--c1", c.c1); svg.style.setProperty("--c2", c.c2);
          svg.setAttribute("aria-label", P.name + " mockup, " + c.name);
          var img = svg.querySelector("image.st-logo"), logo = val("logo");
          if (img) img.setAttribute("href", logo === "mark" ? c.mark : "../assets/store/badge.webp");
          var cn = form.querySelector("[data-color-name]"); if (cn) cn.textContent = c.name;
        }
        u = P.price + (P.sizes[val("size")] || 0);
      }
      form.querySelector("[data-price]").textContent = money(u);
      form.querySelector("[data-line-total]").textContent = money(u * q);
    }
    form.addEventListener("change", update);
    qtyIn.addEventListener("input", update);
    $$("[data-q]", form).forEach(function (b) { b.addEventListener("click", function () { qtyIn.value = (parseInt(qtyIn.value, 10) || 1) + (+b.getAttribute("data-q")); update(); }); });
    if (P.type === "poster") { var pf0 = stage.querySelector(".st-poster"); if (pf0) pf0.classList.add("noframe"); }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var size = val("size"), err = form.querySelector("[data-size-err]");
      if (!size) { if (err) { err.hidden = false; } var first = form.querySelector('input[name="size"]:not(:disabled)'); if (first) first.focus(); toast("Choose a size first"); return; }
      if (err) err.hidden = true;
      var line = { slug: slug, size: size, ben: val("ben"), qty: parseInt(qtyIn.value, 10) || 1 };
      if (P.type === "poster") line.frame = val("frame") === "1"; else { line.color = val("color"); line.logo = val("logo") || (P.svg.indexOf("lea") > -1 ? "" : "badge"); if (P.shape === "patch") line.logo = ""; }
      var bag = load(), k = lineKey(line), hit = bag.filter(function (l) { return lineKey(l) === k; })[0];
      if (hit) hit.qty = Math.min(20, hit.qty + line.qty); else bag.push(line);
      save(bag); toast("Added to bag, for " + (S.ben[line.ben] || ""), true); openBag();
    });
    form.addEventListener("change", function (e) { if (e.target.name === "size") { var err = form.querySelector("[data-size-err]"); if (err) err.hidden = true; } });
    update();
  }

  /* checkout */
  var co = $("[data-checkout]");
  function shipCost() { var s = co && co.querySelector('input[name="ship"]:checked'); return s && s.value === "pickup" ? 0 : SHIP; }
  function renderCheckout(bag) {
    if (!co) return;
    var box = $("[data-sum-lines]"), sub = subtotal(bag), ship = bag.length ? shipCost() : 0;
    box.innerHTML = bag.length ? bag.map(function (l, i) { return lineHTML(l, i, true); }).join("") : '<p class="st-empty">Your bag is empty. <a href="index.html">Start shopping</a>.</p>';
    $("[data-sum-sub]").textContent = money(sub);
    $("[data-sum-ship]").textContent = ship ? money(ship) : (bag.length && shipCost() === 0 ? "Free pickup" : money(0));
    $("[data-sum-total]").textContent = money(sub + ship);
    $("[data-sum-total-top]").textContent = money(sub + ship);
    $("[data-sum-split]").innerHTML = splitHTML(bag);
    var n = $("[data-notify]");
    if (n) {
      var body = "Please email me when Redskins Store checkout opens.\n\nMy bag:\n" + bag.map(function (l) { return "- " + l.qty + " x " + CAT[l.slug].name + " (" + desc(l) + ") for " + (S.ben[l.ben] || ""); }).join("\n");
      n.href = "mailto:" + (S.mail || "") + "?subject=" + encodeURIComponent("Redskins Store: notify me") + "&body=" + encodeURIComponent(body);
    }
  }
  if (co) {
    co.addEventListener("submit", function (e) { e.preventDefault(); });
    co.addEventListener("change", function (e) {
      if (e.target.name === "ship") { var a = $("[data-addr]"); a.hidden = e.target.value === "pickup"; render(); }
      if (e.target.name === "allben" && e.target.value) { var b = load(); b.forEach(function (l) { l.ben = e.target.value; }); save(mergeDupes(b)); toast("Whole order now for " + S.ben[e.target.value]); }
    });
    var sumT = $(".st-sum-toggle");
    if (sumT) sumT.addEventListener("click", function (e) { if (!window.matchMedia("(max-width:820px)").matches && e.target.closest("summary")) e.preventDefault(); });
  }
  function mergeDupes(b) { var m = {}, out = []; b.forEach(function (l) { var k = lineKey(l); if (m[k]) m[k].qty = Math.min(20, m[k].qty + l.qty); else { m[k] = l; out.push(l); } }); return out; }

  window.addEventListener("storage", function (e) { if (e.key === KEY) render(); });
  render();
})();
