(function(){
  "use strict";
  // Click-to-play YouTube (privacy-enhanced; nothing loads from YouTube until you press play)
  document.addEventListener("click", function(e){
    var b = e.target.closest && e.target.closest(".yt-play");
    if(!b) return;
    e.preventDefault();
    var id = b.getAttribute("data-yt"), pl = b.getAttribute("data-ytl");
    var f = document.createElement("iframe");
    if(pl){ if(!/^[\w-]{10,64}$/.test(pl)) return;
      f.src = "https://www.youtube-nocookie.com/embed/videoseries?list=" + pl + "&autoplay=1&rel=0&modestbranding=1";
    } else { if(!/^[\w-]{6,20}$/.test(id)) return;
      f.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0&modestbranding=1"; }
    f.title = b.getAttribute("data-title") || "Game film";
    f.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen";
    f.loading = "lazy";
    f.referrerPolicy = "strict-origin-when-cross-origin";
    b.replaceWith(f);
  });

  // Scoreboard filters
  var list = document.getElementById("gcards");
  if(list){
    var cards = Array.prototype.slice.call(list.children);
    var q = document.getElementById("f-q"), dec = document.getElementById("f-dec"), opp = document.getElementById("f-opp");
    var film = document.getElementById("f-film"), story = document.getElementById("f-story");
    var count = document.getElementById("sb-count"), more = document.getElementById("sb-more");
    var segBtns = Array.prototype.slice.call(document.querySelectorAll(".seg button"));
    var res = "", PAGE = 48, limit = PAGE;
    function apply(reset){
      if(reset) limit = PAGE;
      var qs = (q.value || "").trim().toLowerCase(), n = 0, shown = 0;
      cards.forEach(function(c){
        var ok = (!qs || c.getAttribute("data-q").indexOf(qs) !== -1) &&
          (!dec.value || c.getAttribute("data-dec") === dec.value) &&
          (!opp.value || c.getAttribute("data-opp") === opp.value) &&
          (!res || c.getAttribute("data-res") === res) &&
          (!film.checked || c.getAttribute("data-film") === "1") &&
          (!story.checked || c.getAttribute("data-story") === "1");
        if(ok){ n++; }
        var vis = ok && n <= limit;
        c.hidden = !vis;
        if(vis) shown++;
      });
      count.textContent = n === 1 ? "1 game" : (shown < n ? "Showing " + shown + " of " + n + " games" : n + " games");
      more.hidden = shown >= n;
    }
    [q, dec, opp, film, story].forEach(function(el){ el.addEventListener(el === q ? "input" : "change", function(){ apply(true); }); });
    segBtns.forEach(function(b){ b.addEventListener("click", function(){
      res = b.getAttribute("data-res");
      segBtns.forEach(function(x){ x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      apply(true);
    }); });
    more.addEventListener("click", function(){ limit += PAGE * 2; apply(false); });
    apply(true);

    // Game drawer: loads the game page's content; falls back to normal navigation.
    var drawer = document.getElementById("drawer"), scrim = document.getElementById("scrim"),
        dbody = document.getElementById("drawer-body"), dopen = document.getElementById("drawer-open"),
        dx = document.getElementById("drawer-x"), lastFocus = null, cache = {};
    function close(){
      drawer.hidden = true; scrim.hidden = true; document.body.classList.remove("lock"); dbody.innerHTML = "";
      if(lastFocus) lastFocus.focus();
    }
    function open(href, from){
      lastFocus = from; dopen.href = href;
      dbody.innerHTML = '<p class="fine">Loading…</p>';
      drawer.hidden = false; scrim.hidden = false; document.body.classList.add("lock"); dx.focus();
      var p = cache[href] || (cache[href] = fetch(href).then(function(r){ if(!r.ok) throw new Error(r.status); return r.text(); }));
      p.then(function(t){
        var doc = new DOMParser().parseFromString(t, "text/html");
        var art = doc.getElementById("game-body");
        if(!art) throw new Error("no content");
        dbody.innerHTML = ""; dbody.appendChild(document.importNode(art, true));
        var h = dbody.querySelector("h1"); if(h){ h.setAttribute("tabindex", "-1"); }
      }).catch(function(){ window.location.href = href; });
    }
    list.addEventListener("click", function(e){
      var a = e.target.closest("a.gcard");
      if(!a || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button) return;
      if(!window.fetch || !window.DOMParser) return;
      e.preventDefault(); open(a.getAttribute("href"), a);
    });
    dx.addEventListener("click", close); scrim.addEventListener("click", close);
    document.addEventListener("keydown", function(e){ if(e.key === "Escape" && !drawer.hidden) close(); });
  }
})();
