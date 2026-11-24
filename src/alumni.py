"""Unpublished alumni preview pages (noindex, not linked from the site nav).

Writes /alumni/: a hub, class-of pages for 1960-2000, the trading-card maker and a
sign-up preview. Data: data/alumni.json (public-source names), src/alumni_data/years.json
(cited year facts), alumni/data/football/ (football mentions index).
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "alumni"
YEARS = range(2000, 1959, -1)
ROBOTS = "noindex, nofollow, noarchive"


def E(s):
    return html.escape(str(s)) if s is not None else ""


def up(chrome):
    return re.sub(r'(href|src)="(?!https?:|mailto:|#|/|\.\./|data:)([^"]*)"', r'\1="../\2"', chrome)


def ext(url, text):
    return f'<a href="{E(url)}" target="_blank" rel="noopener">{text}</a>'


STATUS = {
    "transcribed-ocr": ("Graduate list transcribed", "ok"),
    "transcribed-ocr-photo-captions": ("Names from graduation photo pages", "ok"),
    "located-not-transcribed": ("List found, not yet transcribed", "warn"),
    "insert-not-digitized": ("List not in the digitized paper", "warn"),
    "none-found": ("No list found yet", "none"),
}


def build(g):
    head, header, footer = g["head"], g["header"], g["footer"]
    year_file = g["year_file"]
    OUT.mkdir(exist_ok=True)
    A = json.loads((ROOT / "data/alumni.json").read_text(encoding="utf-8"))
    Y = json.loads((ROOT / "src/alumni_data/years.json").read_text(encoding="utf-8"))
    samples = json.loads((ROOT / "src/alumni_data/sample_cards.json").read_text(encoding="utf-8"))
    by_year = {}
    for p in A["people"]:
        by_year.setdefault(p["class_year"], []).append(p)

    # merge verified sample-card data into the football index files
    fdir = OUT / "data/football"
    for pid, s in samples.items():
        f = fdir / f"{pid}.json"
        if f.exists():
            d = json.loads(f.read_text(encoding="utf-8"))
            d["verified"] = s
            f.write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    def page(title, desc, body, js=None, cls=""):
        chrome = up(head(title, desc, robots=ROBOTS)).replace(
            "</head>", '<link rel="stylesheet" href="../assets/alumni.css?v=1">\n</head>')
        script = f'\n<script src="../assets/{js}?v=1" defer></script>' if js else ""
        return chrome + f"""<body class="al {cls}">
{up(header(None))}
<main id="main">
<div class="al-preview" role="note"><strong>Preview.</strong> This section is unpublished and hidden from search engines. It is not linked from the site menu yet.</div>
{body}
</main>
{up(footer())}{script}
</body>
</html>
"""

    def write(name, text):
        (OUT / name).write_text(text, encoding="utf-8")
        print(f"wrote alumni/{name} ({len(text)} bytes)")

    def yr_nav(y, where):
        prev_y, next_y = y + 1, y - 1
        a = f'<a href="class-{prev_y}.html">&larr; Class of {prev_y}</a>' if prev_y <= 2000 else "<span></span>"
        b = f'<a href="class-{next_y}.html">Class of {next_y} &rarr;</a>' if next_y >= 1960 else "<span></span>"
        return f'<nav class="al-yrnav" aria-label="Other classes, {where}">{a}<a href="index.html">All classes</a>{b}</nav>'

    def money(v, d=2):
        return f"${v:,.{d}f}"

    def class_page(y):
        f = Y[str(y)]
        meta = A["years"].get(str(y), {})
        people = sorted(by_year.get(y, []), key=lambda p: (p["name"].split()[-1].lower(), p["name"].lower()))
        st_label, st_cls = STATUS.get(meta.get("list_status", "none-found"), ("No list found yet", "none"))
        size = meta.get("class_size_reported")
        n = len(people)
        # ---- classmates
        cov = f"<p><strong>{n}</strong> name{'s' if n != 1 else ''} found so far"
        if size:
            cov += f" &middot; the paper reported a class of <strong>{size}</strong> ({ext(meta['class_size_source'], 'source')})"
        cov += ".</p>"
        pages = meta.get("list_pages") or []
        pl = ""
        if pages:
            pl = "<p class=\"al-small\">Where the list was printed: " + ", ".join(
                ext(u, f"page {i+1}") for i, u in enumerate(pages)) + "</p>"
        note = f'<p class="al-note">{E(meta["note"])}</p>' if meta.get("note") else ""
        items = []
        for p in people:
            s = p["sources"][0]
            kind = {"newspaper-list": "graduate list", "newspaper-photo-page": "graduation photos",
                    "wiki-list": "wiki list", "wiki-bio": "wiki biography"}.get(s["type"], "source")
            ocr = ' <span class="al-tag">OCR</span>' if s.get("ocr") or s["type"].startswith("newspaper") else ""
            items.append(f'<li><span class="al-nm">{E(p["name"])}</span>{ocr} '
                         f'<a class="al-src" href="{E(s["url"])}" target="_blank" rel="noopener" '
                         f'aria-label="Source for {E(p["name"])}: {kind}">{kind}</a></li>')
        lst = f'<ul class="al-names">{"".join(items)}</ul>' if items else \
            '<p class="al-empty">We have not found a public list of this class yet. If you have a program, yearbook page or clipping, please contact us.</p>'
        ocrnote = ""
        if any(p["sources"][0]["type"].startswith("newspaper") for p in people):
            ocrnote = ('<p class="al-small">Names marked OCR were machine-read from scans of the Adirondack Daily Enterprise '
                       '(NYS Historic Newspapers). Spellings can be off, and photo pages can pick up a stray caption or ad name. '
                       'Tap a source link to check the page. Corrections are welcome.</p>')
        # ---- facts
        gas = f["gas"]; st = f["stamp"]; mw = f["min_wage"]; br = f["bread"]; pr = f["president"]
        bread_v = money(br["price"]) + " / lb" if br["price"] else "Not tracked yet"
        bread_note = "white bread, June" if br["price"] else "BLS series starts in 1980"
        tiles = [
            ("President", E(pr["name"]), f"in office, {pr['as_of']}", pr["url"]),
            ("Gallon of gas", money(gas["price"], 2), f"{E(gas['type'])}, U.S. average", gas["url"]),
            ("First-class stamp", f"{st['cents']}&cent;", "June rate, first ounce", st["url"]),
            ("Loaf of bread", bread_v, bread_note, br["url"]),
            ("Minimum wage", money(mw["rate"]) + " / hr", "federal, June", mw["url"]),
        ]
        tile_html = "".join(
            f'<div class="al-tile"><span class="al-k">{k}</span><span class="al-v">{v}</span>'
            f'<span class="al-s">{s} &middot; {ext(u, "source")}</span></div>' for k, v, s, u in tiles)
        ws = f["world_series"]
        if ws.get("winner"):
            ws_html = f'<strong>{E(ws["winner"])}</strong> beat the {E(ws["loser"])}'
        else:
            ws_html = f'<strong>No World Series.</strong> {E(ws.get("note", ""))}'
        sb = f["super_bowl"]
        sb_html = f'<strong>{E(sb["winner"])}</strong> {E(sb["score"])} over the {E(sb["loser"])}'
        sports = f"""<div class="al-sport"><span class="al-k">World Series, fall {ws['season']}</span><p>{ws_html}. {ext(ws['url'], 'Source')}</p></div>
<div class="al-sport"><span class="al-k">{E(sb['name'])}{', ' + E(sb['played']) if y >= 1967 else ''}</span><p>{sb_html}. {ext(sb['url'], 'Source')}</p></div>"""
        songs = "".join(f'<li><span class="al-t">{E(s["title"])}</span> <span class="al-a">{E(s["artist"])}</span></li>'
                        for s in f["songs"]["list"][:10])
        films = "".join(f'<li><span class="al-t">{E(m["title"])}</span></li>' for m in f["films"]["list"][:10])
        tv = "".join(f'<li value="{t["rank"]}"><span class="al-t">{E(t["title"])}</span></li>' for t in f["tv"]["list"])
        metric = f["films"]["metric"] or "box office"
        news = "".join(f'<li>{E(x["text"])} {ext(x["url"], "More")}</li>' for x in f["news"])
        body = f"""<section class="al-hero">
  <p class="al-eyebrow">Saranac Lake High School</p>
  <h1>Class of {y}</h1>
  <p class="al-status al-st-{st_cls}">{st_label}</p>
  <p><a href="#yr">Jump to the world in {y}</a> &middot; <a href="../{year_file(y)}">Class of {y} home page</a></p>
</section>
{yr_nav(y, 'top')}
<section class="al-sec" aria-labelledby="mates">
  <h2 id="mates">Classmates found in public sources</h2>
  {cov}{pl}{note}{lst}{ocrnote}
</section>
<section class="al-sec" aria-labelledby="yr">
  <h2 id="yr">The world in {y}</h2>
  <div class="al-tiles">{tile_html}</div>
  <h3>Sports</h3>
  <div class="al-sports">{sports}</div>
  <div class="al-cols">
    <div class="al-col"><h3>Top 10 songs</h3><ol class="al-ol">{songs}</ol>
      <p class="al-small">{ext(f['songs']['url'], E(f['songs']['label']))}</p></div>
    <div class="al-col"><h3>Top 10 movies</h3><ol class="al-ol">{films}</ol>
      <p class="al-small">Ranked by {E(metric.lower())}. {ext(f['films']['url'], E(f['films']['label']))}</p></div>
    <div class="al-col"><h3>Top TV, senior year</h3><ol class="al-ol">{tv}</ol>
      <p class="al-small">{ext(f['tv']['url'], E(f['tv']['label']))}. Ties share a rank.</p></div>
  </div>
  <h3>Big news</h3>
  <ul class="al-news">{news}</ul>
  <div class="al-fun">
    <div><span class="al-k">Fad</span><p>{E(f['fad']['text'])} {ext(f['fad']['url'], 'More')}</p></div>
    <div><span class="al-k">Gadget</span><p>{E(f['gadget']['text'])} {ext(f['gadget']['url'], 'More')}</p></div>
  </div>
  <p class="al-small">Songs, movies and news are for calendar {y}. TV is the {E(f['tv']['season'])} season, the World Series is the fall of senior year and the {'Super Bowl' if y >= 1967 else 'NFL title game'} is the one played that winter. Prices are U.S. averages, not Saranac Lake prices. {ext(f['year_url'], f'More about {y} in the United States')}.</p>
</section>
{yr_nav(y, 'bottom')}"""
        return page(f"Class of {y} | Saranac Lake alumni preview", f"Saranac Lake High School Class of {y}: classmates and the world in {y}.", body)

    for y in YEARS:
        write(f"class-{y}.html", class_page(y))

    # ---- hub
    rows = []
    total = 0
    for y in YEARS:
        meta = A["years"].get(str(y), {})
        n = len(by_year.get(y, []))
        total += n
        lab, cls = STATUS.get(meta.get("list_status", "none-found"), ("No list found yet", "none"))
        size = meta.get("class_size_reported")
        rows.append(f'<li><a href="class-{y}.html"><span class="al-yr">{y}</span>'
                    f'<span class="al-cnt">{n} name{"s" if n != 1 else ""}{f" of {size}" if size else ""}</span>'
                    f'<span class="al-dot al-st-{cls}">{lab}</span></a></li>')
    media = json.loads((ROOT / "src/football_data/media.json").read_text(encoding="utf-8"))
    vids = "".join(f'<li>{ext(m["url"], E(m["title"]))} <span class="al-small">({E(m.get("length", ""))}, posted by {E(m.get("channel", ""))})</span></li>'
                   for m in media if m.get("type", "").startswith("video"))
    nvids = sum(1 for m in media if m.get("type", "").startswith("video"))
    hub = f"""<section class="al-hero">
  <p class="al-eyebrow">Saranac Lake High School alumni</p>
  <h1>Classes of 1960 to 2000</h1>
  <p>Classmates found in public records, and what the world looked like the year each class graduated. Every name and fact links to its source.</p>
</section>
<section class="al-sec">
  <div class="al-cta">
    <a class="al-btn" href="card.html">Make a football card</a>
    <a class="al-btn al-btn-2" href="signup.html">Alumni sign-up (preview)</a>
  </div>
  <h2>Pick a class</h2>
  <p>{total:,} names so far across 41 classes. Some classes have a full list, some have none yet.</p>
  <ul class="al-years">{''.join(rows)}</ul>
  <h2>Game video</h2>
  <details class="al-vids"><summary>{nvids} Redskins football videos already posted publicly on YouTube</summary>
  <ul class="al-news">{vids}</ul></details>
  <p class="al-small">Cut-down highlight clips are not made yet. They need the original tapes or the copies on the home NAS, which were not reachable for this preview.</p>
  <h2>Where the names come from</h2>
  <ul class="al-news">
    <li>Graduate lists and graduation photo pages printed each June in the {ext('https://www.nyshistoricnewspapers.org/titles/place/new_york_franklin_saranaclake/', 'Adirondack Daily Enterprise')} (NYS Historic Newspapers). These were machine-read (OCR), so spellings can be off.</li>
    <li>Biographies and lists on the {ext('https://wiki.historicsaranaclake.org/', 'Historic Saranac Lake wiki')}.</li>
    <li>Nothing is guessed. If a list was too garbled to read safely, the class page links to the scan instead.</li>
  </ul>
  <p class="al-small">Missing or misspelled? Email {ext('mailto:plinymiller@gmail.com?subject=Alumni%20list%20correction', 'plinymiller@gmail.com')}.</p>
</section>"""
    write("index.html", page("Alumni preview | Saranac Lake Redskins", "Unpublished alumni preview.", hub))

    # ---- card maker
    card = """<section class="al-hero al-hero-sm">
  <p class="al-eyebrow">Redskins football</p>
  <h1>Make a football card</h1>
  <p>Look up a player, check every stat and mention we found, pick or upload a photo, then download your card as a PNG. Inspired by 1970s cards. Not affiliated with any card company.</p>
</section>
<section class="al-sec al-card-app">
  <div class="al-card-left">
    <label for="al-q" class="al-lbl">Find a player</label>
    <input id="al-q" type="search" autocomplete="off" placeholder="Try Shane Graham" aria-describedby="al-q-help" aria-controls="al-results">
    <p id="al-q-help" class="al-small">Search 409 players from rosters, the football history pages and newspaper stories.</p>
    <ul id="al-results" class="al-results" aria-live="polite"></ul>
    <div id="al-player" class="al-player" hidden></div>
  </div>
  <div class="al-card-right">
    <div class="al-canvas-wrap">
      <canvas id="al-front" width="750" height="1050" role="img" aria-label="Card front preview"></canvas>
      <canvas id="al-back" width="1050" height="750" role="img" aria-label="Card back preview"></canvas>
    </div>
    <fieldset class="al-fields">
      <legend>Card details</legend>
      <label>Name on card<input id="f-name" maxlength="28"></label>
      <div class="al-row">
        <label>Position<input id="f-pos" maxlength="4" placeholder="RB"></label>
        <label>Number<input id="f-num" maxlength="3" inputmode="numeric"></label>
        <label>Season<input id="f-year" maxlength="4" inputmode="numeric"></label>
      </div>
      <label>Class of<input id="f-class" maxlength="4" inputmode="numeric"></label>
      <label>Card back notes (one per line)<textarea id="f-notes" rows="5"></textarea></label>
    </fieldset>
    <fieldset class="al-fields">
      <legend>Photo</legend>
      <div id="al-photos" class="al-photos"></div>
      <label class="al-upload">Upload your own photo<input id="f-upload" type="file" accept="image/*"></label>
      <p class="al-small">Your photo stays on your device. It is never uploaded.</p>
      <div class="al-row">
        <label>Zoom<input id="f-zoom" type="range" min="1" max="3" step="0.01" value="1"></label>
        <label>Left / right<input id="f-x" type="range" min="-1" max="1" step="0.01" value="0"></label>
        <label>Up / down<input id="f-y" type="range" min="-1" max="1" step="0.01" value="0"></label>
      </div>
    </fieldset>
    <div class="al-cta">
      <button id="dl-front" class="al-btn" type="button">Download front (PNG)</button>
      <button id="dl-back" class="al-btn al-btn-2" type="button">Download back (PNG)</button>
    </div>
    <p class="al-small">Sample: <a href="sample/shane-graham-front.png">Shane Graham card front</a> &middot; <a href="sample/shane-graham-back.png">back</a></p>
  </div>
</section>"""
    write("card.html", page("Football card maker | Saranac Lake alumni preview", "Make a Saranac Lake Redskins football card.", card, js="alumni-card.js", cls="al-cardpage"))

    # ---- sign-up preview
    yopts = "".join(f'<option value="{y}">{y}</option>' for y in range(2000, 1889, -1))
    signup = f"""<section class="al-hero al-hero-sm">
  <p class="al-eyebrow">Alumni sign-up</p>
  <h1>Join your class</h1>
  <p>Sign-up is not open yet. This page shows how it will work.</p>
</section>
<section class="al-sec al-narrow">
  <div class="al-rules" id="rules">
    <h2>Be a good neighbor</h2>
    <ul>
      <li>Be kind and respectful. No harassment, hate, threats or bullying.</li>
      <li>Only post what is yours to share. Respect classmates' privacy.</li>
      <li>No spam, ads, scams or selling.</li>
      <li>Keep it about Saranac Lake, your class and your memories.</li>
    </ul>
    <p>This is an unpaid community site run by volunteers. Any user may be banned at any time.</p>
  </div>
  <form id="al-signup" class="al-form" novalidate>
    <div class="al-row">
      <label>First name<input name="first" autocomplete="given-name" required maxlength="40"></label>
      <label>Last name<input name="last" autocomplete="family-name" required maxlength="60"></label>
    </div>
    <label>Last name in high school, if different<input name="school_last" maxlength="60"></label>
    <label>Class year<select name="class_year" required><option value="">Choose a year</option>{yopts}</select></label>
    <label>Email<input name="email" type="email" autocomplete="email" required maxlength="120"></label>
    <div class="al-hp" aria-hidden="true"><label>Leave this empty<input name="website" tabindex="-1" autocomplete="off"></label></div>
    <div class="al-captcha" data-sitekey="TURNSTILE_SITE_KEY">Spam check goes here (Cloudflare Turnstile or hCaptcha)</div>
    <label class="al-check"><input type="checkbox" name="agree" required> I agree to be a good neighbor and understand any user may be banned at any time.</label>
    <button class="al-btn" type="submit" disabled aria-disabled="true">Sign-up opens soon</button>
    <p class="al-small">How it works: we check your name and class year against our list. A match gets a verification email. Anything that does not match goes to a person for review, so you can still join if we are missing you.</p>
  </form>
</section>"""
    write("signup.html", page("Alumni sign-up (preview) | Saranac Lake Redskins", "Alumni sign-up preview.", signup))
