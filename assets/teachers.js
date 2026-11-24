/* Teachers section: published pages from Supabase, with the built-in pages as a fallback. */
(function () {
  "use strict";
  var M = window.TeacherMD, $ = function (id) { return document.getElementById(id); };
  var grid = $("tGrid"), one = $("tOne"), list = $("tList"), note = $("tNote");
  var slug = new URLSearchParams(location.search).get("t");

  function card(p) {
    var a = document.createElement("a");
    a.className = "t-card"; a.href = p.href || ("?t=" + encodeURIComponent(p.slug));
    var img = p.img || (M.okImg(p.thumb_data) ? p.thumb_data : "");
    a.innerHTML =
      '<div class="t-ph' + (img ? " has-img" : "") + '">' + (img ? '<img alt="" loading="lazy" decoding="async">' :
        '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="4" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M4 21c1.5-4.5 4.5-6.5 8-6.5s6.5 2 8 6.5" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>') + "</div>" +
      '<div class="t-copy"><p class="kicker"></p><h2 class="t-name"></h2><p class="t-sum"></p><span class="sf-go">Read more</span></div>';
    if (img) a.querySelector("img").src = img;
    a.querySelector(".kicker").textContent = [p.subject, p.years].filter(Boolean).join(" \u00b7 ") || "Saranac Lake High School";
    a.querySelector(".t-name").textContent = p.teacher_name;
    a.querySelector(".t-sum").textContent = p.summary || M.plain(p.body_md, 150);
    return a;
  }

  function showList(rows) {
    var have = {};
    rows.forEach(function (r) { have[r.teacher_name.toLowerCase().replace(/^(mr|mrs|ms|miss|dr)\.?\s+/, "")] = 1; });
    grid.innerHTML = "";
    var stat = (window.TEACHERS_STATIC || []).filter(function (s) { return !have[s.teacher_name.toLowerCase()]; });
    var all = rows.concat(stat).sort(function (a, b) {
      var k = function (p) { var n = p.teacher_name.replace(/^(mr|mrs|ms|miss|dr)\.?\s+/i, "").trim().split(/\s+/); return (n[n.length - 1] + " " + n[0]).toLowerCase(); };
      return k(a) < k(b) ? -1 : 1;
    });
    all.forEach(function (p) { grid.appendChild(card(p)); });
    $("tCount").textContent = all.length === 1 ? "1 teacher" : all.length + " teachers";
  }

  function showOne(p) {
    list.hidden = true; one.hidden = false;
    document.title = p.title + " | Saranac Lake Redskins";
    one.querySelector(".kicker").textContent = [p.subject, p.years].filter(Boolean).join(" \u00b7 ") || "Teachers";
    one.querySelector("h1").textContent = p.title;
    var sub = one.querySelector(".t-who");
    sub.textContent = p.title.toLowerCase().indexOf(p.teacher_name.toLowerCase()) === -1 ? p.teacher_name : "";
    sub.hidden = !sub.textContent;
    var fig = one.querySelector("figure");
    if (M.okImg(p.photo_data)) {
      fig.hidden = false; fig.querySelector("img").src = p.photo_data;
      fig.querySelector("img").alt = p.photo_caption || ("Photo of " + p.teacher_name);
      fig.querySelector("figcaption").textContent = p.photo_caption || "";
    } else fig.hidden = true;
    one.querySelector(".t-body").innerHTML = M.render(p.body_md);
    var by = one.querySelector(".t-by");
    by.textContent = (p.author_name ? "Written by " + p.author_name + ". " : "") + "Updated " + new Date(p.updated_at).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" }) + ".";
    var mail = one.querySelector(".t-mail");
    mail.href = "mailto:plinymiller@gmail.com?subject=" + encodeURIComponent(p.teacher_name + ": a memory, photo or correction");
  }

  var ready = window.SUPABASE_URL && window.SUPABASE_ANON_KEY && window.supabase;
  if (!ready) { showList([]); return; }
  var db = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY, { auth: { persistSession: false } });

  if (slug) {
    db.from("teacher_posts").select("slug,title,teacher_name,years,subject,body_md,photo_data,photo_caption,author_name,updated_at")
      .eq("slug", slug).eq("published", true).maybeSingle().then(function (r) {
        if (r.data) showOne(r.data);
        else { note.hidden = false; note.textContent = "That teacher page is not available. Here are all the teachers."; loadList(); }
      });
  } else loadList();

  function loadList() {
    showList([]);
    db.from("teacher_posts").select("slug,title,teacher_name,years,subject,body_md,thumb_data,updated_at")
      .eq("published", true).then(function (r) { if (!r.error && r.data) showList(r.data); });
  }
})();
