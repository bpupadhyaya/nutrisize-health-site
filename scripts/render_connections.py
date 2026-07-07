#!/usr/bin/env python3
"""Render /connections/ — the Connections Explorer: the app's cross-domain
knowledge graph (nutrition ↔ physiology ↔ exercise) in every direction, built
from the free-tier exports in assets/data/free/. The interactive views are
rendered client-side by assets/js/connections.js; this emits the page shell so
it shares the site head/nav/footer.

Usage: python3 scripts/render_connections.py   (idempotent)
"""
import json
import os

from render_plans import breadcrumb, ROOT, SITE, asset_v, footer, head, iap_plug, nav

FREE = os.path.join(ROOT, "assets", "data", "free")


def page(n_params, n_total, n_ex, n_food):
    title = "Connections Explorer — How Food, Exercise & Your Body Interact | Nutrisize Health"
    desc = ("See how nutrition, exercise, and physiology connect — in every direction. "
            "Which foods and workouts move a given health parameter (with sources), which "
            "parameters an exercise changes and by how much, and what to eat before, during, "
            "and after training.")
    canonical = f"{SITE}/connections/"
    prefix = "../"

    extra = f"""    <link rel="stylesheet" href="{prefix}assets/css/explorer.css?v={asset_v('assets/css/explorer.css')}">
    <script src="{prefix}assets/js/connections.js?v={asset_v('assets/js/connections.js')}" defer></script>
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type": "ListItem", "position": 1, "name": "Home", "item": "{SITE}/"}},
        {{"@type": "ListItem", "position": 2, "name": "Connections Explorer", "item": "{canonical}"}}
      ]
    }}
    </script>
"""
    html = head(title, desc, canonical, prefix, extra) + nav(prefix) + breadcrumb(prefix, [("Connections", None)])
    html += f"""
<header class="hero hero-sub">
    <div class="wrap">
        <h1>Connections <span class="accent">Explorer</span></h1>
        <p class="tagline">How nutrition, exercise, and your body move together.</p>
        <p class="lede">
            Nothing in the body works alone. This is the Nutrisize Health knowledge graph,
            opened up for learning: pick a <strong>parameter</strong> to see the food and
            exercise that move it — with sources; pick an <strong>exercise</strong> to see the
            parameters it changes and how to fuel it; pick a <strong>food</strong> to see what
            it touches and when to eat it around training. Every link runs in both directions.
        </p>
    </div>
</header>

<section>
    <div class="wrap">
        <div class="cx-tabs" id="cx-tabs" role="tablist" aria-label="Explore by">
            <button class="cx-tab" role="tab" data-lens="parameter" aria-selected="true">By parameter</button>
            <button class="cx-tab" role="tab" data-lens="exercise" aria-selected="false">By exercise</button>
            <button class="cx-tab" role="tab" data-lens="food" aria-selected="false">By food</button>
        </div>
        <div class="cx-picker">
            <input type="search" id="cx-search" placeholder="Filter parameters&hellip;" aria-label="Filter">
            <select id="cx-select" aria-label="Choose an item"></select>
        </div>
        <p class="cx-hint" id="cx-hint">Pick a physiological parameter to see the nutrition and
        exercise that move it — with sources.</p>

        <div id="cx-result" aria-live="polite"></div>

{iap_plug(prefix, "connections-explorer",
          f"This is the free slice of the graph — {n_params} parameters, "
          f"linked to food and exercise.",
          f"The app carries the full web: all {n_total} physiological parameters across 16 body "
          "systems, every one cross-linked to the foods and exercises that move it, the "
          "interactions between parameters, and evidence for each — then tracks your own numbers "
          "and shows what’s changing. Physiology Premium unlocks the complete map.")}

        <div class="notice" style="margin-top:26px;">
            <strong>Educational reference only.</strong> These relationships summarize
            peer-reviewed and guideline sources (linked per parameter) and describe typical
            physiological responses — they are not medical advice, and individual responses vary
            with health, medication, and genetics. Consult a qualified professional before acting
            on them. See our <a href="../disclaimer/">full disclaimer</a>.
        </div>
    </div>
</section>
"""
    html += footer(prefix)
    return html


def main():
    with open(os.path.join(FREE, "parameters.json")) as f:
        pdata = json.load(f)
    params = pdata["parameters"]
    n_ex = sum(len(p["affectingExercises"]) for p in params)
    n_food = sum(len(p["affectingFoods"]) for p in params)
    out_dir = os.path.join(ROOT, "connections")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(page(len(params), pdata["totalParameters"], n_ex, n_food))
    print("wrote connections/index.html (%d free params)" % len(params))


if __name__ == "__main__":
    main()
