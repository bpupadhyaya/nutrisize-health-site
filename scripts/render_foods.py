#!/usr/bin/env python3
"""Render /foods/ — the Food Explorer: a searchable, sortable browser of the
app's free-tier foods (assets/data/free/foods.json, produced by
scripts/export_free_tier.py), with a per-food nutrition popup and side-by-side
compare. The table itself is rendered client-side by assets/js/food-explorer.js;
this script emits the page shell so it shares the site head/nav/footer.

Usage: python3 scripts/render_foods.py   (idempotent)
"""
import json
import os

from render_plans import breadcrumb, ROOT, SITE, asset_v, esc, footer, head, iap_plug, nav

DATA = os.path.join(ROOT, "assets", "data", "free", "foods.json")


def page(n_foods, n_categories):
    title = "Food Explorer — Nutrition Facts for %d Foods, Free | Nutrisize Health" % n_foods
    desc = ("Browse %d foods with full nutrition per 100 g — calories, macros, %d+ vitamins "
            "and minerals with %%DV, glycemic category, and nutrient density. Search, filter "
            "by category, and compare foods side by side." % (n_foods, 18))
    canonical = f"{SITE}/foods/"
    prefix = "../"

    extra = f"""    <link rel="stylesheet" href="{prefix}assets/css/explorer.css?v={asset_v('assets/css/explorer.css')}">
    <script src="{prefix}assets/js/food-explorer.js?v={asset_v('assets/js/food-explorer.js')}" defer></script>
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type": "ListItem", "position": 1, "name": "Home", "item": "{SITE}/"}},
        {{"@type": "ListItem", "position": 2, "name": "Food Explorer", "item": "{canonical}"}}
      ]
    }}
    </script>
"""
    html = head(title, desc, canonical, prefix, extra) + nav(prefix) + breadcrumb(prefix, [("Foods", None)])
    html += f"""
<header class="hero hero-sub">
    <div class="wrap">
        <h1>Food <span class="accent">Explorer</span></h1>
        <p class="tagline">The app&rsquo;s food knowledge base — opened up for learning.</p>
        <p class="lede">
            {n_foods} foods from the Nutrisize Health database, free to explore: full
            nutrition per 100&nbsp;g — calories, macros, and 18 vitamins &amp; minerals with
            %&nbsp;Daily Value — plus glycemic category and a nutrient-density score.
            Search, filter, sort, and compare up to four foods side by side.
        </p>
    </div>
</header>

<section>
    <div class="wrap">
        <div class="fx-toolbar">
            <input type="search" id="fx-q" placeholder="Search foods&hellip;" aria-label="Search foods">
            <select id="fx-cat" aria-label="Filter by category">
                <option value="">All categories</option>
            </select>
            <select id="fx-gi" aria-label="Filter by glycemic category">
                <option value="">Any glycemic index</option>
                <option value="low">Low GI</option>
                <option value="low-medium">Low&ndash;medium GI</option>
                <option value="medium-high">Medium&ndash;high GI</option>
                <option value="high">High GI</option>
            </select>
            <select id="fx-sort" aria-label="Sort">
                <option value="name">Sort: A&ndash;Z</option>
                <option value="calories">Sort: Calories</option>
                <option value="protein">Sort: Protein</option>
                <option value="fiber">Sort: Fiber</option>
                <option value="density">Sort: Nutrient density</option>
            </select>
            <button class="fx-reset" id="fx-reset" type="button">Reset</button>
        </div>
        <p class="fx-count" id="fx-count">Loading {n_foods} foods&hellip;</p>
        <div class="table-scroll">
        <table class="param-table fx-table">
            <thead><tr>
                <th>Food</th><th>Category</th>
                <th class="fx-num">kcal</th><th class="fx-num">Protein g</th>
                <th class="fx-num">Carbs g</th><th class="fx-num">Fat g</th>
                <th class="fx-num">Fiber g</th>
                <th>Density</th><th>GI</th><th>Compare</th>
            </tr></thead>
            <tbody id="fx-tbody"></tbody>
        </table>
        </div>
{iap_plug(prefix, "foods-explorer",
          f"{n_foods} foods free here — the app carries all 4,995.",
          "Nutrition Premium unlocks the full food library in the app: every food with "
          "serving-size math, regional names in 10 languages, cooking impact, allergen "
          "flags, and links to the physiological parameters it moves — all offline, all "
          "private, on your device.")}
        <div class="notice" style="margin-top:26px;">
            <strong>Educational reference only.</strong> Values are per 100&nbsp;g from the
            app&rsquo;s reference database (USDA FoodData Central and comparable sources) and
            %&nbsp;Daily Value uses the FDA 2,000-calorie reference — individual needs vary.
            Not medical or dietary advice. See our <a href="../disclaimer/">full disclaimer</a>.
        </div>
    </div>
</section>

<div class="fx-comparebar" id="fx-cmpBar" hidden>
    <span class="fx-cmp-names" id="fx-cmpNames"></span>
    <button class="fx-cmp-go" id="fx-cmpGo" type="button">Compare</button>
    <button class="fx-cmp-clear" id="fx-cmpClear" type="button">Clear</button>
</div>
"""
    html += footer(prefix)
    return html


def main():
    with open(DATA) as f:
        foods = json.load(f)["foods"]
    cats = sorted({fd["category"] for fd in foods})
    out_dir = os.path.join(ROOT, "foods")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(page(len(foods), len(cats)))
    print("wrote foods/index.html (%d foods, %d categories)" % (len(foods), len(cats)))


if __name__ == "__main__":
    main()
