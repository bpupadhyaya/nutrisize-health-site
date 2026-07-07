#!/usr/bin/env python3
"""Render /foods/<slug>/ — one static, search-indexable page per free-tier food
from assets/data/free/foods.json: full nutrition per 100 g with %DV, serving
sizes, allergens, glycemic and density tags, the physiological parameters it
touches (linked to the Connections Explorer), related foods, and citations.
This is the programmatic-SEO layer that feeds the funnel.

Usage: python3 scripts/render_food_pages.py
"""
import json
import os

from render_plans import ROOT, SITE, asset_v, esc, footer, head, iap_plug, nav

FOODS = os.path.join(ROOT, "assets", "data", "free", "foods.json")

# label, key, unit, FDA Daily Value (0 = value-only), is-macro
SPECS = [
    ("Calories", "calories", "kcal", 2000, 1), ("Protein", "protein", "g", 50, 1),
    ("Carbohydrates", "carbohydrates", "g", 275, 1), ("Fat", "fat", "g", 78, 1),
    ("Fiber", "fiber", "g", 28, 1), ("Total sugars", "sugar", "g", 0, 1),
    ("Sodium", "sodium", "mg", 2300, 1),
    ("Vitamin A", "vitaminA", "µg", 900, 0), ("Vitamin C", "vitaminC", "mg", 90, 0),
    ("Vitamin D", "vitaminD", "µg", 20, 0), ("Vitamin E", "vitaminE", "mg", 15, 0),
    ("Vitamin K", "vitaminK", "µg", 120, 0), ("Thiamin B1", "vitaminB1", "mg", 1.2, 0),
    ("Riboflavin B2", "vitaminB2", "mg", 1.3, 0), ("Niacin B3", "vitaminB3", "mg", 16, 0),
    ("Vitamin B6", "vitaminB6", "mg", 1.7, 0), ("Folate B9", "vitaminB9", "µg", 400, 0),
    ("Vitamin B12", "vitaminB12", "µg", 2.4, 0), ("Calcium", "calcium", "mg", 1300, 0),
    ("Iron", "iron", "mg", 18, 0), ("Magnesium", "magnesium", "mg", 420, 0),
    ("Phosphorus", "phosphorus", "mg", 1250, 0), ("Potassium", "potassium", "mg", 4700, 0),
    ("Zinc", "zinc", "mg", 11, 0), ("Selenium", "selenium", "µg", 55, 0),
]


def titlecase(s):
    return str(s or "").replace("-", " ").replace("_", " ").title()


def fmt(v):
    if v is None:
        return "&ndash;"
    if v >= 100:
        return f"{round(v):,}"
    if v >= 10:
        return str(round(v))
    if v >= 1:
        return str(round(v * 10) / 10)
    return str(round(v * 100) / 100)


def nv(food, key):
    n = food.get("nutrientsPer100g") or {}
    v = n.get(key)
    return v if isinstance(v, (int, float)) else None


def bar(label, v, unit, dv):
    if v is None:
        return ""
    val = f"<b>{fmt(v)}</b> {unit}"
    if not dv:
        return (f'<div class="nm-bar nm-noDV"><div class="nm-bar-top">'
                f'<span class="nm-bar-label">{label}</span>'
                f'<span class="nm-bar-val">{val} <span class="nm-bar-pct">no %DV*</span></span></div></div>')
    p = round(v / dv * 100)
    return (f'<div class="nm-bar"><div class="nm-bar-top"><span class="nm-bar-label">{label}</span>'
            f'<span class="nm-bar-val">{val} <span class="nm-bar-pct">{p}% DV</span></span></div>'
            f'<div class="nm-track"><span class="nm-fill" style="width:{min(p,100)}%"></span></div></div>')


def micro_row(label, v, unit, dv):
    if v is None:
        return ""
    if not dv:
        body = f'<span class="nm-micro-val"><b>{fmt(v)}</b> {unit}</span>'
    else:
        p = round(v / dv * 100)
        body = (f'<span class="nm-micro-val"><b>{fmt(v)}</b> {unit} <span class="nm-bar-pct">{p}%</span></span>'
                f'<div class="nm-track"><span class="nm-fill" style="width:{min(p,100)}%"></span></div>')
    return f'<div class="nm-micro"><span class="nm-micro-label">{label}</span>{body}</div>'


def food_page(food, related, prefix="../../"):
    name = food["name"]
    cat = titlecase(food.get("category"))
    kcal = nv(food, "calories")
    desc = food.get("description") or f"{name}: full nutrition per 100 g, serving sizes, and where it fits your day."
    title = f"{name} Nutrition Facts (per 100g) — Calories, Macros & Vitamins | Nutrisize Health"
    metadesc = esc(desc)[:180]
    canonical = f"{SITE}/foods/{food['slug']}/"

    jsonld = f"""    <link rel="stylesheet" href="{prefix}assets/css/explorer.css?v={asset_v('assets/css/explorer.css')}">
    <script src="{prefix}assets/js/ref-modal.js?v={asset_v('assets/js/ref-modal.js')}" defer></script>
    <script type="application/ld+json">
    {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {{"@type":"ListItem","position":1,"name":"Home","item":"{SITE}/"}},
      {{"@type":"ListItem","position":2,"name":"Foods","item":"{SITE}/foods/"}},
      {{"@type":"ListItem","position":3,"name":"{esc(name)}","item":"{canonical}"}}]}}
    </script>
"""
    html = head(title, metadesc, canonical, prefix, jsonld) + nav(prefix)
    html += f"""
<header class="hero hero-sub">
    <div class="wrap">
        <p style="margin:0 0 8px"><a href="{prefix}foods/" style="color:var(--green-700); font-weight:600; font-size:14px">&larr; Food Explorer</a></p>
        <h1>{esc(name)}</h1>
        <p class="tagline">{esc(cat)}{f" &middot; {esc(titlecase(food.get('subcategory')))}" if food.get('subcategory') else ""} &middot; per 100&nbsp;g</p>
        {f'<p class="lede">{esc(food["description"])}</p>' if food.get("description") else ""}
    </div>
</header>

<section>
    <div class="wrap" style="max-width:820px">
"""
    # Tags
    tags = ""
    if food.get("densityScore") is not None:
        score = food["densityScore"]
        cls = "good" if score >= 7 else "mid" if score >= 4 else "low"
        tags += f'<span class="fx-chip {cls}">Nutrient density {fmt(score)}</span>'
    if food.get("giCategory") and str(food["giCategory"]).lower() not in ("none", "varies"):
        tags += f'<span class="fx-chip mid">GI {esc(titlecase(food["giCategory"]))}</span>'
    if food.get("isStaple"):
        tags += '<span class="fx-chip good">Staple food</span>'
    for a in (food.get("allergens") or []):
        tags += f'<span class="fx-chip low">Allergen: {esc(titlecase(a))}</span>'
    if tags:
        html += f'        <div class="fx-tags" style="margin-top:0">{tags}</div>\n'

    # Macro bars
    macro_bars = "".join(bar(l, nv(food, k), u, dv) for l, k, u, dv, m in SPECS if m)
    html += f'        <div class="pd-sec"><h4>Macronutrients</h4><div class="nm-bars">{macro_bars}</div></div>\n'

    # Micros
    micro_rows = "".join(micro_row(l, nv(food, k), u, dv) for l, k, u, dv, m in SPECS if not m)
    if micro_rows.strip():
        html += (f'        <div class="pd-sec"><h4>Vitamins &amp; minerals</h4>'
                 f'<div class="nm-micro-grid">{micro_rows}</div></div>\n')

    # Serving sizes
    servs = food.get("servingSizes") or []
    if servs:
        rows = "".join(f'<tr><td class="pname">{esc(s.get("label",""))}</td>'
                       f'<td class="change">{fmt(s.get("grams"))} g</td></tr>' for s in servs)
        html += (f'        <div class="pd-sec"><h4>Common serving sizes</h4>'
                 f'<div class="table-scroll"><table class="param-table"><thead><tr>'
                 f'<th>Serving</th><th>Weight</th></tr></thead><tbody>{rows}</tbody></table></div></div>\n')

    # Physiology links -> Connections
    pl = food.get("physiologyLinks") or []
    if pl:
        items = "".join(f'<p class="pd-row"><b>{esc(titlecase(l.get("param")))}</b> &mdash; {esc(l.get("effect",""))}</p>'
                        for l in pl[:6])
        html += (f'        <div class="pd-sec"><h4>What it supports in your body</h4>{items}'
                 f'<p class="tool-note" style="margin-top:6px"><a href="{prefix}connections/?lens=food&id={esc(food["id"])}">'
                 f'See {esc(name)} in the Connections Explorer &rarr;</a></p></div>\n')

    # Best timing around exercise
    if food.get("exerciseTimingBest"):
        t = food["exerciseTimingBest"]
        txt = "; ".join(esc(x) for x in t) if isinstance(t, list) else esc(t)
        html += f'        <div class="pd-sec"><h4>Best timing around exercise</h4><p class="pd-row">{txt}</p></div>\n'

    # Related foods
    if related:
        chips = "".join(f'<a class="cx-badge food" href="{prefix}foods/{r["slug"]}/">{esc(r["name"])}</a>' for r in related)
        html += (f'        <div class="pd-sec"><h4>More {esc(cat.lower())}</h4>'
                 f'<div class="cx-foodlist">{chips}</div></div>\n')

    # Citations
    cites = food.get("citations") or []
    if cites:
        html += ('        <p style="margin-top:18px"><button class="ref-open" type="button" data-ref-open>'
                 f'&#128218; Sources &amp; references &middot; {len(cites)}</button></p>\n')

    html += f"""        <div class="notice" style="margin-top:22px">
            <strong>Educational reference only.</strong> Values are per 100&nbsp;g from the app's
            reference database; %&nbsp;Daily Value uses the FDA 2,000-calorie reference. Not medical
            or dietary advice. See our <a href="{prefix}disclaimer/">full disclaimer</a>.
        </div>
{iap_plug(prefix, "food-page",
          f"Log {name.split('(')[0].strip()} and 4,994 more foods in the app.",
          "Nutrisize Health totals every nutrient from what you actually eat, against targets for "
          "your age and sex — with serving-size math and regional names, offline and private.")}
    </div>
</section>
"""
    # ref library
    if cites:
        rows = []
        for c in cites:
            g = (c.get("evidence_grade") or c.get("evidenceGrade") or "").lower()
            badge = f'<span class="cx-grade {esc(g) or "na"}">{esc(g.upper()) if g else "&ndash;"}</span>'
            txt = esc(c.get("title") or "")
            url = c.get("url")
            link = f'<a href="{esc(url)}" target="_blank" rel="noopener">{txt}</a>' if url else txt
            src = f' <span class="cx-src">&mdash; {esc(c["source"])}{", " + str(c["year"]) if c.get("year") else ""}</span>' if c.get("source") else ""
            rows.append(f'<div class="cx-ref">{badge}<span>{link}{src}</span></div>')
        html += ('<div id="ref-library"><p class="rm-legend">Sources for this food. Links open in a '
                 'new tab.</p><div class="cx-refs">' + "".join(rows) + "</div></div>\n")
    html += footer(prefix)
    return html


def main():
    foods = json.load(open(FOODS))["foods"]
    by_cat = {}
    for f in foods:
        by_cat.setdefault(f.get("category"), []).append(f)
    base = os.path.join(ROOT, "foods")
    slugs = []
    for f in foods:
        peers = [x for x in by_cat.get(f.get("category"), []) if x["id"] != f["id"]]
        peers.sort(key=lambda x: x.get("densityScore") or 0, reverse=True)
        d = os.path.join(base, f["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w") as fh:
            fh.write(food_page(f, peers[:8]))
        slugs.append(f["slug"])
    print("wrote %d per-food pages under /foods/" % len(foods))
    with open(os.path.join(base, ".slugs"), "w") as fh:
        fh.write("\n".join(slugs))


if __name__ == "__main__":
    main()
