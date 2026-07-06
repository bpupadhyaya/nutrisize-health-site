#!/usr/bin/env python3
"""Render /plans/ pages (hub + 10 category pages) from assets/data/plans/*.json.

Usage: python3 scripts/render_plans.py
Idempotent: overwrites plans/index.html and plans/<key>/index.html.
"""
import hashlib
import json
import math
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "assets", "data", "plans")
FOOD_DB = os.path.join(ROOT, "scripts", "food_db.json")
MEAL_FOODS = os.path.join(ROOT, "scripts", "meal_foods")
SITE = "https://nutrisize.health"

# Per-meal nutrients embedded for the popup, computed from the itemized foods in
# scripts/meal_foods/<key>.json. Order MUST match NUTR in assets/js/plan-popup.js
# (blob values are positional arrays to keep pages small).
NUTRIENT_ORDER = [
    "fiber", "sugar", "sodium",
    "vitaminA", "vitaminC", "vitaminD", "vitaminE", "vitaminK",
    "vitaminB1", "vitaminB2", "vitaminB3", "vitaminB6", "vitaminB9", "vitaminB12",
    "calcium", "iron", "magnesium", "phosphorus", "potassium", "zinc", "selenium",
]
# Per-food per-100g arrays in the page food table add the four macros up front.
# Order MUST match FOOD_NUTR in assets/js/plan-popup.js.
FOOD_NUTRIENT_ORDER = ["calories", "protein", "carbohydrates", "fat"] + NUTRIENT_ORDER

CATS = [
    "male-child", "male-teen", "male-young-adult", "male-middle-age", "male-older-adult",
    "female-child", "female-teen", "female-young-adult", "female-middle-age", "female-older-adult",
]
EMOJI = {
    "male-child": "&#128102;", "male-teen": "&#129489;&#8205;&#127891;",
    "male-young-adult": "&#129485;", "male-middle-age": "&#128104;",
    "male-older-adult": "&#128116;",
    "female-child": "&#128103;", "female-teen": "&#128105;&#8205;&#127891;",
    "female-young-adult": "&#129485;&#8205;&#9792;&#65039;", "female-middle-age": "&#128105;",
    "female-older-adult": "&#128117;",
}

GREEN = "#178a5e"
GREEN_DK = "#0b3d2e"
BLUE = "#1268b3"
AMBER = "#d97706"
LINE = "#dcebe3"
INK_FAINT = "#6b7f74"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def esc_attr(s):
    # Attribute-safe: also escape quotes so data-* values can't break the tag.
    return esc(s).replace('"', "&quot;").replace("'", "&#39;")


def asset_v(rel):
    """Short content hash for cache-busting ?v= params on popup assets, so
    browsers pick up JS/CSS changes as soon as the HTML does."""
    path = os.path.join(ROOT, rel)
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


def meal_nid(day, meal):
    return day.lower() + "-" + meal.lower().replace(" ", "-")


# --- household portion labels ("≈ 2 eggs", "≈ 1½ cups cooked") -------------

_SIZE_ADJ = {"small", "medium", "large", "extra-large", "whole", "baby"}
_NO_INFLECT = {"oz", "g", "ml", "tbsp", "tsp", "fl"}
_FRACTIONS = {0.25: "¼", 0.5: "½", 0.75: "¾"}


def _plural(word):
    if word in _NO_INFLECT:
        return word
    if word.endswith("y") and len(word) > 1 and word[-2] not in "aeiou":
        return word[:-1] + "ies"
    if word.endswith(("s", "x", "z", "ch", "sh")):
        return word + "es"
    return word + "s"


def _singular(word):
    if word in _NO_INFLECT:
        return word
    if word.endswith("ies"):
        return word[:-3] + "y"
    if word.endswith(("ches", "shes", "xes", "zes", "ses")):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _inflect(rest, count):
    # A scaled count makes any parenthetical detail wrong ("1 cup (8 oz)"
    # quartered is not "¼ cup (8 oz)") — drop it unless the count stayed 1.
    if count != 1:
        rest = re.sub(r"\s*\([^)]*\)\s*$", "", rest)
    words = rest.split()
    if not words:
        return rest
    i = 1 if words[0] in _SIZE_ADJ and len(words) > 1 else 0
    if words[i] not in _SIZE_ADJ:
        words[i] = _plural(words[i]) if count > 1 else _singular(words[i])
    return " ".join(words)


def _fmt_count(c):
    whole, frac = int(c), round(c - int(c), 2)
    if frac in _FRACTIONS:
        return (str(whole) if whole else "") + _FRACTIONS[frac]
    return str(whole)


def portion_label(grams, servings):
    """Best household-measure label for a gram amount, or '' if none is close.
    Serving descriptions look like '1 cup cooked' / '3 oz portion' / '2 small
    chops'; the count is scaled and the unit word inflected to match."""
    best = None
    for desc, g in servings or []:
        parts = desc.split(None, 1)
        if len(parts) != 2 or not parts[0].isdigit() or not g:
            continue
        base_n, rest = int(parts[0]), parts[1]
        units = grams / g * base_n
        snapped = round(units * 4) / 4.0
        if not 0.25 <= snapped <= 6 or abs(units - snapped) / units > 0.13:
            continue
        roundness = 0 if snapped == int(snapped) else (1 if snapped * 2 == int(snapped * 2) else 2)
        score = (roundness, abs(snapped - 1.5), abs(units - snapped))
        if best is None or score < best[0]:
            best = (score, snapped, rest)
    if best is None:
        return ""
    _, count, rest = best
    return "≈ " + _fmt_count(count) + " " + _inflect(rest, count)


def _round_nutrient(v):
    if v >= 100:
        return int(round(v))
    if v >= 10:
        return round(v, 1)
    return round(v, 2)


def meal_nutrient_blob(plan, food_db):
    """Popup data for one plan page, or {} when the plan has no
    scripts/meal_foods mapping yet (pages then render without it):

      {"foods": [[name, [per-100g values in FOOD_NUTRIENT_ORDER]], ...],
       "meals": {nid: {"t": [meal totals in NUTRIENT_ORDER],
                       "i": [[food index, grams, portion label], ...],
                       "s": day fiber scale}}}
    """
    path = os.path.join(MEAL_FOODS, plan["key"] + ".json")
    if not food_db or not os.path.exists(path):
        return {}
    with open(path) as f:
        mapping = json.load(f)
    fiber_i = NUTRIENT_ORDER.index("fiber")
    foods_tbl, food_idx = [], {}

    def index_food(fid):
        if fid not in food_idx:
            food = food_db[fid]
            food_idx[fid] = len(foods_tbl)
            foods_tbl.append([food["name"],
                              [_round_nutrient(food["n"].get(k, 0))
                               for k in FOOD_NUTRIENT_ORDER]])
        return food_idx[fid]

    meals = {}
    for day in plan["week"]:
        day_map = mapping.get(day["day"], {})
        day_meals = []
        for meal in day["meals"]:
            foods = day_map.get(meal["meal"])
            if not foods:
                continue
            totals = [0.0] * len(NUTRIENT_ORDER)
            items = []
            for item in foods:
                food = food_db.get(item["id"])
                if not food:
                    continue
                scale = item["g"] / 100.0
                for i, k in enumerate(NUTRIENT_ORDER):
                    totals[i] += food["n"].get(k, 0) * scale
                items.append([index_food(item["id"]), item["g"],
                              portion_label(item["g"], food.get("sv"))])
            day_meals.append((meal_nid(day["day"], meal["meal"]), totals, items))
        # The page already publishes a day-total fiber (mealTotals.fiberG); scale
        # the meals' fiber to sum to it so the popup never contradicts the table.
        # The same factor is applied per food in the popup (via "s") so foods sum
        # to their meal and meals sum to the day.
        fiber_sum = sum(t[fiber_i] for _, t, _ in day_meals)
        pub_fiber = day.get("mealTotals", {}).get("fiberG")
        fiber_scale = pub_fiber / fiber_sum if fiber_sum > 0 and pub_fiber else 1.0
        for nid, totals, items in day_meals:
            totals[fiber_i] *= fiber_scale
            meals[nid] = {"t": [_round_nutrient(v) for v in totals],
                          "i": items, "s": round(fiber_scale, 3)}
    return {"foods": foods_tbl, "meals": meals}


# ---------------------------------------------------------------- SVG charts

def energy_chart(plan):
    week = plan["week"]
    target = plan["profile"]["targetKcal"]
    intakes = [d["mealTotals"]["kcal"] for d in week]
    burns = [d["exercise"]["kcalBurned"] for d in week]
    W, H = 560, 250
    ml, mr, mt, mb = 50, 8, 14, 30
    pw, ph = W - ml - mr, H - mt - mb
    ymax = max(max(intakes), target) * 1.12
    step = 500 if ymax > 1600 else 250
    ymax = math.ceil(ymax / step) * step

    def y(v):
        return mt + ph * (1 - v / ymax)

    parts = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
             f'aria-label="Daily energy intake and exercise burn across the week">']
    for gv in range(0, ymax + 1, step):
        gy = y(gv)
        parts.append(f'<line x1="{ml}" y1="{gy:.1f}" x2="{W - mr}" y2="{gy:.1f}" stroke="{LINE}" stroke-width="1"/>')
        parts.append(f'<text x="{ml - 7}" y="{gy + 4:.1f}" text-anchor="end" font-size="10.5" fill="{INK_FAINT}">{gv:,}</text>')
    gw = pw / 7
    bw = min(26, gw * 0.30)
    for i, d in enumerate(week):
        cx = ml + gw * i + gw / 2
        ix, bx = cx - bw - 2, cx + 2
        iy, by = y(intakes[i]), y(burns[i])
        parts.append(f'<rect x="{ix:.1f}" y="{iy:.1f}" width="{bw:.1f}" height="{mt + ph - iy:.1f}" rx="5" fill="{GREEN}"/>')
        parts.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{mt + ph - by:.1f}" rx="5" fill="{BLUE}"/>')
        parts.append(f'<text x="{cx:.1f}" y="{H - 12}" text-anchor="middle" font-size="11" font-weight="600" '
                     f'fill="{INK_FAINT}">{d["day"][:3]}</text>')
    ty = y(target)
    parts.append(f'<line x1="{ml}" y1="{ty:.1f}" x2="{W - mr}" y2="{ty:.1f}" stroke="{GREEN_DK}" '
                 f'stroke-width="1.6" stroke-dasharray="6 5"/>')
    parts.append(f'<text x="{W - mr}" y="{ty - 6:.1f}" text-anchor="end" font-size="10.5" font-weight="700" '
                 f'fill="{GREEN_DK}">target {target:,} kcal</text>')
    parts.append("</svg>")
    legend = (f'<div class="legend"><span><span class="sw" style="background:{GREEN}"></span>Intake (kcal)</span>'
              f'<span><span class="sw" style="background:{BLUE}"></span>Exercise burn (kcal)</span>'
              f'<span><span class="sw" style="background:{GREEN_DK};height:3px;vertical-align:3px"></span>Daily target</span></div>')
    return "".join(parts) + legend


def macro_donut(plan):
    p = plan["profile"]
    pk, ck, fk = p["proteinG"] * 4, p["carbsG"] * 4, p["fatG"] * 9
    tot = pk + ck + fk
    shares = [("Protein", pk / tot, GREEN, f'{p["proteinG"]} g'),
              ("Carbs", ck / tot, BLUE, f'{p["carbsG"]} g'),
              ("Fat", fk / tot, AMBER, f'{p["fatG"]} g')]
    W = H = 210
    cx = cy = W / 2
    r = 74
    C = 2 * math.pi * r
    parts = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
             f'aria-label="Macronutrient split of daily calories">']
    off = 0.0
    for name, fr, color, grams in shares:
        dash = fr * C
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="26" '
                     f'stroke-dasharray="{dash:.2f} {C - dash:.2f}" stroke-dashoffset="{-off:.2f}" '
                     f'transform="rotate(-90 {cx} {cy})"/>')
        off += dash
    parts.append(f'<text x="{cx}" y="{cy - 4}" text-anchor="middle" font-size="26" font-weight="800" '
                 f'fill="{GREEN_DK}">{p["targetKcal"]:,}</text>')
    parts.append(f'<text x="{cx}" y="{cy + 16}" text-anchor="middle" font-size="11.5" '
                 f'fill="{INK_FAINT}">kcal / day</text>')
    parts.append("</svg>")
    leg = "".join(f'<span><span class="sw" style="background:{c}"></span>{n} {g} &middot; {fr * 100:.0f}%</span>'
                  for n, fr, c, g in shares)
    return "".join(parts) + f'<div class="legend">{leg}</div>'


def micro_bars(plan):
    rows = plan["micronutrients"]
    W = 560
    rh, top = 34, 8
    H = top + rh * len(rows) + 14
    lab_w, pct_w = 118, 46
    bx = lab_w + 8
    bw_full = W - bx - pct_w
    cap = 130.0
    parts = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
             f'aria-label="Micronutrient coverage versus recommended intake">']
    x100 = bx + bw_full * (100 / cap)
    parts.append(f'<line x1="{x100:.1f}" y1="{top}" x2="{x100:.1f}" y2="{H - 12}" stroke="{INK_FAINT}" '
                 f'stroke-width="1" stroke-dasharray="3 4"/>')
    parts.append(f'<text x="{x100:.1f}" y="{H - 2}" text-anchor="middle" font-size="9.5" fill="{INK_FAINT}">100% of RDA</text>')
    for i, m in enumerate(rows):
        yc = top + rh * i + rh / 2
        pct = float(m["percentMet"])
        fill = GREEN if pct >= 100 else AMBER
        bw = bw_full * min(pct, cap) / cap
        parts.append(f'<text x="{lab_w}" y="{yc + 4:.1f}" text-anchor="end" font-size="11.5" font-weight="600" '
                     f'fill="#40544a">{esc(m["name"])}</text>')
        parts.append(f'<rect x="{bx}" y="{yc - 8:.1f}" width="{bw_full}" height="16" rx="8" fill="#eef4f0"/>')
        parts.append(f'<rect x="{bx}" y="{yc - 8:.1f}" width="{bw:.1f}" height="16" rx="8" fill="{fill}"/>')
        parts.append(f'<text x="{W - 2}" y="{yc + 4:.1f}" text-anchor="end" font-size="11.5" font-weight="700" '
                     f'fill="{fill}">{pct:.0f}%</text>')
    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------- page shell

def head(title, desc, canonical, prefix, extra=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(desc)}">
    <link rel="canonical" href="{canonical}">
    <meta property="og:title" content="{esc(title)}">
    <meta property="og:description" content="{esc(desc)}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:image" content="{SITE}/assets/img/og-image.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Nutrisize Health">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:image" content="{SITE}/assets/img/og-image.png">
    <link rel="icon" type="image/png" href="{prefix}assets/img/favicon.png">
    <link rel="apple-touch-icon" href="{prefix}assets/img/apple-touch-icon.png">
    <link rel="manifest" href="/site.webmanifest">
    <meta name="theme-color" content="#0b3d2e">
    <link rel="stylesheet" href="{prefix}assets/fonts/inter.css">
    <link rel="stylesheet" href="{prefix}assets/css/style.css">
    <link rel="stylesheet" href="{prefix}assets/css/plans.css?v={asset_v('assets/css/plans.css')}">
    <script src="{prefix}assets/js/plan-popup.js?v={asset_v('assets/js/plan-popup.js')}" defer></script>
    <script src="{prefix}assets/js/ref-modal.js?v={asset_v('assets/js/ref-modal.js')}" defer></script>
{extra}</head>
<body>
"""


def nav(prefix, here="plans"):
    return f"""
<nav>
    <div class="nav-inner">
        <a href="{prefix}" class="nav-logo">
            <img src="{prefix}assets/img/favicon.png" alt="" width="34" height="34">
            Nutrisize Health
        </a>
        <ul class="nav-links">
            <li><a href="{prefix}#features">Features</a></li>
            <li><a href="{prefix}plans/">Plans</a></li>
            <li><a href="{prefix}parameters/">Parameters</a></li>
            <li><a href="{prefix}#privacy">Privacy</a></li>
            <li><a href="{prefix}about/">About</a></li>
            <li><a href="{prefix}support/">Support</a></li>
            <li><a href="{prefix}#download" class="nav-cta">Get the App</a></li>
        </ul>
        <button class="mobile-menu-btn" onclick="document.querySelector('.nav-links').classList.toggle('show')" aria-label="Menu">&#9776;</button>
    </div>
</nav>
"""


def footer(prefix):
    return f"""
<footer>
    <div class="footer-inner">
        <ul class="footer-links">
            <li><a href="{prefix}about/">About</a></li>
            <li><a href="{prefix}plans/">Plans</a></li>
            <li><a href="{prefix}parameters/">Parameters</a></li>
            <li><a href="{prefix}privacy/">Privacy Policy</a></li>
            <li><a href="{prefix}disclaimer/">Disclaimer</a></li>
            <li><a href="{prefix}support/">Support</a></li>
            <li><a href="{prefix}survey/">Survey</a></li>
            <li><a href="https://www.facebook.com/nutrisizehealth" target="_blank" rel="noopener">Facebook</a></li>
            <li><a href="https://www.linkedin.com/company/nutrisizehealth" target="_blank" rel="noopener">LinkedIn</a></li>
            <li><a href="https://equalinformation.com" target="_blank" rel="noopener">EqualInformation</a></li>
        </ul>
        <p class="footer-copy">Contact: <a href="mailto:contact@nutrisize.health">contact@nutrisize.health</a> &middot; <a href="mailto:nutrisize.universal@gmail.com">nutrisize.universal@gmail.com</a><br>
            &copy; 2026 EqualInformation, LLC. All rights reserved.</p>
    </div>
</footer>

</body>
</html>
"""


def app_plug(prefix, text):
    """Quiet inline pointer to the app for things the static samples can't do."""
    return f"""        <div class="app-plug">
            <img src="{prefix}assets/img/favicon.png" alt="" width="34" height="34">
            <p>{text} <a href="{prefix}#download">Get the app &rarr;</a></p>
        </div>
"""


# Authoritative standards the sample plans are built on — shown in the
# sources & references window (assets/js/ref-modal.js) on every plan page.
PLAN_REFS = [
    ("FDA", "Daily Value on Nutrition and Supplement Facts Labels — the %DV reference amounts "
            "used throughout these plans and the meal popups.",
     "https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"),
    ("NIH ODS", "Nutrient Recommendations and Databases — Dietary Reference Intakes (DRIs) from "
                "the National Academies, the basis for energy, protein, fiber, and water targets.",
     "https://ods.od.nih.gov/HealthInformation/nutrientrecommendations.aspx"),
    ("USDA / HHS", "Dietary Guidelines for Americans, 2020–2025 — meal patterns and life-stage "
                   "guidance the weekly structure follows.",
     "https://www.dietaryguidelines.gov/"),
    ("USDA", "FoodData Central — the reference food-composition database behind per-food "
             "nutrient values.",
     "https://fdc.nal.usda.gov/"),
    ("WHO", "Guideline: Sugars intake for adults and children — the basis for added-sugar "
            "limits shown in each profile.",
     "https://www.who.int/publications/i/item/9789241549028"),
    ("WHO", "Guideline: Sodium intake for adults and children — the basis for sodium limits "
            "shown in each profile.",
     "https://www.who.int/publications/i/item/9789241504836"),
    ("WHO", "Guidelines on physical activity and sedentary behaviour (2020) — the weekly "
            "movement targets the exercise plans are sized to.",
     "https://www.who.int/publications/i/item/9789240015128"),
]


def plan_ref_library(prefix):
    rows = "".join(
        f'<div class="rm-cite"><span>'
        f'<a href="{url}" target="_blank" rel="noopener">{esc(text)}</a>'
        f' <span class="rm-src">{esc(org)}</span></span></div>'
        for org, text, url in PLAN_REFS)
    plug = (f'<div class="app-plug" style="margin-top:24px">'
            f'<img src="{prefix}assets/img/favicon.png" alt="" width="34" height="34">'
            f"<p>The app is built on these same standards — 4,995 foods with reference "
            f"nutrient data and targets computed to DRI and WHO guidance, personalized to "
            f'your profile. <a href="{prefix}#download">Get the app &rarr;</a></p></div>')
    return ('<div id="ref-library"><p class="rm-legend">The standards these sample plans are '
            'built on. Links open in a new tab.</p>' + rows + plug + "</div>\n")


DISCLAIMER = """
    <div class="notice">
        <strong>Educational example only.</strong> These sample plans assume a normal, healthy
        person of average size for the group and are provided for education and practice — they
        are not medical or dietary advice. Individual needs vary with health conditions,
        medications, and goals; consult a qualified professional before changing your diet or
        exercise routine. See our <a href="../../disclaimer/">full disclaimer</a>.
    </div>
"""


# ---------------------------------------------------------------- plan page

def plan_page(plan, nblob=None):
    key = plan["key"]
    p = plan["profile"]
    gender, group, ages = plan["gender"], plan["ageGroup"], plan["ageRange"]
    title = f"Sample Weekly Plan — {gender}, {group} ({ages}) | Nutrisize Health"
    desc = (f"A dietitian-style sample week of meals and exercise for a healthy {gender.lower()} "
            f"{group.lower()} ({ages}): {p['targetKcal']:,} kcal/day, macros, micronutrients, and the "
            f"physiological changes to expect.")
    canonical = f"{SITE}/plans/{key}/"
    prefix = "../../"

    jsonld = f"""    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type": "ListItem", "position": 1, "name": "Home", "item": "{SITE}/"}},
        {{"@type": "ListItem", "position": 2, "name": "Sample Weekly Plans", "item": "{SITE}/plans/"}},
        {{"@type": "ListItem", "position": 3, "name": "{gender}, {group} ({ages})", "item": "{canonical}"}}
      ]
    }}
    </script>
"""
    html = head(title, desc, canonical, prefix, jsonld) + nav(prefix)

    # hero + profile stats
    stats = [
        (f'{p["heightCm"]}<small> cm</small>', "Height"),
        (f'{p["weightKg"]}<small> kg</small>', "Weight"),
        (f'{p["bmi"]}', "BMI"),
        (f'{p["bmrKcal"]:,}<small> kcal</small>', "BMR"),
        (f'{p["tdeeKcal"]:,}<small> kcal</small>', "TDEE"),
        (f'{p["targetKcal"]:,}<small> kcal</small>', "Daily target"),
        (f'{p["proteinG"]}<small> g</small>', "Protein"),
        (f'{p["carbsG"]}<small> g</small>', "Carbs"),
        (f'{p["fatG"]}<small> g</small>', "Fat"),
        (f'{p["fiberG"]}<small> g</small>', "Fiber"),
        (f'{p["waterL"]}<small> L</small>', "Water"),
    ]
    pstats = "".join(f'<div class="pstat"><div class="v">{v}</div><div class="k">{k}</div></div>'
                     for v, k in stats)
    html += f"""
<header class="plan-hero">
    <div class="wrap">
        <div class="crumb"><a href="../">Sample Weekly Plans</a> / {gender} / {group}</div>
        <h1>{EMOJI[key]} {gender}, {group} <span style="color:var(--green-600)">({ages})</span></h1>
        <p class="assume">Assumes a normal, healthy {gender.lower()} around age {plan["refAge"]},
        {p["heightCm"]} cm and {p["weightKg"]} kg (BMI {p["bmi"]}), {p["activity"].lower()}.
        A full week of meals and movement, sized to a {p["targetKcal"]:,} kcal/day target.</p>
        <div class="profile-grid">{pstats}</div>
    </div>
</header>
"""

    # charts
    html += f"""
<section class="tint">
    <div class="wrap">
        <div class="section-head">
            <span class="kicker">The week in numbers</span>
            <h2>Energy, macros, and micronutrients</h2>
        </div>
        <div class="chart-row">
            <div class="chart-card">
                <h3>Daily energy balance</h3>
                <div class="sub">Calories eaten vs. burned in planned exercise, each day</div>
                {energy_chart(plan)}
            </div>
            <div class="chart-card">
                <h3>Macro split</h3>
                <div class="sub">Share of daily calories by macronutrient</div>
                {macro_donut(plan)}
            </div>
            <div class="chart-card">
                <h3>Micronutrient coverage</h3>
                <div class="sub">Weekly average vs. recommended intake for this group</div>
                {micro_bars(plan)}
            </div>
        </div>
    </div>
</section>
"""

    # week at a glance
    rows = []
    for d in plan["week"]:
        kc = {m["meal"]: m["kcal"] for m in d["meals"]}
        ex = d["exercise"]
        rows.append(f"""            <tr>
                <td class="day">{d["day"]}</td>
                <td class="num">{kc.get("Breakfast", 0):,}</td>
                <td class="num">{kc.get("Lunch", 0):,}</td>
                <td class="num">{kc.get("Snack", 0):,}</td>
                <td class="num">{kc.get("Dinner", 0):,}</td>
                <td class="num"><span class="kcal-chip">{d["mealTotals"]["kcal"]:,} kcal</span></td>
                <td>{esc(ex["activity"])} &middot; {ex["durationMin"]} min</td>
                <td class="num"><span class="burn-chip">&minus;{ex["kcalBurned"]:,} kcal</span></td>
            </tr>""")
    html += f"""
<section>
    <div class="wrap">
        <div class="section-head">
            <span class="kicker">Week at a glance</span>
            <h2>Seven days, planned end to end</h2>
            <p>Calories per meal, daily totals, and the movement that pairs with them.</p>
        </div>
        <div class="table-scroll">
        <table class="plan-table">
            <thead><tr>
                <th>Day</th><th>Breakfast</th><th>Lunch</th><th>Snack</th><th>Dinner</th>
                <th>Intake</th><th>Exercise</th><th>Burn</th>
            </tr></thead>
            <tbody>
{chr(10).join(rows)}
            </tbody>
        </table>
        </div>
{app_plug(prefix, "The exercise column shows one sensible week for this profile. "
                  "The app plans movement around <em>you</em> — 5,404 exercises matched to "
                  "your equipment, fitness level, and schedule, re-balanced as you log workouts.")}    </div>
</section>
"""

    # day-by-day details
    cards = []
    for i, d in enumerate(plan["week"]):
        mt = d["mealTotals"]
        meal_rows = "".join(f"""                <tr class="meal-row" tabindex="0" role="button" aria-label="See nutrition for {esc_attr(m["meal"])}" data-nid="{meal_nid(d["day"], m["meal"])}" data-meal="{esc_attr(m["meal"])}" data-items="{esc_attr(m["items"])}" data-kcal="{m["kcal"]}" data-protein="{m["proteinG"]}" data-carbs="{m["carbsG"]}" data-fat="{m["fatG"]}">
                    <td class="mname">{esc(m["meal"])}</td>
                    <td>{esc(m["items"])}</td>
                    <td class="num">{m["kcal"]:,}</td>
                    <td class="num">{m["proteinG"]}</td>
                    <td class="num">{m["carbsG"]}</td>
                    <td class="num">{m["fatG"]}</td>
                </tr>
""" for m in d["meals"])
        ex = d["exercise"]
        cards.append(f"""        <details class="day-card"{" open" if i == 0 else ""}>
            <summary>
                <span class="dname">{d["day"]}</span>
                <span class="dhl">{esc(d["highlight"])}</span>
                <span class="kcal-chip">{mt["kcal"]:,} kcal</span>
                <span class="arrow">&#8250;</span>
            </summary>
            <div class="day-body">
                <table class="meal-table">
                    <thead><tr><th>Meal</th><th>Foods</th><th class="num">kcal</th>
                        <th class="num">Protein g</th><th class="num">Carbs g</th><th class="num">Fat g</th></tr></thead>
                    <tbody>
{meal_rows}                    <tr class="total"><td>Total</td><td>Fiber {mt["fiberG"]} g</td>
                        <td class="num">{mt["kcal"]:,}</td><td class="num">{mt["proteinG"]}</td>
                        <td class="num">{mt["carbsG"]}</td><td class="num">{mt["fatG"]}</td></tr>
                    </tbody>
                </table>
                <div class="day-exercise">
                    <span><strong>Exercise:</strong> {esc(ex["activity"])}</span>
                    <span><strong>{ex["durationMin"]} min</strong> &middot; {esc(ex["intensity"])}</span>
                    <span><strong>&asymp;{ex["kcalBurned"]:,} kcal</strong> burned</span>
                    <span>{esc(ex["focus"])}</span>
                </div>
            </div>
        </details>
""")
    html += f"""
<section class="tint">
    <div class="wrap">
        <div class="section-head">
            <span class="kicker">Day by day</span>
            <h2>Every meal, with full macros</h2>
            <p>Open a day to see the foods, portions by calories, and the exercise that completes it.</p>
        </div>
        <div class="day-list">
{"".join(cards)}        </div>
{app_plug(prefix, "These sample weeks assume a typical mixed diet. Eat vegetarian, vegan, "
                  "halal, or around allergies? The app generates this same week for your "
                  "diet and cuisine, from 4,995 foods, sized to your own profile.")}    </div>
</section>
"""

    # physiological params
    prow = "".join(f"""            <tr>
                <td class="pname">{esc(q["name"])}</td>
                <td>{esc(q["typical"])}</td>
                <td class="change">{esc(q["expectedChange"])}</td>
                <td>{esc(q["driver"])}</td>
            </tr>
""" for q in plan["physiologicalParams"])
    html += f"""
<section>
    <div class="wrap">
        <div class="section-head">
            <span class="kicker">Physiological parameters</span>
            <h2>What this plan moves, and why</h2>
            <p>Typical healthy values for this group, and the direction consistent nutrition + exercise nudges them.
            The app tracks 201 parameters like these across 16 body systems &mdash;
            <a href="../../parameters/">see which to check daily, monthly, and yearly</a>.</p>
        </div>
        <div class="table-scroll">
        <table class="param-table">
            <thead><tr><th>Parameter</th><th>Typical healthy range</th><th>Expected change</th><th>Why</th></tr></thead>
            <tbody>
{prow}            </tbody>
        </table>
        </div>
    </div>
</section>
"""

    # changes
    nut = "".join(f"<li>{esc(x)}</li>" for x in plan["changes"]["nutrition"])
    exl = "".join(f"<li>{esc(x)}</li>" for x in plan["changes"]["exercise"])
    html += f"""
<section class="tint">
    <div class="wrap">
        <div class="section-head">
            <span class="kicker">Physiological changes</span>
            <h2>What a consistent week does for the body</h2>
        </div>
        <div class="changes-grid">
            <div class="changes-col">
                <h3>&#129367; From the nutrition plan</h3>
                <ul>{nut}</ul>
            </div>
            <div class="changes-col ex">
                <h3>&#127939; From the exercise plan</h3>
                <ul>{exl}</ul>
            </div>
        </div>
        <p style="margin-top:20px; color: var(--ink-soft); font-size: 14.5px; text-align:center; max-width: 760px; margin-left:auto; margin-right:auto;">{esc(plan["notes"])}</p>
    </div>
</section>
"""

    # downloads + other categories
    chips = "".join(
        f'<a href="../{c}/"{" class=" + chr(34) + "current" + chr(34) if c == key else ""}>'
        f'{EMOJI[c]} {c.replace("-", " ").title().replace("Male", "Male,").replace("Female", "Female,")}</a>'
        for c in CATS)
    html += f"""
<section>
    <div class="wrap">
        <div class="section-head">
            <span class="kicker">Make it yours</span>
            <h2>Download and practice</h2>
            <p>Take this plan with you, or build your own with the auto-calculating worksheet.</p>
        </div>
        <div class="plan-cta">
            <a class="btn" href="../../assets/downloads/nutrisize-plan-{key}.pdf" download>&#11015;&#65039; Download this plan (PDF)</a>
            <a class="btn outline" href="../worksheet/">&#129513; Open the interactive worksheet</a>
        </div>
        <p style="text-align:center; margin-top:18px;">
            <button class="ref-open" type="button" data-ref-open>&#128218; Sources &amp; references
            <span style="font-weight:500; color:#8a9a91;">&middot; the standards this plan is built on</span></button>
        </p>
{DISCLAIMER}
        <div class="section-head" style="margin-top:44px; margin-bottom:20px;">
            <h2 style="font-size:22px">Explore other groups</h2>
        </div>
        <div class="cat-chips">{chips}</div>
    </div>
</section>
"""
    if nblob:
        html += ('<script type="application/json" id="nutri-data">'
                 + json.dumps(nblob, separators=(",", ":")) + "</script>\n")
    html += plan_ref_library(prefix)
    html += footer(prefix)
    return html


# ---------------------------------------------------------------- hub page

def hub_page(plans):
    title = "Sample Weekly Plans — Nutrition & Exercise by Age and Sex | Nutrisize Health"
    desc = ("Free dietitian-style sample weeks — meals, macros, micronutrients, and exercise — "
            "for males and females across five life stages, plus an auto-calculating worksheet.")
    canonical = f"{SITE}/plans/"
    prefix = "../"
    html = head(title, desc, canonical, prefix) + nav(prefix)
    html += """
<header class="hero hero-sub">
    <div class="wrap">
        <h1>Sample <span class="accent">Weekly Plans</span></h1>
        <p class="tagline">A full week of meals and movement — for every stage of life.</p>
        <p class="lede">
            Ten complete example weeks, one for each life stage — every meal with calories and
            macros, day-by-day exercise, micronutrient coverage, and the physiological changes a
            consistent week drives. Built the way the app thinks, sized for a normal healthy
            person in each group.
        </p>
    </div>
</header>

<section>
    <div class="wrap">
        <div class="plan-groups">
"""
    for gender in ("Male", "Female"):
        cls = "" if gender == "Male" else " f"
        html += f'            <div class="plan-group">\n                <h3>{gender}</h3>\n                <div class="plan-cards">\n'
        for plan in plans:
            if plan["gender"] != gender:
                continue
            k, p = plan["key"], plan["profile"]
            html += f"""                    <a class="plan-card{cls}" href="{k}/">
                        <span class="badge">{EMOJI[k]}</span>
                        <span><h4>{plan["ageGroup"]} <span style="color:var(--ink-faint); font-weight:600">({plan["ageRange"]})</span></h4>
                        <span class="sub">{p["heightCm"]} cm &middot; {p["weightKg"]} kg &middot; BMI {p["bmi"]}</span></span>
                        <span class="kcal"><span class="n">{p["targetKcal"]:,}</span><br><span class="l">kcal/day</span></span>
                    </a>
"""
        html += "                </div>\n            </div>\n"
    html += f"""        </div>
{app_plug(prefix, "Looking for a vegetarian, vegan, or allergy-aware version? These pages teach "
                  "the structure on typical healthy profiles; the app builds the week around "
                  "your diet, cuisine, and calorie needs — and adapts it as your body changes.")}    </div>
</section>

<section class="tint">
    <div class="wrap">
        <div class="section-head">
            <span class="kicker">Practice</span>
            <h2>Build your own week</h2>
            <p>The interactive worksheet computes your BMI, BMR, calorie target, and macros from
            your own numbers — then auto-totals your week as you plan it. Download it to keep
            practicing offline, or print the blank sheet.</p>
        </div>
        <div class="plan-cta">
            <a class="btn" href="worksheet/">&#129513; Open the interactive worksheet</a>
            <a class="btn outline" href="../assets/downloads/nutrisize-weekly-worksheet.html" download>&#11015;&#65039; Offline worksheet (HTML)</a>
            <a class="btn outline" href="../assets/downloads/nutrisize-weekly-worksheet-blank.pdf" download>&#128424;&#65039; Printable blank sheet (PDF)</a>
        </div>
    </div>
</section>

<section>
    <div class="wrap">
        <div class="section-head">
            <span class="kicker">How to use these</span>
            <h2>From example to habit</h2>
        </div>
        <div class="grid">
            <div class="card">
                <div class="icon">&#128269;</div>
                <h3>1. Find your group</h3>
                <p>Pick the plan closest to your age and sex. The profile chips show the assumed
                height, weight, and calorie target — note how yours differ.</p>
            </div>
            <div class="card">
                <div class="icon blue">&#128203;</div>
                <h3>2. Study the shape</h3>
                <p>Notice the patterns, not the exact foods: protein at every meal, fiber all day,
                colorful variety, and movement most days with one easy day.</p>
            </div>
            <div class="card">
                <div class="icon">&#9999;&#65039;</div>
                <h3>3. Practice your own</h3>
                <p>Use the worksheet to compute your targets, then draft your week. In the app,
                the same thinking runs live — with 4,995 foods and 5,404 exercises.</p>
            </div>
        </div>
"""
    html += DISCLAIMER.replace("../../disclaimer/", "../disclaimer/")
    html += """    </div>
</section>
"""
    html += footer(prefix)
    return html


# ---------------------------------------------------------------- main

def main():
    plans = []
    for key in CATS:
        path = os.path.join(DATA, key + ".json")
        with open(path) as f:
            plans.append(json.load(f))

    food_db = {}
    if os.path.exists(FOOD_DB):
        with open(FOOD_DB) as f:
            food_db = json.load(f)

    for plan in plans:
        nblob = meal_nutrient_blob(plan, food_db)
        out_dir = os.path.join(ROOT, "plans", plan["key"])
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.html"), "w") as f:
            f.write(plan_page(plan, nblob))
        print("wrote plans/%s/index.html (%d meals, %d foods)"
              % (plan["key"], len(nblob.get("meals", {})), len(nblob.get("foods", []))))

    with open(os.path.join(ROOT, "plans", "index.html"), "w") as f:
        f.write(hub_page(plans))
    print("wrote plans/index.html")


if __name__ == "__main__":
    main()
