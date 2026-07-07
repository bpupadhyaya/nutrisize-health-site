#!/usr/bin/env python3
"""Render /exercises/ — the Exercise Explorer: a searchable, filterable browser
of the app's free-tier exercises (assets/data/free/exercises-index.json, from
scripts/export_free_tier.py), with a per-exercise detail popup (how-to, sets &
reps, common mistakes, physiology links) and a MET-based calorie-burn
calculator. The table is rendered client-side by assets/js/exercise-explorer.js;
this emits the page shell so it shares the site head/nav/footer.

Usage: python3 scripts/render_exercises.py   (idempotent)
"""
import json
import os

from render_plans import ROOT, SITE, asset_v, footer, head, iap_plug, nav

DATA = os.path.join(ROOT, "assets", "data", "free", "exercises-index.json")


def page(n_ex, n_cat):
    title = "Exercise Explorer — %d Exercises with How-To & Calorie Burn, Free | Nutrisize Health" % n_ex
    desc = ("Browse %d exercises across %d disciplines — strength, cardio, flexibility, balance, "
            "rehabilitation, and military — with how-to steps, sets and reps by level, common "
            "mistakes, the parameters each one changes, and a calorie-burn calculator for any "
            "bodyweight." % (n_ex, n_cat))
    canonical = f"{SITE}/exercises/"
    prefix = "../"

    extra = f"""    <link rel="stylesheet" href="{prefix}assets/css/explorer.css?v={asset_v('assets/css/explorer.css')}">
    <script src="{prefix}assets/js/exercise-explorer.js?v={asset_v('assets/js/exercise-explorer.js')}" defer></script>
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type": "ListItem", "position": 1, "name": "Home", "item": "{SITE}/"}},
        {{"@type": "ListItem", "position": 2, "name": "Exercise Explorer", "item": "{canonical}"}}
      ]
    }}
    </script>
"""
    html = head(title, desc, canonical, prefix, extra) + nav(prefix)
    html += f"""
<header class="hero hero-sub">
    <div class="wrap">
        <h1>Exercise <span class="accent">Explorer</span></h1>
        <p class="tagline">The app&rsquo;s exercise library — opened up for learning.</p>
        <p class="lede">
            {n_ex} exercises from the Nutrisize Health database, free to explore across strength,
            cardio, flexibility, balance, rehabilitation, and military training. Filter by muscle,
            equipment, and difficulty; open any exercise for how-to steps, sets and reps by level,
            common mistakes, the physiological parameters it changes &mdash; and a calorie-burn
            calculator that works for <em>your</em> bodyweight.
        </p>
    </div>
</header>

<section>
    <div class="wrap">
        <div class="fx-toolbar">
            <input type="search" id="ex-q" placeholder="Search exercises&hellip;" aria-label="Search exercises">
            <select id="ex-cat" aria-label="Filter by category"><option value="">All disciplines</option></select>
            <select id="ex-muscle" aria-label="Filter by muscle"><option value="">Any muscle</option></select>
            <select id="ex-equip" aria-label="Filter by equipment"><option value="">Any equipment</option></select>
            <select id="ex-diff" aria-label="Filter by difficulty">
                <option value="">Any level</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
            </select>
            <select id="ex-sort" aria-label="Sort">
                <option value="name">Sort: A&ndash;Z</option>
                <option value="met">Sort: MET (intensity)</option>
                <option value="burn">Sort: Calorie burn</option>
                <option value="difficulty">Sort: Difficulty</option>
            </select>
            <button class="fx-reset" id="ex-reset" type="button">Reset</button>
        </div>
        <p class="fx-count" id="ex-count">Loading {n_ex} exercises&hellip;</p>
        <div class="table-scroll">
        <table class="param-table fx-table">
            <thead><tr>
                <th>Exercise</th><th>Discipline</th><th>Primary muscle</th>
                <th>Equipment</th><th>Level</th><th class="fx-num">MET</th>
            </tr></thead>
            <tbody id="ex-tbody"></tbody>
        </table>
        </div>
{iap_plug(prefix, "exercises-explorer",
          f"{n_ex} exercises free here — the app carries all 5,404.",
          "Exercise Premium unlocks the full library in the app: every exercise with video "
          "demonstrations, progression pathways, muscle-activation detail, sport and occupation "
          "context, and links to the physiology it trains — plus your own logging and weekly "
          "plans, offline and private.")}
        <div class="notice" style="margin-top:26px;">
            <strong>Educational reference only.</strong> Calorie burn is estimated from each
            exercise&rsquo;s MET value and varies with intensity, fitness, and body composition.
            Nothing here is medical or fitness advice — consult a qualified professional before
            starting new exercise. See our <a href="../disclaimer/">full disclaimer</a>.
        </div>
    </div>
</section>
"""
    html += footer(prefix)
    return html


def main():
    with open(DATA) as f:
        ex = json.load(f)["exercises"]
    cats = {e["category"] for e in ex}
    out_dir = os.path.join(ROOT, "exercises")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(page(len(ex), len(cats)))
    print("wrote exercises/index.html (%d exercises, %d disciplines)" % (len(ex), len(cats)))


if __name__ == "__main__":
    main()
