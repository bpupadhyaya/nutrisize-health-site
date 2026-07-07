#!/usr/bin/env python3
"""Render /nutrients/ — the nutrient encyclopedia: a hub plus one mini-monograph
page per nutrient (functions, daily values by demographic, deficiency and
toxicity, bioavailability, cooking impact, best food sources cross-linked to the
Food Explorer, and citations). Built from the app's nutrients_data.json; the
"in our database" food sources are computed from the free-tier foods.json.

Nutrient content is educational (not one of the gated IAPs), so all 75 ship.

Usage: python3 scripts/render_nutrients.py [--app-repo <path>]
"""
import argparse
import json
import os
import re

from render_plans import (ROOT, SITE, asset_v, esc, footer, head, iap_plug, nav)

DEFAULT_APP_REPO = os.path.normpath(os.path.join(ROOT, "..", "..", "pvt", "nutrisize-health-claude"))
FOODS = os.path.join(ROOT, "assets", "data", "free", "foods.json")

def classify(nut):
    """Group key: nutrients store macro/micro in `category` and vitamins vs
    minerals in `subcategory`."""
    sub = str(nut.get("subcategory") or "").lower()
    if "vitamin" in sub:
        return "vitamins"
    if "mineral" in sub:
        return "minerals"
    return "macro"


GROUP_SINGULAR = {"vitamins": "Vitamin", "minerals": "Mineral", "macro": "Macronutrient"}

# nutrient id -> key in foods.json nutrientsPer100g (only those the food DB carries)
FOOD_KEY = {
    "protein": "protein", "dietary-fiber": "fiber", "fiber": "fiber",
    "total-carbohydrate": "carbohydrates", "carbohydrate": "carbohydrates",
    "total-fat": "fat", "fat": "fat", "total-sugars": "sugar", "sugar": "sugar",
    "vitamin-a": "vitaminA", "vitamin-c": "vitaminC", "vitamin-d": "vitaminD",
    "vitamin-e": "vitaminE", "vitamin-k": "vitaminK",
    "thiamin": "vitaminB1", "vitamin-b1": "vitaminB1", "riboflavin": "vitaminB2",
    "vitamin-b2": "vitaminB2", "niacin": "vitaminB3", "vitamin-b3": "vitaminB3",
    "vitamin-b6": "vitaminB6", "folate": "vitaminB9", "vitamin-b9": "vitaminB9",
    "vitamin-b12": "vitaminB12", "calcium": "calcium", "iron": "iron",
    "magnesium": "magnesium", "phosphorus": "phosphorus", "potassium": "potassium",
    "sodium": "sodium", "zinc": "zinc", "selenium": "selenium",
}
NUTR_UNIT = {"vitaminA": "µg", "vitaminC": "mg", "vitaminD": "µg", "vitaminE": "mg",
             "vitaminK": "µg", "vitaminB1": "mg", "vitaminB2": "mg", "vitaminB3": "mg",
             "vitaminB6": "mg", "vitaminB9": "µg", "vitaminB12": "µg", "calcium": "mg",
             "iron": "mg", "magnesium": "mg", "phosphorus": "mg", "potassium": "mg",
             "sodium": "mg", "zinc": "mg", "selenium": "µg", "protein": "g", "fiber": "g",
             "carbohydrates": "g", "fat": "g", "sugar": "g"}

DV_LABEL = {"adultMale": "Adult male", "adultFemale": "Adult female",
            "pregnancy": "Pregnancy", "lactation": "Lactation", "children": "Children",
            "infants": "Infants", "elderly": "Older adults", "upperLimit": "Upper limit"}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def humanize(k):
    return re.sub(r"([a-z])([A-Z])", r"\1 \2", str(k)).replace("_", " ").strip().capitalize()


def top_foods(foods, key, n=8):
    scored = [(f, f.get("nutrientsPer100g", {}).get(key)) for f in foods]
    scored = [(f, v) for f, v in scored if isinstance(v, (int, float)) and v > 0]
    scored.sort(key=lambda t: t[1], reverse=True)
    return scored[:n]


def ul(items, limit=None):
    items = list(items)[:limit] if limit else list(items)
    return "<ul class=\"nt-list\">" + "".join(f"<li>{esc(x)}</li>" for x in items) + "</ul>"


def sec(title, body):
    return f'<div class="pd-sec"><h4>{esc(title)}</h4>{body}</div>' if body else ""


def ref_library(nut):
    cites = nut.get("citations") or []
    if not cites:
        return ""
    rows = []
    for c in cites:
        g = (c.get("evidenceGrade") or "").lower()
        badge = f'<span class="cx-grade {esc(g) or "na"}">{esc(g.upper()) if g else "&ndash;"}</span>'
        txt = esc(c.get("title") or "")
        url = c.get("url")
        link = f'<a href="{esc(url)}" target="_blank" rel="noopener">{txt}</a>' if url else txt
        src = f' <span class="cx-src">&mdash; {esc(c["source"])}{(", " + str(c["year"])) if c.get("year") else ""}</span>' if c.get("source") else ""
        rows.append(f'<div class="cx-ref">{badge}<span>{link}{src}</span></div>')
    return ('<div id="ref-library"><p class="rm-legend">Evidence grades: A &mdash; '
            'meta-analyses / large trials; B &mdash; cohort studies &amp; guidelines; '
            'C &mdash; expert consensus. Links open in a new tab.</p>'
            '<div class="cx-refs">' + "".join(rows) + "</div></div>\n")


def nutrient_page(nut, foods, prefix="../../"):
    name = nut["name"]
    cat = GROUP_SINGULAR.get(classify(nut), "Nutrient")
    title = f"{name} — Functions, Daily Value & Food Sources | Nutrisize Health"
    desc = (esc(nut.get("simplyPut") or f"{name}: what it does, how much you need, deficiency and "
            "toxicity, and the best food sources.")[:180])
    canonical = f"{SITE}/nutrients/{slug(nut['id'])}/"

    jsonld = f"""    <link rel="stylesheet" href="{prefix}assets/css/explorer.css?v={asset_v('assets/css/explorer.css')}">
    <script src="{prefix}assets/js/ref-modal.js?v={asset_v('assets/js/ref-modal.js')}" defer></script>
    <script type="application/ld+json">
    {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {{"@type":"ListItem","position":1,"name":"Home","item":"{SITE}/"}},
      {{"@type":"ListItem","position":2,"name":"Nutrients","item":"{SITE}/nutrients/"}},
      {{"@type":"ListItem","position":3,"name":"{esc(name)}","item":"{canonical}"}}]}}
    </script>
"""
    html = head(title, desc, canonical, prefix, jsonld) + nav(prefix)
    html += f"""
<header class="hero hero-sub">
    <div class="wrap">
        <p style="margin:0 0 8px"><a href="{prefix}nutrients/" style="color:var(--green-700); font-weight:600; font-size:14px">&larr; All nutrients</a></p>
        <h1>{esc(name)}</h1>
        {f'<p class="pd-pron" style="text-align:center">{esc(nut["pronunciation"])}</p>' if nut.get("pronunciation") else ""}
        <p class="tagline">{esc(cat)}</p>
        {f'<p class="lede">{esc(nut["simplyPut"])}</p>' if nut.get("simplyPut") else ""}
    </div>
</header>

<section>
    <div class="wrap" style="max-width:820px">
"""
    if nut.get("analogy"):
        html += f'        <div class="pd-analogy" style="margin-top:0">{esc(nut["analogy"])}</div>\n'

    # Functions
    if nut.get("functions"):
        html += "        " + sec("What it does in the body", ul(nut["functions"])) + "\n"

    # Daily values
    dv = nut.get("dailyValues") or {}
    if isinstance(dv, dict) and dv:
        rows = ""
        for k, label in DV_LABEL.items():
            if k in dv and isinstance(dv[k], dict):
                amt = dv[k].get("amount", "")
                src = dv[k].get("source", "")
                rows += f'<tr><td class="pname">{esc(label)}</td><td class="change">{esc(amt)}</td><td>{esc(src)}</td></tr>'
        if rows:
            html += ('        <div class="pd-sec"><h4>How much you need (Daily Value)</h4>'
                     '<div class="table-scroll"><table class="param-table"><thead><tr>'
                     '<th>Group</th><th>Recommended</th><th>Source</th></tr></thead><tbody>'
                     + rows + "</tbody></table></div></div>\n")

    # Best food sources — from the app data
    tfs = nut.get("topFoodSources") or []
    if tfs:
        rows = "".join(
            f'<tr><td class="pname">{esc(f.get("food",""))}</td>'
            f'<td class="change">{esc(f.get("amount",""))}</td>'
            f'<td>{esc(f.get("region",""))}</td></tr>' for f in tfs[:10])
        html += ('        <div class="pd-sec"><h4>Richest food sources</h4>'
                 '<div class="table-scroll"><table class="param-table"><thead><tr>'
                 '<th>Food</th><th>Amount</th><th>Where</th></tr></thead><tbody>'
                 + rows + "</tbody></table></div></div>\n")

    # Computed top free foods (cross-link to Food Explorer)
    fk = FOOD_KEY.get(nut["id"])
    if fk:
        tops = top_foods(foods, fk)
        if tops:
            unit = NUTR_UNIT.get(fk, "")
            chips = "".join(
                f'<a class="cx-badge food" href="{prefix}foods/?q={esc(f["name"])}">'
                f'{esc(f["name"])} <b>{round(v) if v>=10 else round(v,1)}{esc(unit)}</b></a>'
                for f, v in tops)
            html += ('        <div class="pd-sec"><h4>In our food database, per 100&nbsp;g</h4>'
                     f'<div class="cx-foodlist">{chips}</div>'
                     '<p class="tool-note" style="margin-top:8px">Highest among our free foods &mdash; '
                     f'<a href="{prefix}foods/">open the Food Explorer</a> to compare.</p></div>\n')

    # Deficiency
    dc = nut.get("deficiencyConsequences")
    if isinstance(dc, dict) and dc:
        body = "".join(f'<p class="pd-row"><b>{esc(humanize(k))}:</b> {esc(v)}</p>'
                       for k, v in dc.items() if v)
        html += "        " + sec("If you don't get enough", body) + "\n"

    # Toxicity
    tox = nut.get("toxicityRisks")
    if isinstance(tox, dict) and tox:
        body = ""
        if tox.get("upperLimit"):
            body += f'<p class="pd-row"><b>Upper limit:</b> {esc(tox["upperLimit"])}</p>'
        if tox.get("symptoms"):
            body += f'<p class="pd-row">{esc(tox["symptoms"])}</p>'
        html += "        " + sec("Too much", body) + "\n"

    # Bioavailability
    bio = nut.get("bioavailability")
    if isinstance(bio, dict) and bio:
        body = ""
        if bio.get("absorption"):
            body += f'<p class="pd-row">{esc(bio["absorption"])}</p>'
        if bio.get("enhancers"):
            body += f'<p class="pd-row"><b>Helped by:</b> {esc(", ".join(bio["enhancers"]))}</p>'
        if bio.get("inhibitors"):
            body += f'<p class="pd-row"><b>Hindered by:</b> {esc(", ".join(bio["inhibitors"]))}</p>'
        html += "        " + sec("How well you absorb it", body) + "\n"

    # Cooking impact
    if nut.get("cookingImpact"):
        html += "        " + sec("Cooking &amp; storage", f'<p class="pd-row">{esc(nut["cookingImpact"])}</p>') + "\n"

    # Global statistic callout
    if nut.get("globalStatistic"):
        html += f'        <div class="pd-pearl" style="margin-top:18px"><b>Did you know.</b> {esc(nut["globalStatistic"])}</div>\n'

    # Citations button
    if nut.get("citations"):
        html += ('        <p style="margin-top:20px"><button class="ref-open" type="button" data-ref-open>'
                 f'&#128218; Sources &amp; references &middot; {len(nut["citations"])} graded</button></p>\n')

    html += f"""        <div class="notice" style="margin-top:24px">
            <strong>Educational reference only.</strong> Nutrient needs vary with age, sex, health,
            and medication. Not medical or dietary advice. See our <a href="{prefix}disclaimer/">full disclaimer</a>.
        </div>
{iap_plug(prefix, "nutrients",
          f"Track your {name.split(' (')[0]} — and 74 other nutrients — in the app.",
          "Nutrisize Health totals every nutrient from what you actually eat, against targets set "
          "for your age and sex, and flags what's short — across 4,995 foods, on your device.")}
    </div>
</section>
"""
    html += ref_library(nut)
    html += footer(prefix)
    return html


def hub_page(nutrients, prefix="../"):
    title = "Nutrient Encyclopedia — 75 Nutrients, What They Do & Where to Find Them | Nutrisize Health"
    desc = ("A plain-language reference to 75 nutrients — vitamins, minerals, and macronutrients — "
            "with what each does, how much you need, deficiency and toxicity, and the best food "
            "sources. Free and cited.")
    canonical = f"{SITE}/nutrients/"

    jsonld = f"""    <script type="application/ld+json">
    {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {{"@type":"ListItem","position":1,"name":"Home","item":"{SITE}/"}},
      {{"@type":"ListItem","position":2,"name":"Nutrients","item":"{canonical}"}}]}}
    </script>
"""
    by_cat = {"vitamins": [], "minerals": [], "macro": []}
    for n in nutrients:
        by_cat[classify(n)].append(n)

    html = head(title, desc, canonical, prefix, jsonld) + nav(prefix)
    html += f"""
<header class="hero hero-sub">
    <div class="wrap">
        <h1>Nutrient <span class="accent">Encyclopedia</span></h1>
        <p class="tagline">Every nutrient, in plain language and in depth.</p>
        <p class="lede">
            The 75 nutrients Nutrisize Health tracks &mdash; vitamins, minerals, and the
            macronutrients &mdash; each with what it does, how much you need by age and sex,
            what happens when you get too little or too much, and the foods richest in it.
        </p>
    </div>
</header>
"""
    order = [("vitamins", "Vitamins"), ("minerals", "Minerals"), ("macro", "Macronutrients & more")]
    for i, (key, label) in enumerate(order):
        items = sorted(by_cat.get(key, []), key=lambda n: n["name"])
        if not items:
            continue
        tint = ' class="tint"' if i % 2 == 0 else ""
        cards = "".join(
            f'<a class="chip" href="{prefix}nutrients/{slug(n["id"])}/" '
            f'style="text-decoration:none">{esc(n["name"])}</a>' for n in items)
        html += f"""
<section{tint}>
    <div class="wrap">
        <div class="section-head">
            <span class="kicker">{label} &middot; {len(items)}</span>
            <h2>{label}</h2>
        </div>
        <div class="chips">{cards}</div>
    </div>
</section>
"""
    html += f"""
<section>
    <div class="wrap">
{iap_plug(prefix, "nutrients-hub",
          "See these nutrients in what you eat.",
          "The app totals all 75 from your meals against targets for your age and sex, and shows "
          "exactly what's short — across 4,995 foods, private and on your device.")}
    </div>
</section>
"""
    html += footer(prefix)
    return html


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--app-repo", default=DEFAULT_APP_REPO)
    args = ap.parse_args()
    src = os.path.join(args.app_repo, "ios", "NutrisizeHealth", "Resources", "nutrients_data.json")
    nutrients = json.load(open(src))["nutrients"]
    foods = json.load(open(FOODS))["foods"]

    base = os.path.join(ROOT, "nutrients")
    os.makedirs(base, exist_ok=True)
    with open(os.path.join(base, "index.html"), "w") as f:
        f.write(hub_page(nutrients))
    for n in nutrients:
        d = os.path.join(base, slug(n["id"]))
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w") as f:
            f.write(nutrient_page(n, foods))
    print("wrote nutrients/ hub + %d nutrient pages" % len(nutrients))
    # emit slugs for sitemap wiring
    with open(os.path.join(base, ".slugs"), "w") as f:
        f.write("\n".join(slug(n["id"]) for n in nutrients))


if __name__ == "__main__":
    main()
