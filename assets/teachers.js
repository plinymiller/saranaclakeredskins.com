/* Teachers section. MEMBERS ONLY: stories and photos load only for signed-in members
   (Supabase row-level security). Visitors see names and a sign-up invitation. */
(function () {
  "use strict";
  var M = window.TeacherMD, $ = function (id) { return document.getElementById(id); };
  var grid = $("tGrid"), one = $("tOne"), list = $("tList"), gate = $("tGate");
  var slug = new URLSearchParams(location.search).get("t");
  var SIL = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="4" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M4 21c1.5-4.5 4.5-6.5 8-6.5s6.5 2 8 6.5" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>';

  function sortKey(p) { var n = p.teacher_name.replace(/^(mr|mrs|ms|miss|dr)\.?\s+/i, "").trim().split(/\s+/); return (n[n.length - 1] + " " + n[0]).toLowerCase(); }
  function byName(a, b) { return sortKey(a) < sortKey(b) ? -1 : 1; }
  function kick(p) { return [p.subject, p.years].filter(Boolean).join(" \u00b7 ") || "Saranac Lake High School"; }

  function card(p, locked) {
    var a = document.createElement(locked ? "div" : "a");
    a.className = "t-card" + (locked ? " is-locked" : "");
    if (!locked) a.href = "?t=" + encodeURIComponent(p.slug);
    var img = !locked && M.okImg(p.thumb_data) ? p.thumb_data : "";
    a.innerHTML = '<div class="t-ph' + (img ? " has-img" : "") + '">' + (img ? '<img alt="" loading="lazy" decoding="async">' : SIL) +
      (locked ? '<span class="t-lock">Members only</span>' : "") + "</div>" +
      '<div class="t-copy"><p class="kicker"></p><h2 class="t-name"></h2>' + (locked ? "" : '<p class="t-sum"></p><span class="sf-go">Read more</span>') + "</div>";
    if (img) a.querySelector("img").src = img;
    a.querySelector(".kicker").textContent = kick(p);
    a.querySelector(".t-name").textContent = p.teacher_name;
    if (!locked) a.querySelector(".t-sum").textContent = M.plain(p.body_md, 150);
    return a;
  }
  function showList(rows, locked) {
    grid.innerHTML = ""; rows.sort(byName).forEach(function (p) { grid.appendChild(card(p, locked)); });
    $("tCount").textContent = rows.length === 1 ? "1 teacher" : rows.length ? rows.length + " teachers" : "";
    $("tEmpty").hidden = rows.length > 0;
  }
  function showOne(p) {
    list.hidden = true; one.hidden = false;
    document.title = p.title + " | Saranac Lake Redskins";
    one.querySelector(".kicker").textContent = kick(p);
    one.querySelector("h1").textContent = p.title;
    var sub = one.querySelector(".t-who");
    sub.textContent = p.title.toLowerCase().indexOf(p.teacher_name.replace(/^(mr|mrs|ms|miss|dr)\.?\s+/i, "").toLowerCase()) === -1 ? p.teacher_name : "";
    sub.hidden = !sub.textContent;
    var fig = one.querySelector("figure");
    if (M.okImg(p.photo_data)) {
      fig.hidden = false; one.querySelector(".t-head").classList.add("has-photo");
      fig.querySelector("img").src = p.photo_data;
      fig.querySelector("img").alt = p.photo_caption || ("Photo of " + p.teacher_name);
      fig.querySelector("figcaption").textContent = p.photo_caption || "";
    } else { fig.hidden = true; one.querySelector(".t-head").classList.remove("has-photo"); }
    one.querySelector(".t-body").innerHTML = M.render(p.body_md);
    one.querySelector(".t-by").textContent = (p.author_name ? "Written by " + p.author_name + ". " : "") + "Updated " +
      new Date(p.updated_at).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" }) + ".";
    one.querySelector(".t-mail").href = "mailto:plinymiller@gmail.com?subject=" + encodeURIComponent(p.teacher_name + ": a memory, photo or correction");
    window.scrollTo(0, 0);
  }

  function goSignIn(e) { try { localStorage.setItem("slr_next", "teachers/index.html" + (slug ? "?t=" + encodeURIComponent(slug) : "")); } catch (x) {} }
  [].forEach.call(document.querySelectorAll("[data-signin]"), function (a) { a.addEventListener("click", goSignIn); });

  var ready = window.SUPABASE_URL && window.SUPABASE_ANON_KEY && window.supabase;
  if (!ready) { gate.hidden = false; showList([], true); return; }
  var db = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

  db.auth.getSession().then(function (s) {
    var session = s.data && s.data.session;
    if (!session) {
      document.documentElement.classList.add("t-public");
      gate.hidden = false; $("tMember").hidden = true;
      $("tLogin").addEventListener("submit", function (e) {
        e.preventDefault(); var m = $("lgMsg"); m.hidden = true; $("lgBtn").disabled = true;
        db.auth.signInWithPassword({ email: $("lgEmail").value.trim(), password: $("lgPass").value }).then(function (r) {
          $("lgBtn").disabled = false;
          if (r.error) { m.className = "msg err"; m.textContent = r.error.message === "Email not confirmed" ? "Open the confirmation link we emailed you, then log in." : "That email and password do not match an account."; m.hidden = false; }
          else location.reload();
        });
      });
      $("lgForgot").addEventListener("click", function () {
        var m = $("lgMsg"), em = $("lgEmail").value.trim();
        if (!em) { m.className = "msg err"; m.textContent = "Enter your email above, then choose Forgot your password."; m.hidden = false; return; }
        db.auth.resetPasswordForEmail(em, { redirectTo: new URL("../88.html", location.href).href }).then(function () {
          m.className = "msg ok"; m.textContent = "If that email has an account, a reset link is on its way."; m.hidden = false;
        });
      });
      db.rpc("teacher_teaser").then(function (r) { showList(r.error || !Array.isArray(r.data) ? [] : r.data, true); });
      return;
    }
    $("tMember").hidden = false; gate.hidden = true;
    $("tSignOut").addEventListener("click", function () { db.auth.signOut().then(function () { location.reload(); }); });
    if (slug) {
      db.from("teacher_posts").select("slug,title,teacher_name,years,subject,body_md,photo_data,photo_caption,author_name,updated_at")
        .eq("slug", slug).eq("published", true).maybeSingle().then(function (r) {
          if (r.data) showOne(r.data); else { $("tNote").hidden = false; loadList(); }
        });
    } else loadList();
  });
  function loadList() {
    db.from("teacher_posts").select("slug,title,teacher_name,years,subject,body_md,thumb_data,updated_at")
      .eq("published", true).then(function (r) { showList(!r.error && r.data ? r.data : [], false); });
  }
})();
