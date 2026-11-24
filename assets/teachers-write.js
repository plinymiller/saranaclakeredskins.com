/* Private editor for the Teachers section. The private link carries the key after #k=.
   The key is checked by Supabase on every save; it only allows writing teacher pages. */
(function () {
  "use strict";
  var M = window.TeacherMD, $ = function (id) { return document.getElementById(id); };
  var KEYNAME = "slr_teacher_key";
  var key = (location.hash.match(/[#&]k=([A-Za-z0-9_-]{40,200})/) || [])[1] || "";
  try { if (key) localStorage.setItem(KEYNAME, key); else key = localStorage.getItem(KEYNAME) || ""; } catch (e) {}
  window.addEventListener("hashchange", function () { if (/[#&]k=/.test(location.hash)) location.reload(); });
  var F = ["title", "teacher_name", "years", "subject", "photo_caption", "body_md"];
  var editing = null, photo = null, thumb = null, removePhoto = false, keptPhoto = false;

  function view(v) { ["vNoKey", "vEdit", "vDone"].forEach(function (x) { $(x).hidden = x !== v; }); }
  function say(kind, text) { var m = $("wMsg"); m.className = "msg " + kind; m.textContent = text; m.hidden = !text; }

  var ready = window.SUPABASE_URL && window.SUPABASE_ANON_KEY && window.supabase;
  if (!key || !ready) { view("vNoKey"); return; }
  var db = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY, { auth: { persistSession: false } });

  db.rpc("teacher_whoami", { p_key: key }).then(function (r) {
    if (r.error) { view("vNoKey"); if (!/not_allowed/.test(r.error.message)) $("noKeyWhy").textContent = "The site could not be reached just now. Check your internet connection and open your link again."; return; }
    $("whoName").textContent = r.data.name; view("vEdit"); loadMine();
  });

  /* ---- reading what Claude wrote ---- */
  var LABELS = [
    ["title", /^(?:page\s+)?title$/],
    ["teacher_name", /^(?:teacher(?:'s)?(?:\s+name)?|name)$/],
    ["years", /^(?:years?(?:\s+at\s+(?:slhs|saranac(?:\s+lake)?(?:\s+high(?:\s+school)?)?))?|years\s+taught)$/],
    ["subject", /^(?:subject|subjects|taught|role|subject\s*\/\s*role)$/],
    ["photo_caption", /^(?:photo\s+caption|caption)$/],
    ["body_md", /^(?:body(?:\s+markdown)?|story|text|page\s+text)$/]
  ];
  function parse(text) {
    var out = {}, cur = null, body = [], pre = [], found = false;
    String(text).replace(/\r\n?/g, "\n").split("\n").forEach(function (line) {
      var m = line.match(/^\s*(?:[#>*_\s]*)([A-Za-z' \/]{3,40}?)\s*(?:\(.*?\))?\s*[:\uFF1A]\s*(?:\*\*|__)?\s*(.*)$/);
      if (m && cur !== "body_md") {
        var lab = m[1].replace(/[*_]/g, "").trim().toLowerCase();
        for (var i = 0; i < LABELS.length; i++) if (LABELS[i][1].test(lab)) {
          found = true; cur = LABELS[i][0];
          var v = m[2].replace(/^(\*\*|__)|(\*\*|__)$/g, "").trim();
          if (cur === "body_md") { if (v) body.push(v); } else out[cur] = v;
          return;
        }
      }
      if (cur === "body_md") body.push(line);
      else if (!found) pre.push(line);
    });
    if (!found) body = pre;
    var b = body.join("\n").replace(/^\s*```(?:markdown|md)?\s*\n?|\n?```\s*$/g, "").trim();
    if (!found) {
      var h = b.match(/^\s*#\s+(.+)\n/);
      if (h) { out.title = h[1].trim(); b = b.slice(h[0].length).trim(); }
    }
    out.body_md = b;
    ["years", "subject", "photo_caption", "teacher_name", "title"].forEach(function (k) {
      if (out[k] && /^(unknown|not sure|n\/a|none|\?+|\[.*\])$/i.test(out[k])) out[k] = "";
    });
    return out;
  }

  $("paste").addEventListener("input", function () {
    var p = parse(this.value);
    F.forEach(function (k) { if (p[k] !== undefined) $("f_" + k).value = p[k]; });
    if (!$("f_title").value && $("f_teacher_name").value) $("f_title").value = $("f_teacher_name").value;
    preview();
  });
  F.forEach(function (k) { $("f_" + k).addEventListener("input", preview); });

  function preview() {
    var name = $("f_teacher_name").value.trim(), title = $("f_title").value.trim() || name;
    $("pvKicker").textContent = [$("f_subject").value.trim(), $("f_years").value.trim()].filter(Boolean).join(" \u00b7 ") || "Teachers";
    $("pvTitle").textContent = title || "Your page title";
    var who = title && name && title.toLowerCase().indexOf(name.toLowerCase()) === -1 ? name : "";
    $("pvWho").textContent = who; $("pvWho").hidden = !who;
    var src = photo || (keptPhoto && !removePhoto ? keptPhoto : "");
    $("pvFig").hidden = !src; if (src && typeof src === "string") $("pvImg").src = src;
    $("pvCap").textContent = $("f_photo_caption").value.trim();
    $("pvBody").innerHTML = M.render($("f_body_md").value) || '<p class="t-empty">The story will show here after you paste it above.</p>';
    $("pubBtn").disabled = !(name && $("f_body_md").value.trim());
  }

  /* ---- photo: shrink on the phone/computer before sending ---- */
  function shrink(file, max, q) {
    return new Promise(function (ok, bad) {
      var url = URL.createObjectURL(file), img = new Image();
      img.onload = function () {
        var s = Math.min(1, max / Math.max(img.naturalWidth, img.naturalHeight));
        var c = document.createElement("canvas"); c.width = Math.round(img.naturalWidth * s); c.height = Math.round(img.naturalHeight * s);
        var x = c.getContext("2d"); x.fillStyle = "#fff"; x.fillRect(0, 0, c.width, c.height); x.drawImage(img, 0, 0, c.width, c.height);
        URL.revokeObjectURL(url);
        var d = c.toDataURL("image/jpeg", q);
        while (d.length > (max > 600 ? 880000 : 110000) && q > 0.4) { q -= 0.1; d = c.toDataURL("image/jpeg", q); }
        ok(d);
      };
      img.onerror = function () { URL.revokeObjectURL(url); bad(new Error("That file is not a photo this page can read. Try a JPG or PNG.")); };
      img.src = url;
    });
  }
  $("photo").addEventListener("change", function () {
    var f = this.files && this.files[0]; if (!f) return;
    say("", ""); $("photoName").textContent = "Getting the photo ready\u2026";
    Promise.all([shrink(f, 1400, 0.85), shrink(f, 480, 0.8)]).then(function (r) {
      photo = r[0]; thumb = r[1]; removePhoto = false;
      $("photoName").textContent = f.name; $("photoDrop").hidden = false; preview();
    }).catch(function (e) { $("photoName").textContent = ""; say("err", e.message); });
  });
  $("photoDrop").addEventListener("click", function () {
    photo = thumb = null; removePhoto = true; $("photo").value = ""; $("photoName").textContent = ""; this.hidden = true; preview();
  });

  /* ---- publish ---- */
  $("wForm").addEventListener("submit", function (e) {
    e.preventDefault(); say("", "");
    var post = {}; F.forEach(function (k) { post[k] = $("f_" + k).value; });
    if (editing) post.id = editing;
    if (photo) { post.photo_data = photo; post.thumb_data = thumb; }
    if (removePhoto) post.remove_photo = true;
    post.published = true;
    $("pubBtn").disabled = true; $("pubBtn").textContent = "Publishing\u2026";
    db.rpc("teacher_save", { p_key: key, p_post: post }).then(function (r) {
      $("pubBtn").textContent = editing ? "Publish changes" : "Publish";
      if (r.error) { $("pubBtn").disabled = false; return say("err", /not_allowed/.test(r.error.message) ? "Your private link has been turned off. Ask Brian for a new one." : r.error.message); }
      var href = "index.html?t=" + encodeURIComponent(r.data.slug);
      $("doneLink").href = href; $("doneName").textContent = $("f_teacher_name").value.trim();
      view("vDone"); window.scrollTo(0, 0); loadMine();
    });
  });

  $("another").addEventListener("click", function () { reset(); view("vEdit"); $("paste").focus(); });
  function reset() {
    editing = null; photo = thumb = null; removePhoto = false; keptPhoto = false;
    $("paste").value = ""; F.forEach(function (k) { $("f_" + k).value = ""; });
    $("photo").value = ""; $("photoName").textContent = ""; $("photoDrop").hidden = true;
    $("editNote").hidden = true; $("pubBtn").textContent = "Publish"; say("", ""); preview();
  }
  $("cancelEdit").addEventListener("click", reset);

  /* ---- her pages ---- */
  var mine = [];
  function loadMine() {
    db.rpc("teacher_my_posts", { p_key: key }).then(function (r) {
      mine = (r.data || []); var ul = $("mine"); ul.innerHTML = "";
      $("mineBox").hidden = !mine.length;
      mine.forEach(function (p) {
        var li = document.createElement("li");
        li.innerHTML = '<span class="m-t"></span><span class="m-s"></span><span class="m-a">' +
          '<a class="m-view">View</a><button type="button" class="m-edit">Edit</button><button type="button" class="m-hide"></button></span>';
        li.querySelector(".m-t").textContent = p.title;
        li.querySelector(".m-s").textContent = p.published ? "On the site" : "Hidden";
        li.querySelector(".m-view").href = "index.html?t=" + encodeURIComponent(p.slug);
        li.querySelector(".m-view").hidden = !p.published;
        li.querySelector(".m-hide").textContent = p.published ? "Hide" : "Show again";
        li.querySelector(".m-edit").addEventListener("click", function () { edit(p); });
        li.querySelector(".m-hide").addEventListener("click", function () {
          db.rpc("teacher_set_published", { p_key: key, p_id: p.id, p_published: !p.published }).then(loadMine);
        });
        ul.appendChild(li);
      });
    });
  }
  function edit(p) {
    reset(); view("vEdit"); editing = p.id;
    F.forEach(function (k) { $("f_" + k).value = p[k] || ""; });
    keptPhoto = p.has_photo ? (M.okImg(p.thumb_data) ? p.thumb_data : true) : false;
    if (p.has_photo) { $("photoName").textContent = "Current photo kept. Choose a new one to replace it."; $("photoDrop").hidden = false; }
    $("editNote").hidden = false; $("editTitle").textContent = p.title;
    $("pubBtn").textContent = "Publish changes"; preview();
    $("details").open = true; window.scrollTo(0, $("wForm").offsetTop - 80);
  }
  preview();
})();
