/* Site chrome: mobile menu, disclosure sub-menus, compact header on scroll, class-year jump. No dependencies. */
(function () {
  "use strict";
  var head = document.querySelector(".masthead");
  if (!head) return;
  var nav = document.getElementById("site-nav");
  var menuBtn = head.querySelector(".menu-btn");
  var subBtns = [].slice.call(head.querySelectorAll(".sub-btn"));
  var mq = window.matchMedia("(max-width: 1023px)");

  function setSub(btn, open) {
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    btn.parentNode.classList.toggle("open", open);
  }
  function closeSubs(except) { subBtns.forEach(function (b) { if (b !== except) setSub(b, false); }); }
  subBtns.forEach(function (b) {
    b.addEventListener("click", function () {
      var open = b.getAttribute("aria-expanded") !== "true";
      closeSubs(b); setSub(b, open);
    });
  });

  function setMenu(open) {
    menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    head.classList.toggle("menu-open", open);
    document.documentElement.classList.toggle("nav-lock", open);
    if (open) { var f = nav.querySelector("a"); if (f) f.focus(); }
  }
  menuBtn.addEventListener("click", function () { setMenu(menuBtn.getAttribute("aria-expanded") !== "true"); });

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    var openSub = subBtns.filter(function (b) { return b.getAttribute("aria-expanded") === "true"; })[0];
    if (openSub && !mq.matches) { setSub(openSub, false); openSub.focus(); return; }
    if (head.classList.contains("menu-open")) { setMenu(false); menuBtn.focus(); }
  });
  document.addEventListener("click", function (e) { if (!head.contains(e.target)) { closeSubs(); } });
  // close a desktop sub-menu when focus leaves it
  head.addEventListener("focusout", function (e) {
    if (mq.matches) return;
    subBtns.forEach(function (b) { var li = b.parentNode; if (!li.contains(e.relatedTarget)) setSub(b, false); });
  });
  mq.addEventListener && mq.addEventListener("change", function () { setMenu(false); closeSubs(); });

  // compact header once the page scrolls
  var ticking = false;
  function onScroll() {
    if (ticking) return; ticking = true;
    requestAnimationFrame(function () { head.classList.toggle("is-compact", window.scrollY > 24); ticking = false; });
  }
  window.addEventListener("scroll", onScroll, { passive: true }); onScroll();

  // "What year did you graduate?" jump
  var form = document.querySelector("[data-yearjump]");
  if (form) form.addEventListener("submit", function (e) {
    var input = form.querySelector("input"), msg = form.querySelector(".yj-msg");
    var y = parseInt(input.value, 10);
    if (y >= 1890 && y <= 2000) {
      e.preventDefault();
      location.href = y === 2000 ? "00.html" : (y >= 1960 ? ("0" + (y % 100)).slice(-2) + ".html" : y + ".html");
    } else {
      e.preventDefault();
      msg.innerHTML = 'Enter a year from 1890 to 2000, or <a href="classes.html">browse every class</a>.';
      input.setAttribute("aria-invalid", "true"); input.focus();
    }
  });
})();
