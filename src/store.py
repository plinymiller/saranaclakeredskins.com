"""Fundraiser store for saranaclakeredskins.com (static pages in /store/).

Called from generate.py main(): build(globals()).
Payments are intentionally NOT wired up yet: the checkout page ends in a disabled
"Checkout opens soon" state. No card fields, no processor scripts, no keys.
Prices are launch placeholders until vendor quotes are confirmed.
"""
import json
import re
from html import escape as _esc
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "store"
V = "2"  # asset cache-buster


def E(s) -> str:
    return _esc(str(s)) if s is not None else ""


def up(chrome: str) -> str:
    return re.sub(r'(href|src)="(?!https?:|mailto:|#|/|\.\./|data:)([^"]*)"', r'\1="../\2"', chrome)


def money(n) -> str:
    return "TBD"


# ---------------------------------------------------------------- beneficiaries
BENEFICIARIES = [
    {"id": "5qc", "name": "Saranac Lake 5th Quarter Club", "short": "5th Quarter Club",
     "line": "Redskins football's booster club since 1985: equipment, the press box, team meals and more.",
     "icon": "fb"},
    {"id": "sj", "name": "Santa's Jukebox (Holiday Helpers)", "short": "Santa's Jukebox",
     "line": "Saranac Lake's Christmas toy drive since 1948. Gifts reach local kids through Holiday Helpers.",
     "icon": "gift"},
]
BEN = {b["id"]: b for b in BENEFICIARIES}

# ---------------------------------------------------------------- colors
C = {
    "red": ("Red", "#A6192E"),
    "burgundy": ("Burgundy", "#5A1414"),
    "gold": ("Gold", "#FFB612"),
    "white": ("White", "#F6F5F1"),
    "heather": ("Heather Gray", "#B7B6B2"),
    "black": ("Black", "#1F1D1D"),
    "charcoal": ("Charcoal", "#3B3A3A"),
}
# one-color chief mark that reads on each garment color
MARK_ON = {"red": "white", "burgundy": "white", "gold": "burgundy", "white": "burgundy", "heather": "burgundy",
           "black": "white", "charcoal": "white"}

ADULT = [("S", 0), ("M", 0), ("L", 0), ("XL", 0), ("2XL", 0), ("3XL", 0)]
YOUTH = [("Youth S", 0), ("Youth M", 0), ("Youth L", 0)]

PRODUCTS = [
    {"slug": "classic-tee", "name": "Classic Tee", "cat": "tees", "shape": "tee",
     "colors": ["red", "white", "burgundy", "heather"], "sizes": YOUTH + ADULT, "logos": ["badge", "mark"],
     "blurb": "Soft ringspun cotton tee with the Redskins badge or the chief mark across the chest.",
     "details": [("Fabric", "100% ringspun cotton, 4.3 oz. Heather Gray is 90/10 cotton/poly."),
                 ("Fit", "Unisex classic fit. Order your usual size; size up for a roomier fit."),
                 ("Decoration", "Screen printed or direct-to-garment printed, 10 in. wide on adult sizes.")]},
    {"slug": "crewneck-sweatshirt", "name": "Crewneck Sweatshirt", "cat": "sweatshirts", "shape": "crew",
     "colors": ["red", "burgundy", "heather", "white"], "sizes": ADULT, "logos": ["badge", "mark"],
     "blurb": "Heavyweight fleece crew for Adirondack Friday nights in October.",
     "details": [("Fabric", "8 oz. cotton/poly fleece, ribbed cuffs and waistband."),
                 ("Fit", "Unisex relaxed fit."),
                 ("Decoration", "Printed chest graphic, 11 in. wide.")]},
    {"slug": "hoodie", "name": "Pullover Hoodie", "cat": "sweatshirts", "shape": "hoodie",
     "colors": ["red", "burgundy", "heather", "black"], "sizes": YOUTH + ADULT, "logos": ["badge", "mark"],
     "blurb": "The sideline hoodie: lined hood, kangaroo pocket, big chest logo.",
     "details": [("Fabric", "8 oz. cotton/poly fleece, lined hood with drawcord."),
                 ("Fit", "Unisex classic fit with ribbed cuffs."),
                 ("Decoration", "Printed chest graphic, 11 in. wide.")]},
    {"slug": "quarter-zip", "name": "Quarter-Zip Pullover", "cat": "quarter-zips", "shape": "qzip",
     "colors": ["red", "burgundy", "charcoal", "black"], "sizes": ADULT, "logos": ["mark", "badge"],
     "blurb": "Clean, embroidered left-chest mark on a mid-weight quarter-zip. Office to bleachers.",
     "details": [("Fabric", "Mid-weight brushed-back performance knit, stand-up collar."),
                 ("Fit", "Men's/unisex athletic fit."),
                 ("Decoration", "Embroidered left chest, about 3.5 in.")]},
    {"slug": "polo", "name": "Performance Polo", "cat": "polos", "shape": "polo",
     "colors": ["red", "white", "burgundy", "black"], "sizes": ADULT, "logos": ["mark", "badge"],
     "blurb": "Moisture-wicking polo with an embroidered left-chest logo. Reunion and golf-outing ready.",
     "details": [("Fabric", "100% polyester pique, moisture-wicking, snag-resistant."),
                 ("Fit", "Unisex classic fit, three-button placket."),
                 ("Decoration", "Embroidered left chest, about 3.5 in.")]},
    {"slug": "bucket-hat", "name": "Bucket Hat", "cat": "hats", "shape": "bucket",
     "colors": ["red", "white", "burgundy"], "sizes": [("S/M", 0), ("L/XL", 0)], "logos": ["mark", "badge"],
     "blurb": "Cotton twill bucket hat with an embroidered front logo. Lake days and tailgates.",
     "details": [("Fabric", "100% cotton twill, stitched brim, metal eyelets."),
                 ("Fit", "S/M fits 21.5-22.5 in.; L/XL fits 22.5-23.5 in."),
                 ("Decoration", "Embroidered front, about 2.5 in.")]},
    {"slug": "trucker-hat", "name": "Trucker Hat", "cat": "hats", "shape": "trucker",
     "colors": ["red/white", "white/red", "burgundy/white", "red/red"],
     "sizes": [("One size", 0)], "logos": ["badge", "mark"],
     "blurb": "Structured mid-profile trucker with mesh back, snapback and an embroidered front.",
     "details": [("Fabric", "Cotton/poly front, nylon mesh back, plastic snapback."),
                 ("Fit", "One size fits most, adjustable."),
                 ("Decoration", "Embroidered front, about 3.5 in.")]},
    {"slug": "leather-patch-hat", "name": "Leather Patch Hat", "cat": "hats", "shape": "patch",
     "colors": ["red/white", "burgundy/burgundy", "charcoal/white", "heather/red"],
     "sizes": [("One size", 0)], "logos": ["patch"],
     "blurb": "Laser-engraved leather patch of the chief mark, stitched onto a structured trucker.",
     "details": [("Fabric", "Cotton/poly front, mesh back, snapback."),
                 ("Fit", "One size fits most, adjustable."),
                 ("Decoration", "Genuine leather patch, laser engraved, sewn on all four sides.")]},
]
PBY = {p["slug"]: p for p in PRODUCTS}
CATS = [("all", "All"), ("tees", "Tees"), ("sweatshirts", "Sweatshirts"), ("quarter-zips", "Quarter-zips"),
        ("polos", "Polos"), ("hats", "Hats"), ("posters", "Posters")]

# ---------------------------------------------------------------- posters
# Only photos we may reproduce: pre-1931 yearbook scans (public domain) plus our own brand marks.
# Prices are TBD until vendor quotes are in (owner's request, Nov 23 2026).
POSTER_SIZES = [("8x10", "8 × 10 in.", None, 1000), ("11x14", "11 × 14 in.", None, 1400),
                ("16x20", "16 × 20 in.", None, 2000), ("18x24", "18 × 24 in.", None, 2400),
                ("24x36", "24 × 36 in.", None, 3600)]
TBD = "Price TBD"
POSTERS = [
    {"slug": "poster-1925-team", "title": "The 1925 Redskins", "year": "1925", "img": "../football/img/1925_SLHS_Football.jpg",
     "w": 1158, "h": 620, "kind": "photo",
     "cap": "Saranac Lake High School football team, 1925. From the 1926 Canaras yearbook.",
     "credit": "Public domain (published before 1931). Scan via the Historic Saranac Lake Wiki."},
    {"slug": "poster-1927-squad", "title": "The 1927 Squad", "year": "1927", "img": "../football/img/1928_SLHS_Football.jpg",
     "w": 1000, "h": 583, "kind": "photo",
     "cap": "The 1927 squad. From the 1928 Canaras yearbook.",
     "credit": "Public domain (published before 1931). Scan via the Historic Saranac Lake Wiki."},
    {"slug": "poster-1927-lineup", "title": "The Football Squad, 1927", "year": "1927", "img": "../football/img/1928_Canaras_Football2.jpg",
     "w": 728, "h": 1000, "kind": "photo",
     "cap": "The 1928 Canaras page with the 1927 line-up and season record. Harold Hill, captain.",
     "credit": "Public domain (published before 1931). Scan via the Historic Saranac Lake Wiki."},
    {"slug": "poster-1929-squad", "title": "The 1929 Squad", "year": "1929", "img": "../football/img/1930_Canaras_Football.jpg",
     "w": 1000, "h": 1436, "kind": "photo",
     "cap": "The 1929 squad page. From the 1930 Canaras yearbook.",
     "credit": "Public domain (published before 1931). Scan via the Historic Saranac Lake Wiki."},
    {"slug": "poster-badge", "title": "The Redskins Badge", "year": "Logo", "img": "../assets/store/badge.webp",
     "w": 9999, "h": 9999, "kind": "badge",
     "cap": "The round gold badge, printed large on cream stock.", "credit": "Vector artwork: prints sharp at every size."},
    {"slug": "poster-chief-mark", "title": "The Chief Mark", "year": "Logo", "img": "../assets/store/mark-burgundy.webp",
     "w": 9999, "h": 9999, "kind": "mark",
     "cap": "The burgundy chief mark on cream stock.", "credit": "Vector artwork: prints sharp at every size."},
]
EXCLUDED = [
    "1932 and 1937 team photos (1933 and 1938 Canaras)",
    "1944 team photo and 1948 'Football Opening' clipping (Adirondack Daily Enterprise)",
    "1958 varsity, Homecoming, band and cheerleading photos (1958 Canaras)",
    "Coach Ken Wilson portrait; 1987 Hall of Fame inductees and reunion photos",
    "Individual 1932 Canaras player portraits and later player photos",
]


def poster_sizes(p):
    long_px = max(p["w"], p["h"])
    out = []
    for key, label, price, need in POSTER_SIZES:
        out.append((key, label, price, long_px >= need))
    return out


# ---------------------------------------------------------------- mockups
def _logo_src(logo, color_key):
    if logo == "badge":
        return "../assets/store/badge.webp"
    if logo == "patch":
        return "../assets/store/mark-leather.webp"
    return f"../assets/store/mark-{MARK_ON.get(color_key, 'gold')}.webp"


def colors_of(p, ckey):
    """garment color keys -> (c1 hex, c2 hex, primary key)"""
    parts = ckey.split("/")
    c1 = C[parts[0]][1]
    c2 = C[parts[1]][1] if len(parts) > 1 else c1
    return c1, c2, parts[0]


def color_name(ckey):
    parts = ckey.split("/")
    if len(parts) == 1:
        return C[parts[0]][0]
    if parts[0] == parts[1]:
        return C[parts[0]][0]
    return f"{C[parts[0]][0]} / {C[parts[1]][0]} mesh"


SHAPES = {
    "tee": {
        "body": "M128 46 L170 30 Q200 56 230 30 L272 46 L354 94 L326 160 L290 142 L292 404 Q200 416 108 404 L110 142 L74 160 L46 94 Z",
        "extra": '<path d="M170 30 Q200 56 230 30 Q200 70 170 30Z" class="dk2"/>'
                 '<path d="M168 31 Q200 64 232 31" class="rib" stroke-width="7"/>'
                 '<path d="M76 152 L50 98" class="seam"/><path d="M324 152 L350 98" class="seam"/>',
        "logo": {"badge": (140, 92, 120), "mark": (138, 86, 124)},
    },
    "crew": {
        "body": "M140 58 Q200 92 260 58 L322 80 Q352 92 360 130 L384 322 Q386 340 368 344 L340 348 Q324 348 322 330 L300 180 L302 404 Q200 416 98 404 L100 180 L78 330 Q76 348 60 348 L32 344 Q14 340 16 322 L40 130 Q48 92 78 80 Z",
        "extra": '<path d="M150 60 Q200 84 250 60 Q200 70 150 60Z" class="dk2"/>'
                 '<path d="M142 60 Q200 96 258 60" class="rib" stroke-width="10"/>'
                 '<path d="M99 390 Q200 402 301 390 L302 405 Q200 417 98 405Z" class="dk"/>'
                 '<path d="M322 330 L368 324 L369 344 L340 348 Q324 348 322 330Z" class="dk"/>'
                 '<path d="M78 330 L32 324 L31 344 L60 348 Q76 348 78 330Z" class="dk"/>',
        "logo": {"badge": (140, 118, 120), "mark": (138, 112, 124)},
    },
    "hoodie": {
        "back": '<path d="M136 66 Q128 18 200 12 Q272 18 264 66 Q200 44 136 66Z" class="g dk"/>',
        "body": "M140 58 Q200 92 260 58 L322 80 Q352 92 360 130 L384 322 Q386 340 368 344 L340 348 Q324 348 322 330 L300 180 L302 404 Q200 416 98 404 L100 180 L78 330 Q76 348 60 348 L32 344 Q14 340 16 322 L40 130 Q48 92 78 80 Z",
        "extra": '<path d="M136 62 Q200 132 264 62 Q250 54 236 56 Q200 100 164 56 Q150 54 136 62Z" class="g"/>'
                 '<path d="M164 56 Q200 100 236 56 Q200 70 164 56Z" class="dk2"/>'
                 '<path d="M186 86 L182 160" class="cord"/><path d="M214 86 L218 160" class="cord"/>'
                 '<path d="M132 300 L268 300 L284 384 L116 384 Z" class="pocket"/>'
                 '<path d="M99 390 Q200 402 301 390 L302 405 Q200 417 98 405Z" class="dk"/>'
                 '<path d="M322 330 L368 324 L369 344 L340 348 Q324 348 322 330Z" class="dk"/>'
                 '<path d="M78 330 L32 324 L31 344 L60 348 Q76 348 78 330Z" class="dk"/>',
        "logo": {"badge": (146, 150, 108), "mark": (144, 146, 112)},
    },
    "qzip": {
        "body": "M140 58 Q200 92 260 58 L322 80 Q352 92 360 130 L384 322 Q386 340 368 344 L340 348 Q324 348 322 330 L300 180 L302 404 Q200 416 98 404 L100 180 L78 330 Q76 348 60 348 L32 344 Q14 340 16 322 L40 130 Q48 92 78 80 Z",
        "extra": '<path d="M146 34 L254 34 L262 62 Q200 92 138 62 Z" class="g"/>'
                 '<path d="M146 34 L254 34 L256 42 Q200 52 144 42Z" class="dk2"/>'
                 '<path d="M138 62 Q200 92 262 62" class="rib" stroke-width="4"/>'
                 '<path d="M200 46 L200 176" class="zip"/><rect x="195" y="90" width="10" height="20" rx="3" class="pull"/>'
                 '<path d="M99 390 Q200 402 301 390 L302 405 Q200 417 98 405Z" class="dk"/>'
                 '<path d="M322 330 L368 324 L369 344 L340 348 Q324 348 322 330Z" class="dk"/>'
                 '<path d="M78 330 L32 324 L31 344 L60 348 Q76 348 78 330Z" class="dk"/>',
        "logo": {"badge": (226, 118, 58), "mark": (226, 112, 58)},
    },
    "polo": {
        "body": "M128 46 L170 30 Q200 56 230 30 L272 46 L350 90 L324 150 L290 136 L292 404 Q200 416 108 404 L110 136 L76 150 L50 90 Z",
        "extra": '<rect x="190" y="58" width="20" height="78" rx="2" class="dk"/>'
                 '<circle cx="200" cy="76" r="3.2" class="btn-c"/><circle cx="200" cy="98" r="3.2" class="btn-c"/><circle cx="200" cy="120" r="3.2" class="btn-c"/>'
                 '<path d="M170 30 L200 62 L176 96 L146 46 Z" class="g"/><path d="M230 30 L200 62 L224 96 L254 46 Z" class="g"/>'
                 '<path d="M170 30 L200 62 L176 96 L146 46 Z" class="collar"/><path d="M230 30 L200 62 L224 96 L254 46 Z" class="collar"/>'
                 '<path d="M78 142 L54 96" class="seam"/><path d="M322 142 L346 96" class="seam"/>',
        "logo": {"badge": (228, 112, 56), "mark": (228, 106, 56)},
    },
    "bucket": {
        "body": "M118 282 L136 150 Q200 128 264 150 L282 282 Q200 300 118 282 Z",
        "extra": '<path d="M136 150 Q200 128 264 150 Q200 170 136 150Z" class="lt"/>'
                 '<path d="M58 302 Q66 266 118 274 Q200 298 282 274 Q334 266 342 302 Q322 344 200 348 Q78 344 58 302 Z" class="g"/>'
                 '<path d="M58 302 Q66 266 118 274 Q200 298 282 274 Q334 266 342 302 Q322 344 200 348 Q78 344 58 302 Z" class="shade-b"/>'
                 '<path d="M76 304 Q200 338 324 304" class="stitch"/><path d="M92 312 Q200 342 308 312" class="stitch"/>'
                 '<path d="M120 268 Q200 286 280 268" class="stitch"/>'
                 '<circle cx="150" cy="176" r="3.5" class="eye"/><circle cx="250" cy="176" r="3.5" class="eye"/>',
        "logo": {"badge": (160, 182, 80), "mark": (158, 178, 84)},
    },
    "trucker": {
        "back": '<path d="M88 266 Q84 128 200 116 Q316 128 312 266 Z" class="g2"/><path d="M88 266 Q84 128 200 116 Q316 128 312 266 Z" fill="url(#mesh)"/>',
        "body": "M126 262 Q124 140 200 122 Q276 140 274 262 Z",
        "extra": '<circle cx="200" cy="120" r="7" class="g"/>'
                 '<path d="M82 262 Q200 238 318 262 Q354 302 298 322 Q200 338 102 322 Q46 302 82 262 Z" class="g"/>'
                 '<path d="M82 262 Q200 238 318 262 Q354 302 298 322 Q200 338 102 322 Q46 302 82 262 Z" class="shade-b"/>'
                 '<path d="M96 270 Q200 250 304 270" class="stitch"/><path d="M110 312 Q200 326 290 312" class="stitch"/>',
        "logo": {"badge": (154, 150, 92), "mark": (152, 146, 96)},
    },
}
SHAPES["patch"] = dict(SHAPES["trucker"])
SHAPES["patch"]["logo"] = {"patch": (0, 0, 0)}

PATCH = ('<defs><linearGradient id="lea{u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C99766"/>'
         '<stop offset="1" stop-color="#9C6638"/></linearGradient></defs>'
         '<rect x="146" y="162" width="108" height="76" rx="16" fill="url(#lea{u})" stroke="#7A4A24" stroke-width="1.5"/>'
         '<rect x="152" y="168" width="96" height="64" rx="12" fill="none" stroke="#5E3618" stroke-width="1.6" stroke-dasharray="4 3" opacity=".8"/>'
         '<image href="../assets/store/mark-leather.webp" x="173" y="170" width="54" height="60" opacity=".88"/>')


def mockup(shape, ckey, logo, uid, cls="st-mock", label=None, lazy=False):
    s = SHAPES[shape]
    c1, c2, pkey = colors_of(None, ckey)
    lab = E(label) if label else ""
    if logo == "patch":
        logo_svg = PATCH.format(u=uid)
    else:
        x, y, w = s["logo"].get(logo) or list(s["logo"].values())[0]
        logo_svg = f'<image class="st-logo" href="{_logo_src(logo, pkey)}" x="{x}" y="{y}" width="{w}" height="{w}"/>'
    return (f'<svg class="{cls}" viewBox="0 0 400 440" role="img" aria-label="{lab}" '
            f'style="--c1:{c1};--c2:{c2}" data-shape="{shape}">'
            f'<defs><linearGradient id="sh{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".22"/>'
            f'<stop offset=".45" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".28"/></linearGradient></defs>'
            f'<ellipse cx="200" cy="422" rx="150" ry="10" class="floor"/>'
            f'{s.get("back", "")}'
            f'<path d="{s["body"]}" class="g"/><path d="{s["body"]}" fill="url(#sh{uid})"/>'
            f'{s["extra"]}{logo_svg}</svg>')


# ---------------------------------------------------------------- icons
ICON = {
    "bag": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 8h12l-1 12H7L6 8Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M9 8V6a3 3 0 0 1 6 0v2" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>',
    "lock": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="10" width="14" height="10" rx="2" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M8 10V7a4 4 0 0 1 8 0v3" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>',
    "heart": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>',
    "fb": '<svg viewBox="0 0 24 24" aria-hidden="true"><ellipse cx="12" cy="12" rx="9" ry="5.5" transform="rotate(-35 12 12)" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M9 15l6-6M10.5 10.5l1 1M12.5 8.8l1 1M8.8 12.5l1 1" stroke="currentColor" stroke-width="1.5"/></svg>',
    "gift": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="10" width="16" height="10" rx="1" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M3 7h18v3H3zM12 7v13M12 7c-1-3-5-4-5-1.5S12 7 12 7Zm0 0c1-3 5-4 5-1.5S12 7 12 7Z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>',
    "shirt": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 4 4 6.5 5.5 11 7 10.3V20h10v-9.7l1.5.7L20 6.5 16 4c-.6 1.4-2.2 2.3-4 2.3S8.6 5.4 8 4Z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>',
    "truck": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h11v10H3zM14 9h4l3 3v4h-7" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/><circle cx="7" cy="17.5" r="1.8" fill="currentColor"/><circle cx="17" cy="17.5" r="1.8" fill="currentColor"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 5 6v5c0 4.5 3 8 7 10 4-2 7-5.5 7-10V6l-7-3Z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/><path d="m9 12 2 2 4-4" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>',
    "close": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18" stroke="currentColor" stroke-width="2"/></svg>',
}


def build(g: dict) -> None:
    head, header, footer, MAIL, CONTACT = g["head"], g["header"], g["footer"], g["MAIL"], g["CONTACT"]
    OUT.mkdir(exist_ok=True)

    catalog = {}
    for p in PRODUCTS:
        catalog[p["slug"]] = {
            "name": p["name"], "shape": p["shape"], "type": "apparel",
            "colors": {k: {"name": color_name(k), "c1": colors_of(p, k)[0], "c2": colors_of(p, k)[1],
                           "mark": _logo_src("mark", k.split("/")[0])} for k in p["colors"]},
            "sizes": [sz for sz, _u in p["sizes"]],
            "svg": mockup(p["shape"], p["colors"][0], p["logos"][0], "UID", label=p["name"]),
        }
    for p in POSTERS:
        catalog[p["slug"]] = {"name": f"Poster: {p['title']}", "type": "poster", "img": p["img"], "kind": p["kind"],
                              "sizes": [k for k, _l, _pr, ok in poster_sizes(p) if ok],
                              "labels": {k: l for k, l, _p, _o in POSTER_SIZES}}
    data_js = ("window.SLR_STORE=" + json.dumps({"catalog": catalog, "ben": {b["id"]: b["short"] for b in BENEFICIARIES},
                                                  "mail": CONTACT}, separators=(",", ":")) + ";")
    (ROOT / "assets" / "store-data.js").write_text(data_js + "\n", encoding="utf-8")

    def page(title, desc, body, crumbs=None, cls=""):
        chrome = up(head(title, desc)).replace(
            "</head>", f'<link rel="stylesheet" href="../assets/store.css?v={V}">\n</head>')
        chrome = chrome.replace('content="#F7F1E6"', 'content="#A6192E"')
        crumb = ""
        if crumbs:
            crumb = ('<nav class="st-crumbs" aria-label="Breadcrumb"><ol>' +
                     "".join(f"<li>{c}</li>" for c in crumbs) + "</ol></nav>")
        return chrome + f"""<body class="st {cls}">
{up(header("store"))}
<aside class="st-bar" aria-label="Fundraiser notice"><span class="st-bar-in"><b>100% of proceeds</b> go to the 5th Quarter Club or Santa's Jukebox. You choose. <span class="st-bar-soon">Checkout opens soon.</span></span></aside>
{crumb}
{body}
{bag_drawer()}
{up(footer(logo_notice=True))}
<script src="../assets/store-data.js?v={V}" defer></script>
<script src="../assets/store.js?v={V}" defer></script>
</body>
</html>
"""

    def bag_button():
        return ('<button class="st-bagbtn" type="button" data-open-bag aria-haspopup="dialog" aria-controls="st-bag">'
                f'{ICON["bag"]}<span>Bag</span><span class="st-count" data-bag-count aria-label="0 items">0</span></button>')

    def bag_drawer():
        return f"""<div class="st-scrim" data-close-bag hidden></div>
<aside class="st-drawer" id="st-bag" role="dialog" aria-modal="true" aria-labelledby="st-bag-h" hidden tabindex="-1">
  <div class="st-drawer-hd">
    <h2 id="st-bag-h">Your bag</h2>
    <button class="st-icon-btn" type="button" data-close-bag aria-label="Close bag">{ICON["close"]}</button>
  </div>
  <div class="st-drawer-body" data-bag-lines><p class="st-empty">Your bag is empty.</p></div>
  <div class="st-drawer-ft">
    <div class="st-split" data-bag-split></div>
    <div class="st-row st-total"><span>Subtotal</span><b data-bag-subtotal>TBD</b></div>
    <p class="st-fine">Prices are to be determined. Shipping and pickup options at checkout.</p>
    <a class="st-btn st-btn-pri st-wide" href="checkout.html" data-bag-checkout>{ICON["lock"]}<span>Secure checkout</span></a>
    <button class="st-btn st-btn-ghost st-wide" type="button" data-close-bag>Keep shopping</button>
  </div>
</aside>
<div class="st-toast" role="status" aria-live="polite" data-toast></div>"""

    def ben_picker(name="ben"):
        opts = []
        for i, b in enumerate(BENEFICIARIES):
            chk = " checked" if i == 0 else ""
            opts.append(f'<label class="st-ben-opt"><input type="radio" name="{name}" value="{b["id"]}"{chk}>'
                        f'<span class="st-ben-card"><span class="st-ben-ic">{ICON[b["icon"]]}</span>'
                        f'<span><b>{E(b["short"])}</b><small>{E(b["line"])}</small></span></span></label>')
        return (f'<fieldset class="st-field st-ben"><legend>Your purchase supports <span class="st-req">100% of proceeds</span></legend>'
                f'<div class="st-ben-grid">{"".join(opts)}</div></fieldset>')

    def swatches(p, uid):
        out = []
        for i, k in enumerate(p["colors"]):
            c1, c2, _ = colors_of(p, k)
            chk = " checked" if i == 0 else ""
            bg = f"linear-gradient(135deg,{c1} 50%,{c2} 50%)" if c1 != c2 else c1
            out.append(f'<label class="st-sw" title="{E(color_name(k))}"><input type="radio" name="color" value="{k}"{chk}>'
                       f'<span style="background:{bg}"></span><span class="sr-only">{E(color_name(k))}</span></label>')
        return (f'<fieldset class="st-field"><legend>Color: <b data-color-name>{E(color_name(p["colors"][0]))}</b></legend>'
                f'<div class="st-sws">{"".join(out)}</div></fieldset>')

    def sizes_html(p):
        out = []
        for s, upc in p["sizes"]:
            chk = " checked" if len(p["sizes"]) == 1 else ""
            extra = ""
            out.append(f'<label class="st-size"><input type="radio" name="size" value="{E(s)}" data-up="{upc}"{chk} required>'
                       f'<span>{E(s)}{extra}</span></label>')
        guide = ""
        if p["cat"] in ("tees", "sweatshirts", "quarter-zips", "polos"):
            guide = ('<details class="st-guide"><summary>Size guide</summary><table><caption class="sr-only">Chest width, inches, laid flat</caption>'
                     '<thead><tr><th>Size</th><th>S</th><th>M</th><th>L</th><th>XL</th><th>2XL</th><th>3XL</th></tr></thead>'
                     '<tbody><tr><th>Chest (in.)</th><td>18</td><td>20</td><td>22</td><td>24</td><td>26</td><td>28</td></tr></tbody></table>'
                     '<p class="st-fine">Measured flat across the chest. Final charts come from the garment maker.</p></details>')
        return (f'<fieldset class="st-field"><legend>Size <span class="st-err" data-size-err hidden>Choose a size</span></legend>'
                f'<div class="st-sizes">{"".join(out)}</div>{guide}</fieldset>')

    def logo_picker(p):
        if p["logos"] == ["patch"]:
            return ""
        names = {"badge": "Round badge", "mark": "Chief mark"}
        out = []
        for i, l in enumerate(p["logos"]):
            chk = " checked" if i == 0 else ""
            out.append(f'<label class="st-chip"><input type="radio" name="logo" value="{l}"{chk}><span>{names[l]}</span></label>')
        return f'<fieldset class="st-field"><legend>Logo</legend><div class="st-chips">{"".join(out)}</div></fieldset>'

    def qty():
        return ('<div class="st-field st-qtyf"><span class="st-legend" id="qty-l">Quantity</span>'
                '<div class="st-qty" role="group" aria-labelledby="qty-l"><button type="button" data-q="-1" aria-label="Decrease quantity">&minus;</button>'
                '<input type="number" name="qty" value="1" min="1" max="20" inputmode="numeric" aria-labelledby="qty-l">'
                '<button type="button" data-q="1" aria-label="Increase quantity">+</button></div></div>')

    def card(p, i):
        k = p["colors"][0]
        sw = "".join(f'<span style="background:{colors_of(p, c)[0]}" title="{E(color_name(c))}"></span>' for c in p["colors"])
        return (f'<li class="st-card" data-cat="{p["cat"]}"><a href="{p["slug"]}.html">'
                f'<span class="st-card-img">{mockup(p["shape"], k, p["logos"][0], f"c{i}", label=p["name"] + ", " + color_name(k))}</span>'
                f'<span class="st-card-tx"><b>{E(p["name"])}</b><span class="st-price">{TBD}</span>'
                f'<span class="st-dots" aria-label="{len(p["colors"])} colors">{sw}</span></span></a></li>')

    def poster_frame(p, cls="st-poster"):
        if p["kind"] == "photo":
            inner = (f'<img src="{p["img"]}" alt="{E(p["cap"])}" width="{p["w"]}" height="{p["h"]}" loading="lazy" decoding="async">')
        else:
            inner = f'<img src="{p["img"]}" alt="{E(p["title"])}" width="300" height="300" loading="lazy" decoding="async">'
        orient = "port" if p["h"] > p["w"] else ("land" if p["w"] > p["h"] else "port")
        return f'<span class="{cls} {orient} k-{p["kind"]}"><span class="st-mat">{inner}</span></span>'

    def poster_card(p):
        ok = [l for k, l, _pr, o in poster_sizes(p) if o]
        return (f'<li class="st-card st-pcard" data-cat="posters"><a href="{p["slug"]}.html">'
                f'<span class="st-card-img st-wall">{poster_frame(p)}</span>'
                f'<span class="st-card-tx"><b>{E(p["title"])}</b><span class="st-price">{TBD}</span>'
                f'<span class="st-meta">{E(p["year"])} &middot; {len(ok)} size{"s" if len(ok) != 1 else ""}</span></span></a></li>')

    # ------------------------------------------------ store home
    chips = "".join((f'<li><a class="st-filter" href="posters.html">{l}</a></li>' if k == "posters" else
                     f'<li><button type="button" class="st-filter" data-filter="{k}" aria-pressed="{"true" if k == "all" else "false"}">{l}</button></li>')
                    for k, l in CATS)
    grid = "".join(card(p, i) for i, p in enumerate(PRODUCTS))
    pgrid = "".join(poster_card(p) for p in POSTERS[:4])
    bens = "".join(f'<li class="st-bencard"><span class="st-ben-ic big">{ICON[b["icon"]]}</span><div><h3>{E(b["name"])}</h3>'
                   f'<p>{E(b["line"])}</p></div></li>' for b in BENEFICIARIES)
    hero_art = (f'<div class="st-hero-art" aria-hidden="true">'
                f'<div class="st-hero-a">{mockup("hoodie", "red", "badge", "h1", label="")}</div>'
                f'<div class="st-hero-b">{mockup("trucker", "white/red", "badge", "h2", label="")}</div>'
                f'<div class="st-hero-c">{mockup("patch", "charcoal/white", "patch", "h3", label="")}</div></div>')
    body = f"""<main id="main" class="st-main">
  <section class="st-hero">
    <div class="st-wrap st-hero-grid">
      <div class="st-hero-tx">
        <span class="st-kicker">The Redskins Store &middot; Fundraiser</span>
        <h1>Red &amp; White, <span>for a good cause.</span></h1>
        <p class="st-lede">Tees, sweatshirts, quarter-zips, polos, hats and vintage team posters. <b>100% of proceeds</b> go to the Saranac Lake 5th Quarter Club or Santa's Jukebox, and you pick which one with every item.</p>
        <div class="st-cta"><a class="st-btn st-btn-pri" href="#shop">Shop the collection</a><a class="st-btn st-btn-line" href="posters.html">Vintage posters</a></div>
        <ul class="st-proof"><li>{ICON["heart"]}100% of proceeds to local causes</li><li>{ICON["shirt"]}Made to order</li><li>{ICON["truck"]}Ship or pick up in Saranac Lake</li></ul>
      </div>
      {hero_art}
    </div>
  </section>

  <section class="st-wrap st-causes" aria-labelledby="causes-h">
    <div class="st-sec-hd"><span class="st-kicker dk">Where your money goes</span><h2 id="causes-h">You choose the cause</h2>
    <p>Every item in your bag has its own choice. Split your order between both if you like.</p></div>
    <ul class="st-bens">{bens}</ul>
  </section>

  <section class="st-wrap" id="shop" aria-labelledby="shop-h">
    <div class="st-sec-hd st-sec-row"><div><span class="st-kicker dk">The collection</span><h2 id="shop-h">Shop</h2></div>
    {bag_button()}</div>
    <nav class="st-filters" aria-label="Filter products"><ul>{chips}</ul></nav>
    <p class="sr-only" aria-live="polite" data-filter-status></p>
    <ul class="st-grid" data-grid>{grid}</ul>
    <p class="st-fine st-center">Prices are to be determined and will be posted before checkout opens.</p>
  </section>

  <section class="st-posterband" aria-labelledby="post-h">
    <div class="st-wrap">
      <div class="st-sec-hd st-sec-row"><div><span class="st-kicker">From the archive</span><h2 id="post-h">Vintage team posters</h2>
      <p>The oldest Redskins team photos we have, from the 1926 to 1930 Canaras yearbooks.</p></div>
      <a class="st-btn st-btn-pri" href="posters.html">See all posters</a></div>
      <ul class="st-grid st-grid-posters">{pgrid}</ul>
    </div>
  </section>

  <section class="st-wrap st-how" aria-labelledby="how-h">
    <div class="st-sec-hd"><span class="st-kicker dk">How it works</span><h2 id="how-h">Simple, local, and every dollar counts</h2></div>
    <ol class="st-steps">
      <li><b>Pick your gear</b><span>Choose color, size and logo.</span></li>
      <li><b>Choose a cause</b><span>5th Quarter Club or Santa's Jukebox, per item.</span></li>
      <li><b>We make it</b><span>Printed or embroidered to order by local and trusted decorators.</span></li>
      <li><b>Ship or pick up</b><span>Shipping, or free pickup in Saranac Lake.</span></li>
    </ol>
  </section>

  <section class="st-wrap st-faq" aria-labelledby="faq-h">
    <div class="st-sec-hd"><span class="st-kicker dk">Questions</span><h2 id="faq-h">Good to know</h2></div>
    <details><summary>What does "100% of proceeds" mean?</summary><p>Everything left after the cost of making and shipping each item goes to the cause you chose. Nobody keeps a cent. We will post totals raised for each cause.</p></details>
    <details><summary>When can I check out?</summary><p>Very soon. You can build your bag now and it will be waiting for you. Secure payment is being set up and will open shortly.</p></details>
    <details><summary>How long does an order take?</summary><p>Items are made to order. Plan on about two to three weeks for apparel and hats, and about a week for posters.</p></details>
    <details><summary>Can I return or exchange?</summary><p>Because every item is made to order and the proceeds go to charity, sales are final, but if something arrives damaged or wrong we will make it right. <a href="{MAIL}">Contact us</a>.</p></details>
    <details><summary>Is this official school merchandise?</summary><p>No. This is an independent alumni fundraiser. Questions: <a href="{MAIL}">{CONTACT}</a>.</p></details>
  </section>
</main>"""
    (OUT / "index.html").write_text(page("Store | Saranac Lake Redskins",
        "The Redskins Store: tees, sweatshirts, quarter-zips, polos, hats and vintage posters. 100% of proceeds to the 5th Quarter Club or Santa's Jukebox.",
        body, cls="st-home"), encoding="utf-8")

    # ------------------------------------------------ product pages
    def related(cur_slug, n=4):
        others = [p for p in PRODUCTS if p["slug"] != cur_slug]
        cur = PBY.get(cur_slug)
        if cur:
            others.sort(key=lambda p: (p["cat"] != cur["cat"], PRODUCTS.index(p)))
        return "".join(card(p, 100 + i) for i, p in enumerate(others[:n]))

    for i, p in enumerate(PRODUCTS):
        k = p["colors"][0]
        details = "".join(f'<details{" open" if j == 0 else ""}><summary>{E(t)}</summary><p>{E(d)}</p></details>' for j, (t, d) in enumerate(p["details"]))
        details += ('<details><summary>Shipping &amp; pickup</summary><p>Made to order in about two to three weeks. '
                    'Shipping in the U.S., or free pickup in Saranac Lake.</p></details>')
        body = f"""<main id="main" class="st-main st-wrap st-pdp">
  <div class="st-pdp-grid">
    <div class="st-gallery">
      <div class="st-stage" data-stage>{mockup(p["shape"], k, p["logos"][0], "pd", cls="st-mock st-mock-lg", label=f'{p["name"]} mockup, {color_name(k)}')}</div>
      <p class="st-fine st-center">Mockup for illustration. Final print and embroidery placement may vary slightly.</p>
    </div>
    <form class="st-buy" data-buy data-slug="{p["slug"]}" novalidate>
      <span class="st-kicker dk">{E(dict(CATS)[p["cat"]])}</span>
      <h1>{E(p["name"])}</h1>
      <p class="st-pp"><span data-price>{TBD}</span></p>
      <p class="st-blurb">{E(p["blurb"])}</p>
      {swatches(p, i)}
      {logo_picker(p)}
      {sizes_html(p)}
      {ben_picker()}
      {qty()}
      <div class="st-addbar"><button class="st-btn st-btn-pri st-wide st-add" type="submit">{ICON["bag"]}<span>Add to bag</span></button></div>
      <ul class="st-assure"><li>{ICON["heart"]}100% of proceeds to your chosen cause</li><li>{ICON["lock"]}Secure checkout</li><li>{ICON["truck"]}Ship or free local pickup</li></ul>
      <div class="st-acc">{details}</div>
    </form>
  </div>
  <section class="st-related" aria-labelledby="rel-h"><h2 id="rel-h">You might also like</h2><ul class="st-grid st-grid-4">{related(p["slug"])}</ul></section>
</main>"""
        (OUT / f'{p["slug"]}.html').write_text(page(f'{p["name"]} | Redskins Store',
            f'{p["name"]} with the Saranac Lake Redskins logo. 100% of proceeds to the 5th Quarter Club or Santa\'s Jukebox.',
            body, crumbs=['<a href="index.html">Store</a>', f'<a href="index.html#shop">{E(dict(CATS)[p["cat"]])}</a>',
                          f'<span aria-current="page">{E(p["name"])}</span>']), encoding="utf-8")

    # ------------------------------------------------ posters
    allp = "".join(poster_card(p) for p in POSTERS)
    excl = "".join(f"<li>{E(x)}</li>" for x in EXCLUDED)
    body = f"""<main id="main" class="st-main">
  <section class="st-posterband st-posterhead">
    <div class="st-wrap"><span class="st-kicker">From the archive</span><h1 class="st-h1">Vintage team posters</h1>
    <p class="st-lede">Every team photo we are free to reprint, plus the Redskins badge and chief mark. Printed on heavyweight matte paper with a white border, framed or unframed. 100% of proceeds to your chosen cause.</p></div>
  </section>
  <section class="st-wrap" aria-labelledby="all-h">
    <div class="st-sec-row st-sec-hd"><h2 id="all-h">All posters</h2>{bag_button()}</div>
    <ul class="st-grid st-grid-posters">{allp}</ul>
    <div class="st-note">
      <h2>Why some favorite photos aren't here yet</h2>
      <p>Yearbook photos published before 1931 are in the public domain, so we can print them. Later photos on the Historic Saranac Lake Wiki and in the Adirondack Daily Enterprise may still be under copyright. We are asking for permission before offering:</p>
      <ul>{excl}</ul>
      <p>Have an original print or a high-resolution scan you'd share? <a href="{MAIL}">Contact us</a>. Higher-resolution scans also unlock larger poster sizes.</p>
    </div>
  </section>
</main>"""
    (OUT / "posters.html").write_text(page("Vintage Posters | Redskins Store",
        "Vintage Saranac Lake Redskins football team posters from the 1926-1930 Canaras yearbooks. 100% of proceeds to local causes.",
        body, crumbs=['<a href="index.html">Store</a>', '<span aria-current="page">Posters</span>']), encoding="utf-8")

    for p in POSTERS:
        sz = poster_sizes(p)
        first_ok = next(k for k, l, pr, ok in sz if ok)
        opts = []
        for k, l, pr, ok in sz:
            chk = " checked" if k == first_ok else ""
            dis = "" if ok else " disabled"
            note = "" if ok else '<small>Needs a sharper scan</small>'
            opts.append(f'<label class="st-size st-psize"><input type="radio" name="size" value="{k}"{chk}{dis}>'
                        f'<span>{E(l)}{note}</span></label>')
        unavailable = [l for k, l, pr, ok in sz if not ok]
        why = (f'<p class="st-fine">Larger sizes are off for now: this scan is {p["w"]}&times;{p["h"]} pixels, which would print soft above '
               f'{E(next(l for k, l, pr, ok in reversed(sz) if ok))}.</p>') if unavailable else ""
        frame = ('<fieldset class="st-field"><legend>Finish</legend><div class="st-chips">'
                 '<label class="st-chip"><input type="radio" name="frame" value="0" checked><span>Print only</span></label>'
                 f'<label class="st-chip"><input type="radio" name="frame" value="1"><span>Black frame</span></label></div></fieldset>')
        body = f"""<main id="main" class="st-main st-wrap st-pdp">
  <div class="st-pdp-grid">
    <div class="st-gallery">
      <div class="st-stage st-wall" data-stage data-frame-target>{poster_frame(p, "st-poster st-poster-lg")}</div>
      <p class="st-fine st-center">{E(p["credit"])}</p>
    </div>
    <form class="st-buy" data-buy data-slug="{p["slug"]}" data-kind="poster" novalidate>
      <span class="st-kicker dk">Poster &middot; {E(p["year"])}</span>
      <h1>{E(p["title"])}</h1>
      <p class="st-pp"><span data-price>{TBD}</span></p>
      <p class="st-blurb">{E(p["cap"])}</p>
      <fieldset class="st-field"><legend>Size</legend><div class="st-sizes st-sizes-wide">{"".join(opts)}</div>{why}</fieldset>
      {frame}
      {ben_picker()}
      {qty()}
      <div class="st-addbar"><button class="st-btn st-btn-pri st-wide st-add" type="submit">{ICON["bag"]}<span>Add to bag</span></button></div>
      <ul class="st-assure"><li>{ICON["heart"]}100% of proceeds to your chosen cause</li><li>{ICON["lock"]}Secure checkout</li><li>{ICON["truck"]}Ships rolled in a tube, or framed</li></ul>
      <div class="st-acc"><details open><summary>Paper &amp; print</summary><p>Archival matte paper, about 230 gsm, with a white border so the photo keeps its original shape.</p></details>
      <details><summary>About this photo</summary><p>{E(p["cap"])} {E(p["credit"])}</p></details></div>
    </form>
  </div>
  <section class="st-related" aria-labelledby="rel-h"><h2 id="rel-h">More posters</h2><ul class="st-grid st-grid-4 st-grid-posters">{"".join(poster_card(q) for q in POSTERS if q is not p)}</ul></section>
</main>"""
        (OUT / f'{p["slug"]}.html').write_text(page(f'{p["title"]} poster | Redskins Store', E(p["cap"]), body,
            crumbs=['<a href="index.html">Store</a>', '<a href="posters.html">Posters</a>', f'<span aria-current="page">{E(p["title"])}</span>']),
            encoding="utf-8")

    # ------------------------------------------------ checkout
    ben_all = "".join(f'<label class="st-chip"><input type="radio" name="allben" value="{b["id"]}"><span>All to {E(b["short"])}</span></label>' for b in BENEFICIARIES)
    body = f"""<main id="main" class="st-main st-wrap st-co">
  <ol class="st-progress" aria-label="Checkout steps"><li class="done">Bag</li><li aria-current="step">Details</li><li>Payment</li></ol>
  <h1 class="st-h1 st-co-h">Secure checkout</h1>
  <div class="st-co-grid">
    <form class="st-co-form" data-checkout novalidate autocomplete="on">
      <section class="st-co-sec" aria-labelledby="c1"><h2 id="c1"><span>1</span>Contact</h2>
        <div class="st-in"><label for="em">Email</label><input id="em" type="email" autocomplete="email" inputmode="email" required></div>
        <div class="st-in"><label for="ph">Phone <small>(optional, for pickup texts)</small></label><input id="ph" type="tel" autocomplete="tel" inputmode="tel"></div>
      </section>
      <section class="st-co-sec" aria-labelledby="c2"><h2 id="c2"><span>2</span>Delivery</h2>
        <div class="st-ship" role="radiogroup" aria-labelledby="c2">
          <label class="st-opt"><input type="radio" name="ship" value="ship" checked><span><b>Ship to me</b><small>U.S. only</small></span><em data-ship-price>TBD</em></label>
          <label class="st-opt"><input type="radio" name="ship" value="pickup"><span><b>Pick up in Saranac Lake</b><small>We'll email when it's ready</small></span><em>Free</em></label>
        </div>
        <div class="st-addr" data-addr>
          <div class="st-in"><label for="nm">Full name</label><input id="nm" autocomplete="name" required></div>
          <div class="st-in"><label for="a1">Street address</label><input id="a1" autocomplete="address-line1" required></div>
          <div class="st-in"><label for="a2">Apt, suite <small>(optional)</small></label><input id="a2" autocomplete="address-line2"></div>
          <div class="st-in3"><div class="st-in"><label for="ct">City</label><input id="ct" autocomplete="address-level2" required></div>
          <div class="st-in"><label for="stt">State</label><input id="stt" autocomplete="address-level1" required></div>
          <div class="st-in"><label for="zp">ZIP</label><input id="zp" autocomplete="postal-code" inputmode="numeric" required></div></div>
        </div>
      </section>
      <section class="st-co-sec" aria-labelledby="c3"><h2 id="c3"><span>3</span>Your causes</h2>
        <p class="st-fine">Each item keeps the cause you picked. Want to send the whole order to one?</p>
        <div class="st-chips"><label class="st-chip"><input type="radio" name="allben" value="" checked><span>Keep my picks</span></label>{ben_all}</div>
      </section>
      <section class="st-co-sec st-pay" aria-labelledby="c4"><h2 id="c4"><span>4</span>Payment</h2>
        <div class="st-pay-box">{ICON["lock"]}<div><b>Secure payment opens soon</b>
        <p>Card, Apple Pay and Google Pay will be handled on an encrypted, PCI-compliant payment page. Your card number never touches this site and is never stored by us.</p></div></div>
      </section>
      <div class="st-place">
        <button class="st-btn st-btn-pri st-wide" type="submit" disabled aria-describedby="soon-note">{ICON["lock"]}<span>Checkout opens soon</span></button>
        <p id="soon-note" class="st-fine">We're putting the finishing touches on secure payment. Your bag is saved on this device. Nothing you type on this page is sent or stored.</p>
        <a class="st-btn st-btn-ghost st-wide" data-notify href="{MAIL}">Email me when checkout opens</a>
      </div>
    </form>
    <aside class="st-summary" aria-labelledby="sum-h">
      <details class="st-sum-toggle" open><summary><h2 id="sum-h">Order summary</h2><b data-sum-total-top></b></summary>
      <div data-sum-lines><p class="st-empty">Your bag is empty. <a href="index.html">Start shopping</a>.</p></div>
      <div class="st-sum-rows">
        <div class="st-row"><span>Subtotal</span><span data-sum-sub>TBD</span></div>
        <div class="st-row"><span>Shipping</span><span data-sum-ship>TBD</span></div>
        <div class="st-row"><span>Tax</span><span>Calculated at payment</span></div>
        <div class="st-row st-total"><span>Total</span><b data-sum-total>TBD</b></div>
      </div>
      <div class="st-split" data-sum-split></div>
      </details>
      <ul class="st-trust">
        <li>{ICON["lock"]}<span><b>Encrypted</b>HTTPS / TLS throughout</span></li>
        <li>{ICON["shield"]}<span><b>PCI-compliant</b>Card data handled by the payment processor</span></li>
        <li>{ICON["heart"]}<span><b>100% of proceeds</b>to the causes you chose</span></li>
      </ul>
    </aside>
  </div>
</main>"""
    (OUT / "checkout.html").write_text(page("Checkout | Redskins Store", "Secure checkout for the Redskins Store.", body,
        crumbs=['<a href="index.html">Store</a>', '<span aria-current="page">Checkout</span>'], cls="st-checkout"), encoding="utf-8")
    print(f"store: {len(PRODUCTS)} products, {len(POSTERS)} posters")
