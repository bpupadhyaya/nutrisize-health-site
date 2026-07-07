#!/usr/bin/env python3
"""Render /simulator/ — the What-if weight & energy simulator: pick a daily
calorie change and see a realistic (metabolism-adapting) weight projection over
24 weeks. The whole tool is client-side (assets/js/simulator.js); this emits the
page shell so it shares the site head/nav/footer.

Usage: python3 scripts/render_simulator.py   (idempotent)
"""
import os

from render_plans import ROOT, SITE, asset_v, footer, head, iap_plug, nav


def page():
    title = "What-If Weight Simulator — See Your Energy-Balance Projection | Nutrisize Health"
    desc = ("Set a daily calorie change and see a realistic weight projection over 24 weeks — "
            "one that flattens the way real weight loss plateaus as your metabolism adapts. "
            "Free, private, and instant.")
    canonical = f"{SITE}/simulator/"
    prefix = "../"

    extra = f"""    <link rel="stylesheet" href="{prefix}assets/css/tools.css?v={asset_v('assets/css/tools.css')}">
    <script src="{prefix}assets/js/simulator.js?v={asset_v('assets/js/simulator.js')}" defer></script>
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type": "ListItem", "position": 1, "name": "Home", "item": "{SITE}/"}},
        {{"@type": "ListItem", "position": 2, "name": "What-If Simulator", "item": "{canonical}"}}
      ]
    }}
    </script>
"""
    html = head(title, desc, canonical, prefix, extra) + nav(prefix)
    html += f"""
<header class="hero hero-sub">
    <div class="wrap">
        <h1>What-If <span class="accent">Simulator</span></h1>
        <p class="tagline">See where a daily calorie change actually takes you.</p>
        <p class="lede">
            Move one slider and watch a 24-week projection of your weight — a
            <em>realistic</em> one that bends as your metabolism adapts, not the straight line
            most calculators draw. It shows why steady progress plateaus, and what a change
            really adds up to.
        </p>
    </div>
</header>

<section>
    <div class="wrap">
        <div class="tool-grid">
            <div class="tool-panel">
                <h3>&#128202; Your numbers</h3>
                <div class="tool-field">
                    <label for="sim-sex">Sex</label>
                    <select id="sim-sex"><option value="m">Male</option><option value="f">Female</option></select>
                </div>
                <div class="tool-row2">
                    <div class="tool-field"><label for="sim-age">Age</label>
                        <input id="sim-age" type="number" min="15" max="100" value="35"></div>
                    <div class="tool-field"><label for="sim-units">Units</label>
                        <select id="sim-units"><option value="metric">cm, kg</option><option value="imperial">in, lb</option></select></div>
                </div>
                <div class="tool-row2">
                    <div class="tool-field"><label for="sim-height">Height</label>
                        <input id="sim-height" type="number" min="120" max="230" value="172"></div>
                    <div class="tool-field"><label for="sim-weight">Weight</label>
                        <input id="sim-weight" type="number" min="30" max="300" value="82"></div>
                </div>
                <div class="tool-field">
                    <label for="sim-activity">Activity level</label>
                    <select id="sim-activity">
                        <option value="1.2">Sedentary</option>
                        <option value="1.375">Lightly active</option>
                        <option value="1.55" selected>Moderately active</option>
                        <option value="1.725">Very active</option>
                    </select>
                </div>
                <div class="tool-field tool-slider">
                    <div class="tool-slabel"><label for="sim-delta" style="margin:0">Daily calories vs. maintenance</label>
                        <span class="tool-sval" id="sim-delta-val">-400</span></div>
                    <input id="sim-delta" type="range" min="-1000" max="500" step="50" value="-400">
                </div>
                <p class="tool-note" style="margin-top:4px">Negative = eating below maintenance
                (lose), positive = above (gain).</p>
            </div>

            <div class="tool-out" id="sim-out"></div>
        </div>

{iap_plug(prefix, "simulator",
          "This is a projection. The app tracks what actually happens.",
          "The Nutrisize Health app logs what you really eat and do, recomputes your targets as "
          "your body changes, and shows your true trend over time — with adaptive weekly plans "
          "that adjust when progress stalls. A projection points the way; the app keeps you on it.")}
    </div>
</section>
"""
    html += footer(prefix)
    return html


def main():
    out_dir = os.path.join(ROOT, "simulator")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(page())
    print("wrote simulator/index.html")


if __name__ == "__main__":
    main()
