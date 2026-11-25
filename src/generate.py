#!/usr/bin/env python3
"""Generate static HTML pages for saranaclakeredskins.com."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTACT = "plinymiller@gmail.com"
MAIL = "mailto:plinymiller@gmail.com?subject=Saranac%20Lake%20alumni%20site"
CREDIT = "a <a href=\"https://plinymiller.com\" target=\"_blank\" rel=\"noopener\">plinymiller design</a> \u2013 a <a href=\"https://b-tuff.co\" target=\"_blank\" rel=\"noopener\">B-Tuff Company</a>"
KOFI = "https://ko-fi.com/plinymiller"
SUPPORT_BLURB = "This site is a volunteer labor of love. Contributions help cover web hosting, the domain, and upkeep \u2014 nothing more. This site is not a nonprofit, and contributions are not tax-deductible."
FIRST, LAST = 1890, 2000
FONTS = "https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400;1,8..60,600&display=swap"


def year_file(y: int) -> str:
    if y == 2000:
        return "00.html"
    if 1960 <= y <= 1999:
        return f"{y % 100:02d}.html"
    return f"{y}.html"


def year_mark(y: int) -> str:
    if 1960 <= y <= 2000:
        return f"\u2019{y % 100:02d}"
    return str(y)


SITE = "https://saranaclakeredskins.com"
OG_DEFAULT = "An independent alumni project for Saranac Lake High School classes of 1890 to 2000."


def head(title: str, description: str | None = None, robots: str | None = None) -> str:
    desc = f'<meta name="description" content="{description}">\n' if description else ""
    og_desc = description or OG_DEFAULT
    og = (f'<meta property="og:type" content="website">\n'
          f'<meta property="og:site_name" content="Saranac Lake Redskins">\n'
          f'<meta property="og:title" content="{title}">\n'
          f'<meta property="og:description" content="{og_desc}">\n'
          f'<meta property="og:image" content="{SITE}/assets/og-card.png?v=4">\n'
          f'<meta property="og:image:width" content="1200">\n'
          f'<meta property="og:image:height" content="630">\n'
          f'<meta property="og:image:alt" content="Saranac Lake Redskins badge">\n'
          f'<meta name="twitter:card" content="summary_large_image">\n')
    rob = f'<meta name="robots" content="{robots}">\n' if robots else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{desc}{rob}{og}<meta name="theme-color" content="#FFFFFF">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png">
<link rel="icon" type="image/png" sizes="192x192" href="assets/icon-192.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="assets/class.css">
<link rel="stylesheet" href="assets/site.css?v=1">
<script>document.documentElement.classList.add("js")</script>
<script src="assets/site.js?v=1" defer></script>
</head>
"""


SITE_TITLE = "Saranac Lake Redskins"
SECTIONS = [
    ("sports", "sports.html", "Sports"),
    ("arts", "arts.html", "Arts"),
    ("news", "news.html", "News"),
    ("memoriam", "in-memoriam.html", "In Memoriam"),
]

# Top menu, in the owner's order. Sub-menus are disclosure lists (not ARIA menus).
NAV = [
    ("home", "index.html", "Home", None),
    ("news", "news.html", "News", None),
    ("classes", "classes.html", "Find Your Class", [
        ("classes.html", "Pick your class year", "Every class from 1890 to 2000"),
        ("alumni/index.html", "Classmates &amp; the year you graduated", "Names from public records, 1960 to 2000"),
        ("welcome.html", "My class home", "For members who have signed up"),
    ]),
    ("sports", "sports.html", "Sports", [
        ("sports.html", "All sports", "Teams, seasons and coaches"),
        ("football/index.html", "Football: The Film Room", "Every game since 1923, with film"),
        ("football/index.html#scoreboard", "Football scoreboard", "Scores and newspaper write-ups"),
        ("football/players.html", "Football players", "Rosters, captains and honors"),
    ]),
    ("arts", "arts.html", "Arts", None),
    ("memoriam", "in-memoriam.html", "In Memoriam", None),
    ("shop", "shop.html", "Shop", None),
    ("contact", "contact.html", "Contact Us", None),
]
GROUP = {"football": "sports", "alumni": "classes", "classes-year": "classes"}


def header(current: str | None = None, extra: str = "", home: bool = False) -> str:
    cur = GROUP.get(current, current)
    items = []
    for key, href, label, sub in NAV:
        here = ' aria-current="page"' if current == key else (' aria-current="true"' if cur == key else "")
        if not sub:
            items.append(f'<li><a class="nav-a" href="{href}"{here}>{label}</a></li>')
            continue
        sid = f"sub-{key}"
        subs = "".join(
            f'<li><a href="{h}"{" aria-current=\"page\"" if (current == "football" and h == "football/index.html") else ""}>'
            f'<span class="sub-t">{t}</span><span class="sub-d">{d}</span></a></li>' for h, t, d in sub)
        items.append(
            f'<li class="has-sub"><a class="nav-a" href="{href}"{here}>{label}</a>'
            f'<button class="sub-btn" type="button" aria-expanded="false" aria-controls="{sid}">'
            f'<span class="sr-only">{label} pages</span><svg aria-hidden="true" width="12" height="12" viewBox="0 0 12 12"><path d="M2 4.5l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6"/></svg></button>'
            f'<ul class="sub" id="{sid}">{subs}</ul></li>')
    extra_html = f'<div class="top-extra">{extra}</div>' if extra else ""
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="masthead" id="top">
  <div class="mast-row">
    <a class="brand" href="index.html">
      <img src="assets/logo-badge.svg" width="48" height="48" alt="{BADGE_ALT}">
      <span class="brand-words"><span class="brand-kicker">Saranac Lake High School &middot; Alumni</span><span class="brand-title">{SITE_TITLE}</span></span>
    </a>
    {extra_html}
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav"><span class="menu-ic" aria-hidden="true"></span><span class="menu-l">Menu</span></button>
    <nav class="site-nav" id="site-nav" aria-label="Main">
      <ul class="nav-list">{''.join(items)}</ul>
    </nav>
  </div>
</header>
"""


BADGE_ALT = "Saranac Lake Redskins badge"
LOGO_NOTICE = "This site is not affiliated with or endorsed by the Washington Commanders (formerly the Washington Redskins) or the NFL."


def divider() -> str:
    return ('<div class="brand-divider" aria-hidden="true"><span></span>'
            '<img src="assets/mark-red.svg" width="56" height="62" alt=""><span></span></div>')


def footer(logo_notice: bool = False) -> str:
    notice = f'\n    <p class="logo-notice">{LOGO_NOTICE}</p>' if logo_notice else ""
    explore = "".join(f'<li><a href="{h}">{l}</a></li>' for k, h, l, _ in NAV if k != "home")
    return f"""<footer class="site-foot">
  <div class="foot">
    <div class="foot-brand">
      <img class="foot-mark" src="assets/mark-maroon.svg" width="40" height="45" alt="">
      <p><strong>Saranac Lake Redskins</strong><br>An independent alumni project for Saranac Lake High School classes of 1890 to 2000.</p>
    </div>
    <nav aria-label="Footer: explore"><h2 class="foot-h">Explore</h2><ul>{explore}<li><a href="football/index.html">Football</a></li></ul></nav>
    <nav aria-label="Legal"><h2 class="foot-h">This site</h2><ul>
      <li><a href="support.html">Support</a></li>
      <li><a href="privacy.html">Privacy</a></li>
      <li><a href="terms.html">Terms</a></li>
      <li><a href="{MAIL}">{CONTACT}</a></li>
    </ul></nav>
  </div>
  <div class="foot-base">
    <p>Questions, corrections, or to have your account and details removed: <a href="contact.html">contact us</a>.</p>
    <p class="credit">{CREDIT}</p>{notice}
  </div>
</footer>
"""


def write(name: str, html: str) -> None:
    path = ROOT / name
    path.write_text(html, encoding="utf-8")
    print(f"wrote {name} ({path.stat().st_size} bytes)")


def _site_stats():
    import json as _j
    D = ROOT / "src" / "football_data"
    games = _j.loads((D / "games.json").read_text(encoding="utf-8"))
    seasons = _j.loads((D / "seasons.json").read_text(encoding="utf-8"))
    media = _j.loads((D / "media.json").read_text(encoding="utf-8"))
    fb = {
        "games": len(games),
        "seasons": sum(1 for x in seasons if x.get("games_found")),
        "films": sum(1 for x in media if str(x.get("type", "")).startswith("video")),
        "titles": sum(1 for x in seasons if x.get("championship")),
    }
    al = {"names": 0, "years": {}}
    try:
        A = _j.loads((ROOT / "data" / "alumni.json").read_text(encoding="utf-8"))
        al["names"] = len(A.get("people", []))
        Y = _j.loads((ROOT / "src" / "alumni_data" / "years.json").read_text(encoding="utf-8"))
        for y in ("1970", "1988", "2000"):
            f = Y[y]
            song = f["songs"]["list"][0]
            al["years"][y] = (song["title"], song["artist"], f["gas"]["price"], f["films"]["list"][0]["title"])
    except Exception:
        pass
    return fb, al


def index_page() -> str:
    fb, al = _site_stats()
    decades = "".join(
        f'<li><a href="classes.html#d{d}" aria-label="Classes of the {d}s"><span class="dec-n">{d}<small>s</small></span></a></li>'
        for d in range(1890, 2000, 10)) + '<li><a href="classes.html#d2000" aria-label="Class of 2000"><span class="dec-n">2000</span></a></li>'
    years = "".join(
        f'<li><a href="alumni/class-{y}.html"><span class="yr">{y}</span>'
        f'<span class="yr-row"><span class="yr-k">No. 1 song</span> &ldquo;{t}&rdquo; <span class="yr-by">{ar}</span></span>'
        f'<span class="yr-row"><span class="yr-k">Top movie</span> {mv}</span>'
        f'<span class="yr-row"><span class="yr-k">Gallon of gas</span> ${g:.2f}</span></a></li>'
        for y, (t, ar, g, mv) in al["years"].items())
    return head(
        "Home of the Saranac Lake Redskins",
        "An independent alumni project for Saranac Lake High School classes of 1890 to 2000. Find your class, sign in, and reconnect.",
    ) + f"""<body class="home">
{header("home", home=True)}
<main id="main">
  <section class="h-hero" aria-labelledby="h-title">
    <div class="h-hero-copy">
      <p class="kicker">Saranac Lake High School &middot; Classes of 1890&ndash;2000</p>
      <h1 id="h-title">Welcome home, <em>alumni.</em></h1>
      <p class="lede">An independent alumni project for every class from 1890 to 2000. Find your class bulletin board and classmate directory, catch reunion news, and dig into a century of Redskins history.</p>
      <form class="yearjump" action="classes.html" data-yearjump>
        <label for="yj">What year did you graduate?</label>
        <div class="yj-row">
          <input id="yj" name="year" inputmode="numeric" pattern="[0-9]{{4}}" maxlength="4" placeholder="1988" autocomplete="off" aria-describedby="yj-msg">
          <button class="btn" type="submit">Go to my class</button>
        </div>
        <p class="yj-msg" id="yj-msg" role="status">Or <a href="classes.html">browse every class</a>.</p>
      </form>
    </div>
    <div class="h-hero-art">
      <div class="logo-wrap">
        <img src="assets/logo-badge.svg" width="1480" height="1480" alt="{BADGE_ALT}" fetchpriority="high">
        <a href="88.html" class="feather-tip" aria-label="Class of 1988"></a>
      </div>
    </div>
  </section>

  <section class="h-decades" aria-labelledby="dec-h">
    <h2 id="dec-h" class="kicker">Jump to a decade</h2>
    <ol class="decades-strip">{decades}</ol>
  </section>

  <section class="h-feature" aria-labelledby="fb-h">
    <figure class="h-feature-img">
      <img src="football/img/1925_SLHS_Football.jpg" width="1158" height="620" alt="The 1925 Saranac Lake High School football team posing in uniform" loading="lazy">
      <figcaption>The 1925 team, from the 1926 <i>Canaras</i> yearbook.</figcaption>
    </figure>
    <div class="h-feature-copy">
      <p class="kicker">Sports &middot; Football since 1923</p>
      <h2 id="fb-h">The Film Room</h2>
      <p>Every game we can find, from the first kickoff against Mineville in 1923 to today: scores, newspaper write-ups, rosters, team photos and game film.</p>
      <dl class="figures">
        <div><dt>Games</dt><dd>{fb["games"]}</dd></div>
        <div><dt>Seasons</dt><dd>{fb["seasons"]}</dd></div>
        <div><dt>Films</dt><dd>{fb["films"]}</dd></div>
        <div><dt>Title seasons</dt><dd>{fb["titles"]}</dd></div>
      </dl>
      <p class="links"><a class="btn" href="football/index.html">Enter the Film Room</a> <a class="text-link" href="football/index.html#scoreboard">Scoreboard</a> <a class="text-link" href="football/players.html">Players</a></p>
    </div>
  </section>

  <section class="h-years" aria-labelledby="yrs-h">
    <div class="h-years-head">
      <p class="kicker">Classmates &amp; the year you graduated</p>
      <h2 id="yrs-h">What was playing when you walked</h2>
      <p>{al["names"]:,} classmates found so far in public records for the classes of 1960 to 2000, plus the songs, movies, prices and headlines of each graduation year.</p>
      <p><a class="text-link strong" href="alumni/index.html">See all 41 class years</a></p>
    </div>
    <ol class="yr-list">{years}</ol>
  </section>

  <section class="h-index" aria-labelledby="more-h">
    <h2 id="more-h" class="kicker">Also on the site</h2>
    <ul class="index-list">
      <li><a href="news.html"><span class="ix-t">Alumni news</span><span class="ix-d">Reunions, milestones and updates from Saranac Lake alumni.</span></a></li>
      <li><a href="arts.html"><span class="ix-t">Arts and music</span><span class="ix-d">Band, chorus, drama, art and the stage crews behind them.</span></a></li>
      <li class="quiet"><a href="in-memoriam.html"><span class="ix-t">In memoriam</span><span class="ix-d">Remembering classmates, teachers and coaches.</span></a></li>
      <li><a href="shop.html"><span class="ix-t">Shop</span><span class="ix-d">Alumni gear and archival prints, coming soon.</span></a></li>
    </ul>
  </section>

  <section class="h-close" id="support" aria-label="Share news and support">
    <div>
      <h2>Have class news?</h2>
      <p>Reunion dates, photos, and class group links will be posted here. To share one, <a href="{MAIL}">email us</a> at {CONTACT}.</p>
    </div>
    <div>
      <h2 id="support-heading">Support this site</h2>
      <p>{SUPPORT_BLURB}</p>
      <p><a class="btn ghost" href="{KOFI}" target="_blank" rel="noopener">Support on Ko-fi</a></p>
    </div>
  </section>
</main>
{footer(logo_notice=True)}
</body>
</html>
"""


def classes_page() -> str:
    jumps = []
    decades = []
    # 1890s through 1990s, then 2000
    for start in range(1890, 2000, 10):
        end = start + 9
        label = f"The {start}s"
        hid = f"d{start}"
        short = f"{start}s"
        jumps.append(f'<a href="#{hid}">{short}</a>')
        years = "".join(
            f'<a href="{year_file(y)}" aria-label="Class of {y}">{y}</a>'
            for y in range(start, end + 1)
        )
        # Open 1950s–1990s by default (living alumni are most likely here)
        opened = " open" if start >= 1950 else ""
        decades.append(
            f'<details class="decade" id="{hid}"{opened}><summary>{label}</summary><div class="years">{years}</div></details>'
        )
    jumps.append('<a href="#d2000">2000</a>')
    decades.append(
        f'<details class="decade" id="d2000" open><summary>2000</summary>'
        f'<div class="years"><a href="{year_file(2000)}" aria-label="Class of 2000">2000</a></div></details>'
    )
    return head(
        "Find Your Class | Saranac Lake Redskins",
        "Saranac Lake High School alumni, classes of 1890 to 2000. Pick your graduation year to join your class.",
    ) + f"""<body>
{header("classes", extra='<a class="btn ghost hide-sm" href="welcome.html">My class home</a>')}
<main id="main" class="wrap">
  <header class="pagehead">
    <span class="label">Saranac Lake High School alumni</span>
    <h1>Find your class</h1>
    <p class="lede">Pick the year you graduated. Each class has its own bulletin board and directory, and there is one board that every class shares.</p>
    <p>New: <a href="alumni/index.html">classmates found in public records, and the world the year you graduated (1960 to 2000)</a>.</p>
  </header>
  <nav class="decade-jump" aria-label="Jump to a decade">
    {''.join(jumps)}
  </nav>
  <div class="decades">
    {''.join(decades)}
  </div>
</main>
{footer()}
</body>
</html>
"""


def class_page(year: int) -> str:
    mark = year_mark(year)
    yy = year % 100 if year >= 1960 else year
    # typographic big mark uses the same short form when unambiguous
    big = mark
    return head(
        f"Class of {year} | Saranac Lake Redskins",
        f"Saranac Lake High School Class of {year}. Sign in for your class bulletin board, the classmate directory and reunion news.",
    ) + f"""<body>
{header("classes-year")}
<main id="main" class="wrap">
  <section class="desk" id="viewOut">
    <div class="intro">
      <p class="big" aria-hidden="true">{big}</p>
      <span class="label">Saranac Lake High School</span>
      <h1>Class of {year}</h1>
      <ol class="steps">
        <li><b>1</b><span>Create your account. It takes about a minute.</span></li>
        <li><b>2</b><span>Open the link we email you.</span></li>
        <li><b>3</b><span>Post on the Class of {year} board, find classmates, and say hello to every class.</span></li>
      </ol>
      <p class="pick">Not the Class of {year}? <a href="classes.html">Pick your year</a>.</p>
    </div>

    <div class="card">
      <p class="msg note" id="offNote" hidden>Sign-up is not switched on yet. Check back soon.</p>
      <div class="tabs" role="tablist">
        <button type="button" role="tab" id="tabUp" aria-selected="true" aria-controls="formUp">Create account</button>
        <button type="button" role="tab" id="tabIn" aria-selected="false" aria-controls="formIn">Log in</button>
      </div>
      <form id="formUp" novalidate>
        <div class="row">
          <div class="f"><label for="upFirst">First name</label><input type="text" id="upFirst" autocomplete="given-name" required></div>
          <div class="f"><label for="upLast">Last name</label><input type="text" id="upLast" autocomplete="family-name" required></div>
        </div>
        <div class="f"><label for="upGrad">Name at graduation <i>(if different)</i></label><input type="text" id="upGrad"></div>
        <div class="row">
          <div class="f"><label for="upUser">Username</label><input type="text" id="upUser" autocomplete="username" required minlength="3" maxlength="24" pattern="[A-Za-z0-9_.\\-]+"></div>
          <div class="f"><label for="upPass">Password <i>(8 or more characters)</i></label><input type="password" id="upPass" autocomplete="new-password" required minlength="8"></div>
        </div>
        <div class="row">
          <div class="f"><label for="upEmail">Email</label><input type="email" id="upEmail" autocomplete="email" required></div>
          <div class="f"><label for="upCell">Cell phone</label><input type="tel" id="upCell" autocomplete="tel" required></div>
        </div>
        <fieldset>
          <legend>Mailing address, optional</legend>
          <div class="f"><label for="upStreet">Street</label><input type="text" id="upStreet" autocomplete="street-address"></div>
          <div class="row three">
            <div class="f"><label for="upCity">City</label><input type="text" id="upCity" autocomplete="address-level2"></div>
            <div class="f"><label for="upState">State</label><input type="text" id="upState" autocomplete="address-level1"></div>
            <div class="f"><label for="upZip">ZIP</label><input type="text" id="upZip" autocomplete="postal-code"></div>
          </div>
        </fieldset>
        <label class="check" for="upListed"><input type="checkbox" id="upListed"><span>List my name and city in the classmate directory.</span></label>
        <label class="check" for="upShowEmail"><input type="checkbox" id="upShowEmail"><span>Show my email to classmates in the directory.</span></label>
        <label class="check" for="upShowCell"><input type="checkbox" id="upShowCell"><span>Show my cell number to classmates in the directory.</span></label>
        <label class="check" for="upConsent"><input type="checkbox" id="upConsent" required><span>I agree that the class organizers may contact me about class news and reunions using the details above.</span></label>
        <p class="msg" id="upMsg" hidden role="status"></p>
        <button class="btn" type="submit" id="upBtn">Create account</button>
        <p class="small">Your email, cell number and mailing address are seen only by the class organizers unless you tick the boxes above. They are never sold or shared outside the class. See our <a href="privacy.html">Privacy</a> page for details.</p>
      </form>

      <form id="formIn" hidden novalidate>
        <div class="f"><label for="inEmail">Email</label><input type="email" id="inEmail" autocomplete="email" required></div>
        <div class="f"><label for="inPass">Password</label><input type="password" id="inPass" autocomplete="current-password" required></div>
        <p class="msg" id="inMsg" hidden role="status"></p>
        <button class="btn" type="submit" id="inBtn">Log in</button>
        <button class="link" type="button" id="forgot">Forgot your password?</button>
      </form>
    </div>
  </section>

  <section class="desk" id="viewReset" hidden>
    <div class="intro"><p class="big" aria-hidden="true">{big}</p><h1>Choose a new password</h1></div>
    <div class="card">
      <form id="formReset" novalidate>
        <div class="f"><label for="rsPass">New password <i>(8 or more characters)</i></label><input type="password" id="rsPass" autocomplete="new-password" required minlength="8"></div>
        <p class="msg" id="rsMsg" hidden role="status"></p>
        <button class="btn" type="submit">Save password</button>
      </form>
    </div>
  </section>
</main>
{footer()}
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.js"></script>
<script src="assets/config.js"></script>
<script>var CLASS_YEAR = {year};</script>
<script src="assets/signin.js"></script>
</body>
</html>
"""


def welcome_page() -> str:
    extra = """<div class="who" id="who" hidden><span id="whoName"></span><button class="btn ghost" id="signOut" type="button">Sign out</button></div>"""
    return head("My Class Home | Saranac Lake Redskins", robots="noindex") + f"""<body>
{header(extra=extra)}
<main id="main">
<div class="wrap" id="page" hidden>
  <section class="hello">
    <div>
      <span class="label">Saranac Lake High School</span>
      <h1>Welcome to the virtual home of the <em>Class of <span id="yrTitle"></span></em></h1>
      <p>We&rsquo;re in the process of building this site. Please pass on the site info to fellow classmates, and feel free to leave a message on the bulletin board below or search the directory for classmates.</p>
      <p class="t-welcome-link"><strong>New:</strong> <a href="teachers/index.html">Teachers</a>, stories and photos of the teachers who shaped SLHS, for members.</p>
    </div>
    <div class="share">
      <span class="label">Pass it on</span>
      <code id="shareLink"></code>
      <button class="btn ghost" id="copyLink" type="button">Copy the link</button>
    </div>
  </section>

  <section class="rooms">
    <p class="msg note" id="pending" hidden>You&rsquo;re in. Classmates&rsquo; email addresses, cell numbers and class photos open up once an organizer confirms your class.</p>

    <div class="room" id="board">
      <header><h2>Bulletin board</h2><span class="label" id="postCount"></span></header>
      <div class="roombar">
        <div class="seg" role="group" aria-label="Choose a board">
          <button type="button" id="bdClass" aria-pressed="true"></button>
          <button type="button" id="bdAll" aria-pressed="false">All classes</button>
        </div>
        <p class="posting" id="postingTo"></p>
      </div>
      <form id="formPost" novalidate>
        <div class="f"><label for="postBody" id="postLabel">Leave a message</label><textarea id="postBody" maxlength="1000" required></textarea></div>
        <p class="msg" id="postMsg" hidden role="status"></p>
        <div class="postbar"><button class="btn" type="submit" id="postBtn">Post message</button><span class="small" id="postLeft">1000 characters left</span></div>
      </form>
      <div class="board" id="postList"></div>
      <p class="empty" id="postEmpty">No messages yet. Be the first to say hello.</p>
    </div>

    <div class="room" id="roomDir">
      <header><h2>Directory</h2><span class="label" id="dirCount"></span></header>
      <div class="roombar">
        <div class="seg" role="group" aria-label="Choose a directory">
          <button type="button" id="drClass" aria-pressed="true"></button>
          <button type="button" id="drAll" aria-pressed="false">All classes</button>
        </div>
        <div class="f search" style="margin:0;flex:1 1 260px"><label for="dirSearch">Search by name or city</label><input type="text" id="dirSearch" autocomplete="off"></div>
      </div>
      <div class="dir-cards" id="dirCards"></div>
      <div class="scroll"><table class="dir" id="dirTable" hidden><thead><tr><th scope="col">Name</th><th scope="col" id="thClass">Class</th><th scope="col">City</th><th scope="col">Email</th><th scope="col">Cell</th></tr></thead><tbody></tbody></table></div>
      <p class="empty" id="dirEmpty">No one listed yet.</p>
    </div>

    <div class="room news">
      <header><h2>Reunion news</h2><span class="label">From the organizers</span></header>
      <div id="newsList"><p class="empty">No news posted yet. Reunion dates will appear here when organizers share them.</p></div>
    </div>

    <div class="room" id="roomPhotos">
      <header><h2>Class photos</h2><span class="label" id="photoLabel"></span></header>
      <div class="photos" id="photoGrid"></div>
      <p class="empty" id="photoEmpty">No photos posted yet. Send yours to <a href="{MAIL}">{CONTACT}</a>.</p>
    </div>

    <div class="room">
      <header><h2>Your details</h2><span class="label" id="meUser"></span></header>
      <form id="formMe" class="card" novalidate>
        <div class="row">
          <div class="f"><label for="meFirst">First name</label><input type="text" id="meFirst" required></div>
          <div class="f"><label for="meLast">Last name</label><input type="text" id="meLast" required></div>
        </div>
        <div class="f"><label for="meGrad">Name at graduation <i>(if different)</i></label><input type="text" id="meGrad"></div>
        <div class="f"><label for="meCell">Cell phone</label><input type="tel" id="meCell" required></div>
        <fieldset>
          <legend>Mailing address, optional</legend>
          <div class="f"><label for="meStreet">Street</label><input type="text" id="meStreet"></div>
          <div class="row three">
            <div class="f"><label for="meCity">City</label><input type="text" id="meCity"></div>
            <div class="f"><label for="meState">State</label><input type="text" id="meState"></div>
            <div class="f"><label for="meZip">ZIP</label><input type="text" id="meZip"></div>
          </div>
        </fieldset>
        <label class="check" for="meListed"><input type="checkbox" id="meListed"><span>List my name and city in the classmate directory.</span></label>
        <label class="check" for="meShowEmail"><input type="checkbox" id="meShowEmail"><span>Show my email to classmates in the directory.</span></label>
        <label class="check" for="meShowCell"><input type="checkbox" id="meShowCell"><span>Show my cell number to classmates in the directory.</span></label>
        <p class="msg" id="meMsg" hidden role="status"></p>
        <button class="btn" type="submit">Save changes</button>
      </form>
    </div>
  </section>
</div>
</main>
{footer()}
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.js"></script>
<script src="assets/config.js"></script>
<script src="assets/home.js"></script>
</body>
</html>
"""


def privacy_page() -> str:
    return head(
        "Privacy | Saranac Lake Redskins",
        "How saranaclakeredskins.com collects, stores, and shares alumni account information.",
    ) + f"""<body>
{header()}
<main id="main" class="wrap prose">
  <span class="label">Saranac Lake Redskins</span>
  <h1>Privacy</h1>
  <p>saranaclakeredskins.com is an independent alumni project for Saranac Lake High School classes of 1890 to 2000. It is not an official site of the school district. Questions about this policy, or requests to have your account and details removed, can be sent to <a href="{MAIL}">{CONTACT}</a>.</p>

  <h2>What we collect</h2>
  <p>When you create an account we ask for your first name, last name, name at graduation (if different), a username, email address, cell phone number, and an optional mailing address (street, city, state, and ZIP). You also choose a password and tell us whether to list your name and city, email, or cell number in the classmate directory. If you post on a bulletin board, we store the message you write. If you send class photos to us, we may store and display the image and any caption you provide.</p>

  <h2>How it is stored</h2>
  <p>Account, directory, message, and photo information is stored with Supabase, a cloud database and sign-in service we use to run the site. Your password is handled by that service; we do not keep it in plain text. Your browser also holds a sign-in session so you can stay logged in.</p>

  <h2>Who can see it</h2>
  <p>Class organizers can see the contact details you provide so they can reach you about class news and reunions. Classmates see your email address or cell number only if you tick those boxes, and only after an organizer confirms that you belong to the class. Your name and city appear in the directory only if you choose to be listed. Bulletin board messages are visible to signed-in classmates on the board you post to. We do not sell your information, and we do not share it outside the class except as needed to operate the site or as required by law.</p>

  <h2>Removal and corrections</h2>
  <p>You can update your details while signed in. To have your account and details removed, or to correct something you cannot change yourself, email <a href="{MAIL}">{CONTACT}</a>.</p>

  <h2>Changes</h2>
  <p>If this policy changes, we will post the update on this page.</p>
</main>
{footer()}
</body>
</html>
"""


def terms_page() -> str:
    return head(
        "Terms | Saranac Lake Redskins",
        "Terms of use and disclaimer for the Saranac Lake Redskins independent alumni project.",
    ) + f"""<body>
{header()}
<main id="main" class="wrap prose">
  <span class="label">Saranac Lake Redskins</span>
  <h1>Terms and disclaimer</h1>
  <p>saranaclakeredskins.com is an independent alumni project for Saranac Lake High School classes of 1890 to 2000. It is not affiliated with Saranac Lake Central School District or any official school body, and it is not an official record of the school.</p>

  <h2>The site is provided as-is</h2>
  <p>The site is offered as-is, without warranties of any kind, including that it will always be available, complete, or free of errors. Information posted here may be incomplete or out of date.</p>

  <h2>No liability</h2>
  <p>To the fullest extent permitted by law, the operators of this site, a plinymiller design, and a B-Tuff Company are not liable for any loss, damage, or claim arising from your use of the site, from reliance on information posted here, from downtime, or from content submitted by users.</p>

  <h2>Your content</h2>
  <p>You are responsible for the messages, photos, and other material you submit. Do not post anything you do not have the right to share, and do not post content that is unlawful or that harms others. We may edit, hide, or remove content or accounts when we believe it is necessary to run the site fairly.</p>

  <h2>Questions</h2>
  <p>Questions about these terms can be sent to <a href="{MAIL}">{CONTACT}</a>.</p>
</main>
{footer()}
</body>
</html>
"""


def not_found_page() -> str:
    return head("Page not found | Saranac Lake Redskins") + f"""<body>
{header()}
<main id="main" class="lost">
  <img class="lost-mark" src="assets/mark-red.svg" width="120" height="134" alt="">
  <span class="label">Saranac Lake Redskins</span>
  <h1>This page is not here</h1>
  <p>The address may be mistyped, or the page may have moved. You can go back home or find your class by year.</p>
  <div class="actions">
    <a class="btn" href="index.html">Home</a>
    <a class="btn ghost" href="classes.html">Find your class</a>
  </div>
</main>
{footer()}
</body>
</html>
"""


def support_page() -> str:
    return head(
        "Support | Saranac Lake Redskins",
        "Help keep this alumni site online. Contributions cover web hosting, the domain, and upkeep.",
    ) + f"""<body>
{header()}
<main id="main" class="wrap prose support-page">
  <img class="page-mark" src="assets/mark-maroon.svg" width="96" height="107" alt="">
  <span class="label">Support</span>
  <h1>Support this site</h1>
  <p>{SUPPORT_BLURB}</p>
  <p><a class="btn gold" href="{KOFI}" target="_blank" rel="noopener">Support this site</a></p>
</main>
{footer()}
</body>
</html>
"""


SECTION_COPY = {
    "sports": ("Sports", "Redskins sports",
               "Teams, seasons, coaches and the games people still talk about.",
               "Stories and photos coming soon. Send yours, with your class year, to"),
    "arts": ("Arts", "Arts and music",
             "Band, chorus, drama, art and the stage crews behind them.",
             "Stories and photos coming soon. Send yours, with your class year, to"),
    "news": ("News", "Alumni news",
             "Reunions, milestones and updates from Saranac Lake alumni.",
             "News and announcements coming soon. Send yours, with your class year, to"),
    "memoriam": ("In Memoriam", "In memoriam",
                 "Remembering classmates, teachers and coaches.",
                 "Remembrances will be shared here with care."),
}


def teasers() -> str:
    cards = []
    for key, href, label in SECTIONS:
        _, _, blurb, _ = SECTION_COPY[key]
        cls = " memoriam" if key == "memoriam" else ""
        cards.append(f'<a class="teaser{cls}" href="{href}"><span class="label">{label}</span>'
                     f'<strong>{SECTION_COPY[key][1]}</strong><span class="teaser-text">{blurb}</span>'
                     f'<span class="teaser-go" aria-hidden="true">&rarr;</span></a>')
    return f"""<section class="panel" aria-labelledby="sections-heading">
    <h2 id="sections-heading" class="sr-only">Explore</h2>
    <div class="teasers">{''.join(cards)}</div>
  </section>"""


def pagehead(label: str, title: str, blurb: str) -> str:
    return f"""<header class="pagehead">
    <p class="kicker">{label}</p>
    <h1>{title}</h1>
    <p class="lede">{blurb}</p>
  </header>"""


def contribute(soon: str, what: str) -> str:
    return f"""<aside class="contribute" aria-label="How to contribute">
    <p class="kicker">Coming soon</p>
    <p class="contribute-lede">{soon} <a href="{MAIL}">{CONTACT}</a>.</p>
    <ol class="steps-plain">
      <li>Email {what}, with your name and class year.</li>
      <li>Add a photo if you have one. Tell us who is in it and roughly when.</li>
      <li>We check the details with you before anything is posted.</li>
    </ol>
  </aside>"""


def section_page(key: str) -> str:
    label, title, blurb, soon = SECTION_COPY[key]
    if key == "memoriam":
        body = f"""<main id="main" class="wrap memoriam-page">
  {pagehead(label, title, blurb)}
  <div class="memoriam-box">
    <p>{soon}</p>
    <p>To remember a classmate, teacher or coach, email their name, class year, and a few words to <a href="{MAIL}">{CONTACT}</a>. A photo is welcome. We will check details with you before anything is posted.</p>
  </div>
</main>"""
    elif key == "sports":
        fb, _ = _site_stats()
        body = f"""<main id="main" class="wrap section-page">
  {pagehead(label, title, blurb)}
  <a class="sport-feature" href="football/index.html">
    <img src="football/img/1928_SLHS_Football.jpg" width="1000" height="583" alt="The 1928 Saranac Lake High School football team" loading="lazy">
    <span class="sf-copy">
      <span class="kicker">Football &middot; since 1923</span>
      <span class="sf-title">Redskins football</span>
      <span class="sf-text">The Film Room: every game we can find, with scores, newspaper write-ups, rosters, team photos and game film.</span>
      <span class="sf-figs">{fb["games"]} games &middot; {fb["seasons"]} seasons &middot; {fb["films"]} films</span>
      <span class="sf-go">Enter the Film Room <span aria-hidden="true">&rarr;</span></span>
    </span>
  </a>
  <section class="more-sports" aria-labelledby="ms-h">
    <h2 id="ms-h">More sports coming soon</h2>
    <ul class="sport-list"><li>Basketball</li><li>Hockey</li><li>Skiing</li><li>Track</li><li>And more</li></ul>
    <p>Basketball, hockey, skiing, track and more are on the way. {soon} <a href="{MAIL}">{CONTACT}</a>.</p>
  </section>
</main>"""
    else:
        what = {"news": "your news (a reunion date, a milestone, a class group link)",
                "arts": "your story or memory from band, chorus, drama, art or stage crew"}[key]
        body = f"""<main id="main" class="wrap section-page">
  {pagehead(label, title, blurb)}
  {contribute(soon, what)}
</main>"""
    return head(f"{label} | Saranac Lake Redskins",
                f"{blurb} Saranac Lake High School alumni, classes of 1890 to 2000.") + f"""<body>
{header(key)}
{body}
{footer()}
</body>
</html>
"""


def shop_page() -> str:
    return head("Shop | Saranac Lake Redskins",
                "Saranac Lake Redskins alumni gear and archival prints are coming soon.") + f"""<body>
{header("shop")}
<main id="main" class="wrap section-page">
  {pagehead("Shop", "The alumni shop", "Redskins alumni gear and archival prints of old team photos are on the way.")}
  <aside class="contribute" aria-label="Shop status">
    <p class="kicker">Coming soon</p>
    <p class="contribute-lede">The shop is not open yet. Want to know when it opens, or have an idea for something you would wear? Email <a href="{MAIL}">{CONTACT}</a>.</p>
    <p>In the meantime, you can help cover hosting and upkeep on the <a href="support.html">support page</a>.</p>
  </aside>
</main>
{footer()}
</body>
</html>
"""


def contact_page() -> str:
    return head("Contact Us | Saranac Lake Redskins",
                "Contact the Saranac Lake Redskins alumni site: news, corrections, photos, remembrances and account removal.") + f"""<body>
{header("contact")}
<main id="main" class="wrap section-page">
  {pagehead("Contact Us", "Get in touch", "This is a volunteer project. The best way to reach us is email.")}
  <p class="contact-email"><a href="{MAIL}">{CONTACT}</a></p>
  <section class="contact-topics" aria-labelledby="ct-h">
    <h2 id="ct-h" class="kicker">Good reasons to write</h2>
    <dl>
      <div><dt>Class news</dt><dd>Reunion dates, milestones and class group links for the <a href="news.html">news page</a>.</dd></div>
      <div><dt>Corrections</dt><dd>A misspelled name, a wrong score, a missing classmate. Tell us the page and what to fix.</dd></div>
      <div><dt>Photos and film</dt><dd>Yearbooks, team photos, programs and game tapes help fill in the history.</dd></div>
      <div><dt>In memoriam</dt><dd>A classmate, teacher or coach to remember. See <a href="in-memoriam.html">In Memoriam</a>.</dd></div>
      <div><dt>Your details</dt><dd>To have your account and details removed, email us from the address on your account.</dd></div>
    </dl>
  </section>
</main>
{footer()}
</body>
</html>
"""


def main() -> None:
    for key, href, _ in SECTIONS:
        write(href, section_page(key))
    write("index.html", index_page())
    write("classes.html", classes_page())
    write("welcome.html", welcome_page())
    write("privacy.html", privacy_page())
    write("terms.html", terms_page())
    write("support.html", support_page())
    write("shop.html", shop_page())
    write("contact.html", contact_page())
    write("404.html", not_found_page())
    from football import build as build_football
    build_football(globals())
    from alumni import build as build_alumni
    build_alumni(globals())
    for y in range(FIRST, LAST + 1):
        write(year_file(y), class_page(y))
    print("done")


if __name__ == "__main__":
    main()
