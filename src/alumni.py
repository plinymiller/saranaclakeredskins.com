"""Alumni pages: hub and class-of pages for 1960-2000.

Writes /alumni/: a hub and class-of pages for 1960-2000. Data: data/alumni.json (public-source names), src/alumni_data/years.json
(cited year facts), alumni/data/football/ (football mentions index).
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "alumni"
YEARS = range(2000, 1959, -1)
ROBOTS = None  # published: indexable


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
    by_year = {}
    for p in A["people"]:
        by_year.setdefault(p["class_year"], []).append(p)

    def page(title, desc, body, js=None, cls=""):
        chrome = up(head(title, desc, robots=ROBOTS)).replace(
            "</head>", '<link rel="stylesheet" href="../assets/alumni.css?v=1">\n</head>')
        script = f'\n<script src="../assets/{js}?v=1" defer></script>' if js else ""
        return chrome + f"""<body class="al {cls}">
{up(header(None))}
<main id="main">
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
        return page(f"Class of {y} | Saranac Lake Redskins", f"Saranac Lake High School Class of {y}: classmates and the world in {y}.", body)

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
  <h2>Pick a class</h2>
  <p>{total:,} names so far across 41 classes. Some classes have a full list, some have none yet.</p>
  <ul class="al-years">{''.join(rows)}</ul>
  <h2>Game video</h2>
  <details class="al-vids"><summary>{nvids} Redskins football videos already posted publicly on YouTube</summary>
  <ul class="al-news">{vids}</ul></details>
  <h2>Where the names come from</h2>
  <ul class="al-news">
    <li>Graduate lists and graduation photo pages printed each June in the {ext('https://www.nyshistoricnewspapers.org/titles/place/new_york_franklin_saranaclake/', 'Adirondack Daily Enterprise')} (NYS Historic Newspapers). These were machine-read (OCR), so spellings can be off.</li>
    <li>Biographies and lists on the {ext('https://wiki.historicsaranaclake.org/', 'Historic Saranac Lake wiki')}.</li>
    <li>Nothing is guessed. If a list was too garbled to read safely, the class page links to the scan instead.</li>
  </ul>
  <p class="al-small">Missing or misspelled? Email {ext('mailto:plinymiller@gmail.com?subject=Alumni%20list%20correction', 'plinymiller@gmail.com')}.</p>
</section>"""
    write("index.html", page("Classmates and class years, 1960-2000 | Saranac Lake Redskins", "Saranac Lake High School classmates found in public records, and the world the year each class graduated, 1960 to 2000.", hub))
