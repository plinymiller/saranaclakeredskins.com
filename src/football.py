"""Football section for saranaclakeredskins.com (static pages in /football/).

Data lives in src/football_data/*.json (research compiled Nov 2026).
Called from generate.py main(): build(globals()).
"""
import json
import re
from collections import Counter, defaultdict
from datetime import date as _date
from html import escape as _esc
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src" / "football_data"
OUT = ROOT / "football"
UNVERIFIED = {"auto-ocr", "probable", "derived"}
COACHES_SRC = "https://wiki.historicsaranaclake.org/index.php/Football"
# Varsity head football coaches, from the Historic Saranac Lake wiki's Football page table.
COACHES = [("1923", "1924", "Russell Sackett"), ("1925", "1936", "Ken Wilson"), ("1937", "1939", "Art Mahoney"),
           ("1940", "1943", "Ken Wilson"), ("1944", None, "Ron Knapp"), ("1945", None, "Bill Leroy"),
           ("1946", None, "Art Mahoney"), ("1947", None, "Lou George"), ("1948", "1951", "Butler Sullivan"),
           ("1952", None, "Ken Wilson"), ("1953", "1955", "Bill Gallagher"), ("1956", "1958", "Duke Benz"),
           ("1959", "1969", "Fraser Sturgeon"), ("1970", "1984", "John Raymond"), ("1985", None, "Larry Ewald"),
           ("1986", "1991", "John Raymond"), ("1992", "1994", "Bruce Bullock"), ("1995", "1998", "John Raymond"),
           ("1999", "2009", "Mark Farmer"), ("2010", "", "Eric Bennett")]
FEATURED = "TKof5enjrdg"  # 1983 Class C Super Bowl vs AuSable Valley


def E(s) -> str:
    return _esc(str(s)) if s is not None else ""


def load(name):
    return json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))


def up(chrome: str) -> str:
    """Re-point the shared site chrome's relative links one level up."""
    return re.sub(r'(href|src)="(?!https?:|mailto:|#|/|\.\./|data:)([^"]*)"', r'\1="../\2"', chrome)


MONTHS = "Jan Feb Mar Apr May June July Aug Sept Oct Nov Dec".split()


def fmt_date(g) -> str:
    d = g.get("date")
    if not d:
        return "Date unknown"
    try:
        y, m, dd = (int(x) for x in d.split("-"))
        s = f"{MONTHS[m-1]} {dd}, {y}"
    except Exception:
        return E(d)
    return ("About " if g.get("date_estimated") else "") + s


def ha(g) -> str:
    return {"away": "at", "neutral": "vs"}.get(g.get("home_away"), "vs")


def has_score(g) -> bool:
    return g.get("score_slhs") is not None and g.get("score_opp") is not None


def score(g) -> str:
    return f"{g['score_slhs']}&ndash;{g['score_opp']}" if has_score(g) else "Score unknown"


def unv(g) -> str:
    if g.get("confidence") in UNVERIFIED and has_score(g):
        return ('<span class="unv" title="Score read by machine from an old scoreboard list, or from a single '
                'secondary source. Not yet checked by hand.">unverified</span>')
    return ""


def res_badge(g) -> str:
    r = g.get("result")
    if not r:
        return '<span class="res na" title="Result unknown">?</span>'
    return f'<span class="res {r}" title="{ {"W": "Win", "L": "Loss", "T": "Tie"}[r] }">{r}</span>'


def yt_thumb(vid) -> str:
    return f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"


def player(v, big=False) -> str:
    vid = E(v["youtube_id"])
    t = E(v.get("title") or "Game film")
    return (f'<div class="yt{" yt-big" if big else ""}"><button type="button" class="yt-play" data-yt="{vid}" data-title="{t}" '
            f'aria-label="Play video: {t}"><img src="{yt_thumb(vid)}" alt="" loading="lazy" width="480" height="360">'
            f'<span class="yt-btn" aria-hidden="true"></span></button>'
            f'<p class="yt-cap">{t} <span>&middot; {E(v.get("channel"))}{(" &middot; " + E(v["length"])) if v.get("length") else ""}'
            f' &middot; <a href="{E(v["url"])}" target="_blank" rel="noopener">YouTube</a></span></p></div>')


def contact_slot(mail, season=None, compact=False) -> str:
    subj = f"Football {season}" if season else "Football"
    href = mail.split("?")[0] + "?subject=" + subj.replace(" ", "%20") + "%20%E2%80%94%20saranaclakeredskins.com"
    return (f'<div class="slot{" compact" if compact else ""}"><span class="slot-ico" aria-hidden="true">+</span>'
            f'<p><strong>Have film, a program, or photos from this season?</strong> '
            f'<a href="{href}">Contact us</a></p></div>')


def paras(text) -> str:
    parts = [p.strip() for p in re.split(r"\n\s*\n|\s+\u2014\s+(?=[A-Z][a-z])", text) if p.strip()]
    return "".join(f"<p>{E(p)}</p>" for p in parts)


def is_pd(a) -> bool:
    return bool(a.get("full_text")) and (a.get("copyright_basis") or "").startswith("Public domain")


def article_html(a, game_link=None) -> str:
    meta = " &middot; ".join(x for x in [E(a.get("paper")), fmt_date({"date": a.get("date")}) if a.get("date") and len(a["date"]) == 10 else E(a.get("date"))] if x)
    out = [f'<article class="story" id="{E(a["id"])}"><p class="story-meta">{meta}</p><h3>{E(a["headline"])}</h3>']
    if is_pd(a):
        out.append(f'<p class="story-sum">{E(a["summary"])}</p>')
        out.append(f'<details class="fulltext"><summary>Read the full text <span>(public domain)</span></summary>{paras(a["full_text"])}</details>')
    else:
        out.append(f'<p class="story-sum">{E(a["summary"])}</p>')
        if a.get("quote"):
            out.append(f'<blockquote>&ldquo;{E(a["quote"].strip(chr(34)))}&rdquo;</blockquote>')
    links = []
    if a.get("url"):
        links.append(f'<a href="{E(a["url"])}" target="_blank" rel="noopener">{"Original source" if is_pd(a) else "Read it at the source"} &#8599;</a>')
    if game_link:
        links.append(game_link)
    out.append(f'<p class="story-links">{" &middot; ".join(links)}</p>')
    out.append(f'<p class="story-rights">{E(a.get("copyright_basis"))}</p></article>')
    return "".join(out)


def src_html(s) -> str:
    name = s.get("paper") or s.get("source") or "Source"
    bits = [E(name)]
    if s.get("date"):
        bits.append(E(s["date"]))
    if s.get("headline"):
        bits.append(f'&ldquo;{E(s["headline"])}&rdquo;')
    label = " &middot; ".join(bits)
    link = f'<a href="{E(s["url"])}" target="_blank" rel="noopener">{label} &#8599;</a>' if s.get("url") else label
    note = f'<span class="src-note">{E(s["note"])}</span>' if s.get("note") else ""
    return f"<li>{link}{note}</li>"


def notes_html(text) -> str:
    if not text:
        return ""
    chunks = [c.strip() for c in re.split(r"(?=Conflict:)", text) if c.strip()]
    out = []
    for c in chunks:
        if c.startswith("Conflict:"):
            out.append(f'<div class="note conflict"><strong>Sources disagree</strong><p>{E(c[len("Conflict:"):].strip())}</p></div>')
        else:
            out.append(f'<p class="game-notes">{E(c)}</p>')
    return "".join(out)


def photo_html(m) -> str:
    """Embed only public-domain (pre-1931) photos we host; everything else is link-only with credit."""
    if m.get("local_file") and (m.get("license") or "").startswith("Public domain"):
        return (f'<figure class="photo"><a href="img/{E(m["local_file"])}"><img src="img/{E(m["local_file"])}" alt="{E(m["title"])}" loading="lazy"></a>'
                f'<figcaption>{E(m["title"])}<span>Public domain &middot; scan via <a href="{E(m.get("page") or m["url"])}" target="_blank" rel="noopener">{E(m.get("source"))}</a></span></figcaption></figure>')
    return ""


def photo_link(m) -> str:
    url = m.get("url") or m.get("page")
    return (f'<li><a href="{E(url)}" target="_blank" rel="noopener">{E(m["title"])} &#8599;</a>'
            f'<span class="src-note">Photo: {E(m.get("source"))}. Link only; not reproduced here.</span></li>')


def coaches_html(sfile=None) -> str:
    rows = []
    for a, b, name in COACHES:
        yrs = a if b is None else (f"{a}&ndash;" if b == "" else f"{a}&ndash;{b}")
        if sfile:
            yrs = f'<a href="{sfile(int(a))}">{yrs}</a>'
        rows.append(f"<tr><td>{yrs}</td><td>{E(name)}</td></tr>")
    return (f'<table class="riv coaches"><thead><tr><th>Years</th><th>Head coach</th></tr></thead><tbody>{"".join(rows)}</tbody></table>'
            f'<p class="fine">Varsity head coaches, from the <a href="{COACHES_SRC}" target="_blank" rel="noopener">Historic Saranac Lake wiki</a>. '
            f'Our sources list Eric Bennett from 2010 but not when his tenure ended, or the coaches since. <a href="mailto:plinymiller@gmail.com?subject=Football%20coaches">Know more? Contact us</a>.</p>')


def build(g: dict) -> None:
    head, header, footer, MAIL, CONTACT = g["head"], g["header"], g["footer"], g["MAIL"], g["CONTACT"]
    G = load("games")
    S = {s["season"]: s for s in load("seasons")}
    A = load("articles")
    R = load("rosters")
    M = load("media")
    P = load("players")
    OUT.mkdir(exist_ok=True)
    AID = {a["id"]: a for a in A}
    GID = {x["id"]: x for x in G}
    by_season = defaultdict(list)
    for x in G:
        by_season[x["season"]].append(x)
    for y in by_season:
        by_season[y].sort(key=lambda x: (x.get("date") or "9999", x["id"]))
    game_arts = defaultdict(list)
    for a in A:
        for gid in a.get("game_ids") or []:
            if gid in GID and a["id"] not in game_arts[gid]:
                game_arts[gid].append(a["id"])
    for x in G:
        for aid in x.get("articles") or []:
            if aid in AID and aid not in game_arts[x["id"]]:
                game_arts[x["id"]].append(aid)
    vids = [m for m in M if m.get("youtube_id")]
    game_vids = defaultdict(list)
    for x in G:
        for v in x.get("videos") or []:
            game_vids[x["id"]].append(v)
    vid_meta = {v["youtube_id"]: v for v in vids}
    seasons_all = sorted(S)
    players_by_season = defaultdict(list)
    for p in P:
        for y in p.get("seasons") or []:
            players_by_season[y].append(p)

    def gfile(x):
        return f"game-{x['id']}.html"

    def sfile(y):
        return f"{y}.html"

    def page(title, desc, body, crumbs=None):
        chrome = up(head(title, desc)).replace("</head>", '<link rel="stylesheet" href="../assets/football.css?v=2">\n</head>')
        crumb = ""
        if crumbs:
            crumb = '<nav class="crumbs" aria-label="Breadcrumb">' + ' <span aria-hidden="true">/</span> '.join(crumbs) + "</nav>"
        return chrome + f"""<body class="fb">
{up(header("football"))}
{crumb}
{body}
{up(footer())}
<script src="../assets/football.js?v=1" defer></script>
</body>
</html>
"""

    def write(name, html):
        (OUT / name).write_text(html, encoding="utf-8")

    def rec(gs):
        w = sum(1 for x in gs if x.get("result") == "W")
        l = sum(1 for x in gs if x.get("result") == "L")
        t = sum(1 for x in gs if x.get("result") == "T")
        return w, l, t

    def season_record(y, short=False):
        s = S.get(y) or {}
        if s.get("official_record"):
            r = s["official_record"]
            m = re.match(r"\s*(\d+-\d+(?:-\d+)?)", r)
            if short and m:
                return m.group(1), "official"
            return E(r), "official"
        gs = by_season.get(y, [])
        if not gs:
            return "", ""
        w, l, t = rec(gs)
        return f"{w}-{l}" + (f"-{t}" if t else ""), "found"

    C = '<a href="index.html">Football</a>'

    # ---------------- game pages ----------------
    for y, gs in by_season.items():
        for i, x in enumerate(gs):
            prev_g = gs[i - 1] if i > 0 else None
            next_g = gs[i + 1] if i + 1 < len(gs) else None
            gtype = x.get("game_type") or "regular"
            kicker = " &middot; ".join(b for b in [fmt_date(x), {"home": "Home", "away": "Away", "neutral": "Neutral site"}.get(x.get("home_away"), ""),
                                                   E(gtype.title()) if gtype.lower() not in ("regular",) else ""] if b)
            if has_score(x):
                h1 = f'Saranac Lake {x["score_slhs"]}, {E(x["opponent"])} {x["score_opp"]}'
            else:
                h1 = f'Saranac Lake {ha(x)} {E(x["opponent"])}'
            films = "".join(player(v) for v in game_vids.get(x["id"], []))
            arts = "".join(article_html(AID[a]) for a in game_arts.get(x["id"], []))
            nav = []
            if prev_g:
                nav.append(f'<a class="pn prev" href="{gfile(prev_g)}">&larr; {ha(prev_g)} {E(prev_g["opponent"])}</a>')
            nav.append(f'<a class="pn up" href="{sfile(y)}">{y} season</a>')
            if next_g:
                nav.append(f'<a class="pn next" href="{gfile(next_g)}">{ha(next_g)} {E(next_g["opponent"])} &rarr;</a>')
            conf_note = ""
            if x.get("confidence") == "film-title":
                conf_note = '<p class="fine">Score taken from the uploader&rsquo;s film title.</p>'
            elif x.get("confidence") in UNVERIFIED and has_score(x):
                conf_note = '<p class="fine"><span class="unv">unverified</span> This score was read by machine from an old newspaper scoreboard, or comes from a single secondary source. Corrections welcome.</p>'
            elif x.get("confidence") == "partial":
                conf_note = '<p class="fine">We know this game was played, but have not found the final score yet.</p>'
            body = f"""<main id="main" class="wrap fb-main">
<article class="game" id="game-body">
  <header class="scorehead {x.get('result') or 'na'}">
    <p class="label">{kicker}</p>
    <h1>{h1}</h1>
    <p class="scoreline">{res_badge(x)} <span class="num">{score(x)}</span> {unv(x)}</p>
    {f'<p class="headline">&ldquo;{E(x["headline"])}&rdquo;</p>' if x.get("headline") else ""}
  </header>
  {conf_note}
  {notes_html(x.get("notes"))}
  {f'<section class="g-films"><h2 class="h2">Game film</h2>{films}</section>' if films else contact_slot(MAIL, y, compact=True)}
  {f'<section class="g-stories"><h2 class="h2">Write-ups</h2>{arts}</section>' if arts else ""}
  <section class="g-sources"><h2 class="h2">Sources</h2><ul class="srcs">{"".join(src_html(s) for s in x.get("sources") or [])}</ul></section>
  <nav class="pager" aria-label="Season games">{"".join(nav)}</nav>
</article>
</main>"""
            title = f"{y} Saranac Lake vs {x['opponent']}" + (f" ({x['score_slhs']}-{x['score_opp']})" if has_score(x) else "")
            write(gfile(x), page(f"{title} | Football | Saranac Lake Redskins",
                                 f"Saranac Lake High School football, {y}: {('final ' + str(x['score_slhs']) + '-' + str(x['score_opp'])) if has_score(x) else 'game'} {ha(x)} {x['opponent']}. Score, write-ups, film and sources.",
                                 body, [C, f'<a href="{sfile(y)}">{y}</a>', f'<span aria-current="page">{ha(x)} {E(x["opponent"])}</span>']))

    # ---------------- season pages ----------------
    def game_row(x):
        icons = ""
        if game_vids.get(x["id"]):
            icons += '<span class="ic film" title="Has film">Film</span>'
        if game_arts.get(x["id"]):
            icons += '<span class="ic wr" title="Has a write-up">Story</span>'
        return (f'<li><a class="grow" href="{gfile(x)}">{res_badge(x)}<span class="g-when">{fmt_date(x)}</span>'
                f'<span class="g-opp">{ha(x)} {E(x["opponent"])}</span><span class="g-sc">{score(x)} {unv(x)}</span>{icons}</a></li>')

    for i, y in enumerate(seasons_all):
        s = S[y]
        gs = by_season.get(y, [])
        recs, kind = season_record(y)
        sv = [v for v in vids if str(v.get("season")) == str(y)]
        hero_film = player(sv[0], big=True) if sv else ""
        more_films = "".join(player(v) for v in sv[1:])
        def fact_li(f):
            see = f.get("see_also") or {}
            extra = f' Read <a href="{E(see["href"])}">{E(see["label"])}</a>.' if see.get("href") and see.get("label") else ""
            return f'<li>{E(f["fact"])} <a class="src" href="{E(f["source"])}" target="_blank" rel="noopener">source</a>{extra}</li>'
        facts = "".join(fact_li(f) for f in s.get("wiki_facts") or [])
        conflicts = "".join(f'<div class="note conflict"><strong>Sources disagree</strong><p>{E(c)}</p></div>' for c in s.get("conflicts") or [])
        rosters = []
        for r in [r for r in R if r.get("season") == y and r.get("players")]:
            staff = " &middot; ".join(f"{E(k.title())}: {E(v)}" for k, v in (r.get("staff") or {}).items() if v)
            rosters.append(f'<div class="roster"><p class="label">{E(r.get("type"))}</p><ul class="names">{"".join(f"<li>{E(n)}</li>" for n in r["players"])}</ul>'
                           f'{f"<p class=fine>{staff}</p>" if staff else ""}{f"<p class=fine>{E(r.get(chr(110)+chr(111)+chr(116)+chr(101)))}</p>" if r.get("note") else ""}'
                           f'<p class="fine">Source: {f"<a href={chr(34)}{E(r[chr(117)+chr(114)+chr(108)])}{chr(34)} target=_blank rel=noopener>{E(r.get(chr(115)+chr(111)+chr(117)+chr(114)+chr(99)+chr(101)))}</a>" if r.get("url") else E(r.get("source"))}</p></div>')
        photos = [m for m in M if m["type"] == "photo" and str(m.get("season")) == str(y)]
        scans = [m for m in M if "page scan" in m["type"] and str(m.get("season")) == str(y)]
        emb = "".join(photo_html(m) for m in photos)
        links = "".join(photo_link(m) for m in photos + scans if not photo_html(m))
        sarts = "".join(article_html(a, (f'<a href="{gfile(GID[a["game_ids"][0]])}">Game page</a>' if len(a.get("game_ids") or []) == 1 and a["game_ids"][0] in GID else None))
                        for a in A if a.get("season") == y)
        pl = "".join(f'<li><a href="players.html#{E(p["id"])}">{E(p["name"])}</a></li>' for p in players_by_season.get(y, []))
        meta = " &middot; ".join(b for b in [f"Coach {E(s['coach'])}" if s.get("coach") else "", E(s.get("league"))] if b)
        prev_y = seasons_all[i - 1] if i > 0 else None
        next_y = seasons_all[i + 1] if i + 1 < len(seasons_all) else None
        rec_line = ""
        if recs:
            rec_line = f'<p class="srec"><span class="num">{recs}</span> <span>{"record" if kind == "official" else "in games found so far"}</span></p>'
        body = f"""<main id="main" class="fb-main season">
<section class="theater"><div class="wrap">
  <p class="label gold">{meta}</p>
  <h1>{y} <span>Redskins football</span></h1>
  {f'<p class="title-chip">{E(s["championship"])}</p>' if s.get("championship") else ""}
  {rec_line}
  {hero_film}
</div></section>
<div class="wrap">
  {conflicts}
  {f'<section><h2 class="h2">Season notes</h2><ul class="facts">{facts}</ul></section>' if facts else ""}
  {f'<p class="game-notes">{E(s["notes"])}</p>' if s.get("notes") else ""}
  <section><h2 class="h2">Games</h2>{f'<ul class="games">{"".join(game_row(x) for x in gs)}</ul>' if gs else '<p class="empty">No games found for this season yet.</p>'}</section>
  {f'<section><h2 class="h2">More film</h2><div class="films">{more_films}</div></section>' if more_films else ""}
  {contact_slot(MAIL, y)}
  {f'<section><h2 class="h2">Roster</h2>{"".join(rosters)}</section>' if rosters else ""}
  {f'<section><h2 class="h2">Players and coaches</h2><ul class="chips">{pl}</ul></section>' if pl else ""}
  {f'<section><h2 class="h2">Team photos</h2><div class="photos">{emb}</div></section>' if emb else ""}
  {f'<section><h2 class="h2">More photos (links)</h2><ul class="srcs">{links}</ul></section>' if links else ""}
  {f'<section><h2 class="h2">Write-ups</h2>{sarts}</section>' if sarts else ""}
  <nav class="pager" aria-label="Seasons">{f'<a class="pn prev" href="{sfile(prev_y)}">&larr; {prev_y}</a>' if prev_y else ""}<a class="pn up" href="index.html#seasons">All seasons</a>{f'<a class="pn next" href="{sfile(next_y)}">{next_y} &rarr;</a>' if next_y else ""}</nav>
</div>
</main>"""
        write(sfile(y), page(f"{y} Season | Football | Saranac Lake Redskins",
                             f"Saranac Lake High School football, {y} season: games, scores, write-ups, rosters and film.",
                             body, [C, f'<span aria-current="page">{y}</span>']))

    # ---------------- hub ----------------
    feat = vid_meta.get(FEATURED)
    feat_html = player(feat, big=True) if feat else ""
    def tile(v):
        gm = GID.get(v.get("game_id"))
        href = gfile(gm) if gm else E(v["url"])
        ext = "" if gm else ' target="_blank" rel="noopener"'
        sc = f'<span class="sc {gm["result"]}">{gm["result"]} {score(gm)}</span>' if gm and has_score(gm) and gm.get("result") else ""
        mine = '<span class="own">adkdon&rsquo;s film</span>' if v.get("owner_is_brian") else ""
        label = f'{gm["season"]} {ha(gm)} {E(gm["opponent"])}' if gm else E(v["title"])
        return (f'<a class="tile" href="{href}"{ext}><span class="th"><img src="{yt_thumb(E(v["youtube_id"]))}" alt="" loading="lazy" width="480" height="360">{sc}{mine}</span>'
                f'<span class="tt">{label}</span><span class="ts">{E(v.get("channel"))}{(" &middot; " + E(v["length"])) if v.get("length") else ""}</span></a>')
    def sy(v):
        try:
            return int(v.get("season"))
        except Exception:
            return 0
    rails = [("adkdon&rsquo;s film archive", "Uploaded by adkdon", [v for v in vids if v.get("owner_is_brian")]),
             ("The Massena series, 1957&ndash;2010", "Massena Sports Archive", [v for v in vids if "Massena Sports" in (v.get("channel") or "")]),
             ("The &rsquo;90s run", "1991&ndash;2001, including the 1995 Carrier Dome season",
              [v for v in vids if 1990 <= sy(v) <= 2001 and "Massena Sports" not in (v.get("channel") or "") and not v.get("owner_is_brian") and "hall of fame" not in (v.get("title") or "").lower()]),
             ("Hall of Fame &amp; modern era", "", [v for v in vids if (sy(v) >= 2002 and "Massena Sports" not in (v.get("channel") or "") and not v.get("owner_is_brian")) or "hall of fame" in (v.get("title") or "").lower()])]
    rails_html = "".join(f'<section class="rail-sec"><div class="rail-h"><h2 class="h2">{t}</h2><span>{s}</span></div><div class="rail">{"".join(tile(v) for v in sorted(l, key=sy))}</div></section>' for t, s, l in rails if l)
    vault = []
    for y in range(1970, 1989):
        n = len([v for v in vids if sy(v) == y])
        r, _ = season_record(y, True)
        champ = " &middot; Title" if (S.get(y) or {}).get("championship") else ""
        vault.append(f'<a class="vc{" has" if n else ""}" href="{sfile(y)}"><b>{y}</b><span>{(str(n) + " film" + ("s" if n > 1 else "") + " online") if n else "Film wanted"}</span><span>{r}{champ}</span></a>')
    # scoreboard
    decades = sorted({(x["season"] // 10) * 10 for x in G})
    opp_n = Counter(x["opponent"] for x in G)
    opps = sorted(opp_n, key=lambda o: (-opp_n[o], o))
    cards = []
    for x in sorted(G, key=lambda x: (x["season"], x.get("date") or "9999", x["id"]), reverse=True):
        fl = bool(game_vids.get(x["id"]))
        st = bool(game_arts.get(x["id"]))
        q = f'{x["season"]} {x["opponent"]} {x.get("headline") or ""}'.lower()
        cards.append(f'<li class="gc" data-dec="{(x["season"]//10)*10}" data-opp="{E(x["opponent"])}" data-res="{x.get("result") or "U"}" data-film="{int(fl)}" data-story="{int(st)}" data-q="{E(q)}">'
                     f'<a href="{gfile(x)}" class="gcard">{res_badge(x)}<span class="gc-main"><span class="gc-yr">{x["season"]} &middot; {fmt_date(x) if x.get("date") else "Date unknown"}</span>'
                     f'<span class="gc-opp">{ha(x)} {E(x["opponent"])}</span></span><span class="gc-sc">{score(x)}{unv(x)}'
                     f'{"<span class=" + chr(34) + "ic film" + chr(34) + ">Film</span>" if fl else ""}{"<span class=" + chr(34) + "ic wr" + chr(34) + ">Story</span>" if st else ""}</span></a></li>')
    dec_opts = "".join(f'<option value="{d}">{d}s</option>' for d in sorted(decades, reverse=True))
    opp_opts = "".join(f'<option value="{E(o)}">{E(o)} ({opp_n[o]})</option>' for o in opps)
    # seasons grid
    sgrid = []
    for d in sorted({(y // 10) * 10 for y in seasons_all}, reverse=True):
        items = []
        for y in [y for y in seasons_all if (y // 10) * 10 == d]:
            r, kind = season_record(y, True)
            champ = '<i title="Championship">&#9733;</i>' if (S.get(y) or {}).get("championship") else ""
            items.append(f'<a class="sy{"" if by_season.get(y) else " thin"}" href="{sfile(y)}"><b>{y}{champ}</b><span>{r or "&mdash;"}</span></a>')
        sgrid.append(f'<div class="sdec"><h3>{d}s</h3><div class="sgrid">{"".join(items)}</div></div>')
    # rivals
    riv = defaultdict(lambda: [0, 0, 0, 9999])
    for x in G:
        r = riv[x["opponent"]]
        if x.get("result") == "W": r[0] += 1
        elif x.get("result") == "L": r[1] += 1
        elif x.get("result") == "T": r[2] += 1
        r[3] = min(r[3], x["season"])
    rv = sorted(((o, *v) for o, v in riv.items() if sum(v[:3]) >= 4), key=lambda t: -(t[1] + t[2] + t[3]))[:14]
    riv_rows = "".join(f'<tr><td>{E(o)}</td><td>{w}-{l}{("-" + str(t)) if t else ""}</td><td>{f}</td><td><span class="bar"><i style="width:{round(100*(w+t/2)/max(1,w+l+t))}%"></i></span></td></tr>' for o, w, l, t, f in rv)
    pd_photos = "".join(photo_html(m) for m in M if m["type"] == "photo" and photo_html(m))
    n_scored = sum(1 for x in G if has_score(x))
    n_titles = sum(1 for s in S.values() if s.get("championship"))
    body = f"""<main id="main" class="fb-main hub">
<section class="theater"><div class="wrap feat">
  <div class="feat-copy">
    <p class="label gold">Saranac Lake Redskins &middot; Football since 1923</p>
    <h1>The Film Room</h1>
    <p>Every game we can find, from the first kickoff against Mineville in 1923 to today: scores, newspaper write-ups, rosters, team photos and game film.</p>
    <ul class="stats"><li><b>{len(G)}</b><span>games</span></li><li><b>{len(by_season)}</b><span>seasons</span></li><li><b>{len(vids)}</b><span>films</span></li><li><b>{n_titles}</b><span>title seasons</span></li></ul>
    <p class="jump"><a class="btn gold" href="#scoreboard">Scoreboard</a> <a class="btn ghost-light" href="#seasons">Seasons</a> <a class="btn ghost-light" href="players.html">Players</a></p>
  </div>
  <div class="feat-film"><p class="label gold">Featured film &middot; 1983 Class C Super Bowl vs AuSable Valley</p>{feat_html}
  <p class="feat-more"><a href="1983.html">See the 1983 season &rarr;</a></p></div>
</div></section>
<div class="wrap">
{rails_html}
<section class="rail-sec" id="vault"><div class="rail-h"><h2 class="h2">The film vault &middot; 1970&ndash;1988</h2><span>Reels from these seasons are being digitized and will appear here.</span></div>
<div class="vault">{"".join(vault)}</div>
{contact_slot(MAIL)}
</section>

<section id="scoreboard" class="sb" aria-labelledby="sb-h">
  <div class="rail-h"><h2 class="h2" id="sb-h">Scoreboard</h2><span>{len(G)} games, {n_scored} with final scores. <span class="unv">unverified</span> marks scores not yet checked by hand.</span></div>
  <form class="filters" role="search" onsubmit="return false">
    <label class="f-q"><span class="sr-only">Search</span><input type="search" id="f-q" placeholder="Search opponent or year" autocomplete="off"></label>
    <label><span class="sr-only">Decade</span><select id="f-dec"><option value="">All decades</option>{dec_opts}</select></label>
    <label><span class="sr-only">Opponent</span><select id="f-opp"><option value="">All opponents</option>{opp_opts}</select></label>
    <div class="seg" role="group" aria-label="Result"><button type="button" data-res="" aria-pressed="true">All</button><button type="button" data-res="W" aria-pressed="false">Wins</button><button type="button" data-res="L" aria-pressed="false">Losses</button><button type="button" data-res="T" aria-pressed="false">Ties</button></div>
    <label class="tog"><input type="checkbox" id="f-film"> Has film</label>
    <label class="tog"><input type="checkbox" id="f-story"> Has story</label>
  </form>
  <p class="sb-count" id="sb-count" aria-live="polite">{len(G)} games</p>
  <ul class="gcards" id="gcards">{"".join(cards)}</ul>
  <p class="more-wrap"><button type="button" class="btn ghost" id="sb-more" hidden>Show more games</button></p>
</section>

<section id="seasons"><div class="rail-h"><h2 class="h2">Seasons</h2><span>&#9733; championship season. Records are official where known, otherwise from the games found so far.</span></div>
{"".join(sgrid)}
</section>

<div class="split">
<section><div class="rail-h"><h2 class="h2">All-time vs rivals</h2><span>From games found so far</span></div>
<table class="riv"><thead><tr><th>Opponent</th><th>W-L-T</th><th>Since</th><th><span class="sr-only">Win share</span></th></tr></thead><tbody>{riv_rows}</tbody></table></section>
<section><div class="rail-h"><h2 class="h2">Team photos</h2><span>Canaras yearbooks, 1920s</span></div><div class="photos two">{pd_photos}</div>
<p class="fine">Later photos are linked from each season page with credit to their owners.</p></section>
</div>
<section id="coaches"><div class="rail-h"><h2 class="h2">Head coaches</h2><span>Varsity head coaches since 1923</span></div>
{coaches_html(sfile)}</section>
<section class="more-links"><a class="teaser" href="players.html"><span class="label">People</span><strong>Players and coaches</strong><span class="teaser-text">{sum(1 for p in P if not any("coach" in x.lower() for x in p.get("positions") or []))} player bios, plus every varsity head coach since 1923.</span></a>
<a class="teaser" href="credits.html"><span class="label">Credits</span><strong>Sources and credits</strong><span class="teaser-text">Where every score, story and film comes from, and how we handle copyright.</span></a></section>
</div>
</main>
<div class="scrim" id="scrim" hidden></div>
<aside class="drawer" id="drawer" aria-label="Game details" hidden><div class="drawer-bar"><a id="drawer-open" href="#">Open full page</a><button type="button" id="drawer-x" aria-label="Close">&times;</button></div><div id="drawer-body"></div></aside>"""
    write("index.html", page("Football | Saranac Lake Redskins",
                             "Saranac Lake High School Redskins football since 1923: every game we can find, with scores, newspaper write-ups, rosters, team photos and game film.",
                             body, [f'<a href="../sports.html">Sports</a>', '<span aria-current="page">Football</span>']))

    # ---------------- players ----------------
    def pcard(p):
        yrs = ", ".join(f'<a href="{sfile(y)}">{y}</a>' for y in p.get("seasons") or [] if y in S) if len(p.get("seasons") or []) <= 8 else \
            f'<a href="{sfile(p["seasons"][0])}">{p["seasons"][0]}</a>&ndash;<a href="{sfile(p["seasons"][-1])}">{p["seasons"][-1]}</a>' if p["seasons"][0] in S and p["seasons"][-1] in S else ""
        bits = []
        if p.get("positions"): bits.append(E(", ".join(p["positions"])))
        if p.get("grad_year"): bits.append(f"Class of {p['grad_year']}")
        honors = "".join(f"<li>{E(h)}</li>" for h in p.get("honors") or [])
        return (f'<article class="pcard" id="{E(p["id"])}"><h3>{E(p["name"])}{f" <span>&ldquo;{E(p[chr(97)+chr(107)+chr(97)])}&rdquo;</span>" if p.get("aka") else ""}</h3>'
                f'<p class="label">{" &middot; ".join(bits)}</p>{f"<p class=fine>Seasons: {yrs}</p>" if yrs else ""}'
                f'<p>{E(p["bio"])}</p>{f"<ul class=honors>{honors}</ul>" if honors else ""}'
                f'{f"<p class=story-links><a href={chr(34)}{E(p[chr(119)+chr(105)+chr(107)+chr(105)+chr(95)+chr(117)+chr(114)+chr(108)])}{chr(34)} target=_blank rel=noopener>More on the Historic Saranac Lake wiki &#8599;</a></p>" if p.get("wiki_url") else ""}</article>')
    coaches = [p for p in P if any("coach" in x.lower() for x in p.get("positions") or [])]
    players = [p for p in P if p not in coaches]
    body = f"""<main id="main" class="wrap fb-main">
<header class="pagehead"><span class="label">Football</span><h1>Players and coaches</h1>
<p class="lede">Short bios drawn mostly from the Historic Saranac Lake wiki, Canaras yearbooks and newspaper stories. Each one links to its source. Know someone who belongs here? <a href="{MAIL}">Contact us</a>.</p></header>
<h2 class="h2">Players</h2><div class="pgrid">{"".join(pcard(p) for p in players)}</div>
<h2 class="h2" id="coaches">Coaches</h2>{coaches_html(sfile)}
</main>"""
    write("players.html", page("Players and Coaches | Football | Saranac Lake Redskins",
                               "Bios of Saranac Lake High School football players and coaches, 1923 to today.", body,
                               [C, '<span aria-current="page">Players and coaches</span>']))

    # ---------------- credits ----------------
    papers = Counter()
    for x in G:
        for s in x.get("sources") or []:
            p = s.get("paper") or s.get("source") or ""
            if p and not p.startswith("Historic Saranac Lake") and not p.startswith("YouTube"):
                papers[re.sub(r"\s*\(.*?\)$", "", p)] += 1
    for a in A:
        p = a.get("paper") or ""
        if p and "Historic Saranac Lake" not in p and "Canaras" not in p and "SLHS" not in p:
            papers[re.sub(r"\s*\(.*?\)$", "", p.split(",")[0])] += 0
    chans = Counter(v.get("channel") for v in vids)
    body = f"""<main id="main" class="wrap fb-main prose-fb">
<header class="pagehead"><span class="label">Football</span><h1>Sources and credits</h1>
<p class="lede">This section was put together from public archives, old newspapers, school yearbooks and game film shared online. Thank you to everyone who kept these records.</p></header>
<section><h2 class="h2">Historic Saranac Lake wiki</h2>
<p><a href="https://wiki.historicsaranaclake.org/index.php/Football" target="_blank" rel="noopener">Historic Saranac Lake</a>&rsquo;s wiki was our richest source: its Football page, player and coach biographies, transcribed newspaper clippings, the Coogan scrapbooks, and scans of the Canaras yearbooks. Every game, roster and bio drawn from it links back to the page it came from. Yearbook photos published before 1931 are public domain and are shown here. Later photos stay on the wiki, and we link to them with credit.</p></section>
<section><h2 class="h2">NYS Historic Newspapers</h2>
<p>Scores and stories from 1923 to the 2000s were found in the digitized papers at <a href="https://nyshistoricnewspapers.org/" target="_blank" rel="noopener">NYS Historic Newspapers</a>, a project of the Northern New York Library Network and the New York State Library. Many scores were read by machine (OCR) from small-type scoreboard lists. Those carry an <span class="unv">unverified</span> tag until someone checks them by hand.</p></section>
<section><h2 class="h2">Newspapers</h2><ul class="cols">{"".join(f"<li>{E(p)}</li>" for p in sorted(papers))}</ul></section>
<section><h2 class="h2">Game film</h2><p>Films play through YouTube&rsquo;s privacy-enhanced player and remain the property of their uploaders. Thank you to:</p>
<ul class="cols">{"".join(f"<li>{E(c)} ({n} film{'s' if n != 1 else ''})</li>" for c, n in chans.most_common())}</ul></section>
<section><h2 class="h2">How we handle copyright</h2>
<ul class="facts"><li>Articles and yearbook pages published before 1931 are in the US public domain, and we show their full text.</li>
<li>For anything newer we give a short summary, at most one brief quote, and a link to the original.</li>
<li>Newspaper and wiki photos published after 1930 are linked, not copied, and credited to their source.</li></ul></section>
<section><h2 class="h2">How to read the data</h2>
<ul class="facts"><li><span class="unv">unverified</span>: a score read by machine from an old scoreboard list, or found in only one secondary source.</li>
<li><strong>Sources disagree</strong>: when two sources give different facts, we show both instead of picking one.</li>
<li>Where a season record is marked &ldquo;in games found so far&rdquo;, some games from that year are still missing.</li></ul></section>
<section><h2 class="h2">Corrections and contributions</h2>
<p>Have film, a program, a roster, a yearbook or photos? Spot a wrong score? <a href="{MAIL}">Contact us</a> at {CONTACT}.</p></section>
</main>"""
    write("credits.html", page("Sources and Credits | Football | Saranac Lake Redskins",
                               "Where the Saranac Lake football scores, stories, photos and films come from.", body,
                               [C, '<span aria-current="page">Sources and credits</span>']))
    print(f"football: {len(G)} games, {len(S)} seasons, {len(P)} people")
