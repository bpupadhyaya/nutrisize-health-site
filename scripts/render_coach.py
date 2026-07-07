#!/usr/bin/env python3
"""Render /coach/ — "Meet your Coach": a marketing showcase of the app's
intelligence layer (adaptive weekly plans, the 10 KPIs, cross-domain insights,
forecasts, a monthly doctor report, smart nudges). Hosts the live KPI demo and
links the what-if simulator. Markets existing app capabilities; the explicit
subscription price/CTA is intentionally held until the app ships it (see
SHOW_SUBSCRIPTION).

Usage: python3 scripts/render_coach.py   (idempotent)
"""
import os

from render_plans import ROOT, SITE, asset_v, footer, head, iap_plug, nav

# Flip to True and set the price once the $4.99/mo Coach subscription is live in
# the app stores. Until then the page markets the intelligence features without
# advertising a purchase visitors can't complete.
SHOW_SUBSCRIPTION = False
SUB_PRICE = "$4.99/mo"

FEATURES = [
    ("&#128197;", "Adaptive weekly plans",
     "Your meal and exercise week rebuilds itself from what you actually logged, your goals, "
     "and your trend — and adjusts when progress stalls."),
    ("&#128172;", "AI coach, on your data",
     "Ask anything and get answers grounded in your own numbers and a knowledge base of 4,995 "
     "foods, 5,404 exercises, and 201 parameters — private, on your device."),
    ("&#128279;", "Cross-domain insights",
     "It connects the dots across sleep, food, activity, and vitals — surfacing what is actually "
     "moving your numbers, week over week."),
    ("&#128200;", "Trend forecasts",
     "See where your weight and health KPIs are heading, and how a change today bends the curve "
     "months out."),
    ("&#129658;", "Monthly doctor report",
     "A clean, shareable summary of your trends and ranges — ready to bring to your next "
     "appointment."),
    ("&#128276;", "Smart, gentle nudges",
     "Context-aware reminders that adapt to your day and your goals — never generic, never noisy."),
]

INSIGHTS = [
    ("Sleep &times; heart rate", "Your resting heart rate ran 4 bpm higher on weeks you slept "
     "under 6.5 hours — a signal your recovery was running short."),
    ("Steps &times; sleep", "On days you passed 8,000 steps, you fell asleep faster and slept "
     "about 40 minutes longer that night."),
    ("Late meals &times; morning glucose", "Dinners after 9pm tracked with higher fasting glucose "
     "the next morning — worth shifting earlier."),
]


def page():
    title = "Meet your Coach — Adaptive Plans, Insights & Your 10 Health KPIs | Nutrisize Health"
    desc = ("The intelligence behind Nutrisize Health: adaptive weekly plans, an on-device AI "
            "coach, cross-domain insights, forecasts, and a monthly doctor report — built on your "
            "own data. Try the live 10-KPI demo.")
    canonical = f"{SITE}/coach/"
    prefix = "../"

    extra = f"""    <link rel="stylesheet" href="{prefix}assets/css/tools.css?v={asset_v('assets/css/tools.css')}">
    <script src="{prefix}assets/js/kpi-demo.js?v={asset_v('assets/js/kpi-demo.js')}" defer></script>
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type": "ListItem", "position": 1, "name": "Home", "item": "{SITE}/"}},
        {{"@type": "ListItem", "position": 2, "name": "Meet your Coach", "item": "{canonical}"}}
      ]
    }}
    </script>
"""
    feat_cards = "".join(
        f"""            <div class="card">
                <div class="icon{' blue' if i % 2 else ''}">{ic}</div>
                <h3>{t}</h3>
                <p>{d}</p>
            </div>
""" for i, (ic, t, d) in enumerate(FEATURES))

    insight_cards = "".join(
        f"""            <div class="card">
                <span class="kicker">{k}</span>
                <p style="margin-top:10px">{d}</p>
            </div>
""" for k, d in INSIGHTS)

    sub_line = ""
    if SHOW_SUBSCRIPTION:
        sub_line = (f'<p class="tagline" style="margin-top:8px">Included with Coach — '
                    f'<strong>{SUB_PRICE}</strong>, with a free trial.</p>')

    html = head(title, desc, canonical, prefix, extra) + nav(prefix)
    html += f"""
<header class="hero hero-sub">
    <div class="wrap">
        <h1>Meet your <span class="accent">Coach</span></h1>
        <p class="tagline">The databases are yours to keep. The Coach works for you every week.</p>
        <p class="lede">
            The Nutrisize Health libraries tell you <em>what</em> is true. The Coach is the layer
            that turns your own tracked data into <em>guidance</em> — adaptive plans, insights you
            would never spot by eye, and a clear read on where you are headed. It gets sharper the
            longer you use it.
        </p>
        {sub_line}
    </div>
</header>

<section class="tint">
    <div class="wrap">
        <div class="section-head">
            <span class="kicker">What the Coach does</span>
            <h2>Intelligence, built on your data</h2>
            <p>Six ways the app works for you between check-ins — all private, all on your device.</p>
        </div>
        <div class="grid">
{feat_cards}        </div>
    </div>
</section>

<section>
    <div class="wrap">
        <div class="section-head">
            <span class="kicker">Live demo</span>
            <h2>Your 10 health KPIs, scored in real time</h2>
            <p>The app scores ten dimensions of your health from what you log. Move the sliders to
            see how everyday habits shift the scores — the same ten the Coach watches for you.</p>
        </div>
        <div class="tool-grid">
            <div class="tool-panel" id="kpi-inputs"></div>
            <div>
                <div class="tool-out" style="margin-bottom:16px; display:flex; align-items:baseline; gap:16px;">
                    <div class="tool-stat"><div class="v" id="kpi-overall">–</div>
                        <div class="k">Overall wellness score</div></div>
                    <p class="tool-note" style="margin:0; flex:1; min-width:200px;">A weighted read across all
                    ten. In the app this is computed from your real logs and trends, not sliders.</p>
                </div>
                <div class="kpi-grid" id="kpi-cards"></div>
            </div>
        </div>
        <p class="tool-note" style="max-width:760px">Illustrative scoring for the demo. In the app,
        each KPI is computed from your logged nutrition, activity, sleep, and vitals — with a
        seven-day trend and specific, ranked recommendations.</p>
    </div>
</section>

<section class="tint">
    <div class="wrap">
        <div class="section-head">
            <span class="kicker">Insights you would miss by eye</span>
            <h2>It connects what happens across your week</h2>
            <p>Examples of the cross-domain patterns the Coach surfaces from your own history.</p>
        </div>
        <div class="grid">
{insight_cards}        </div>
        <p style="text-align:center; margin-top:30px">
            <a class="btn outline" href="../simulator/">Try the what-if simulator &rarr;</a>
        </p>
    </div>
</section>

<section>
    <div class="wrap">
{iap_plug(prefix, "coach",
          "Ready when you are.",
          "Adaptive plans, the AI coach, insights, forecasts, and your monthly doctor report live "
          "in the Nutrisize Health app — learning from your data, working on your device. Download "
          "free and start building your picture.")}
    </div>
</section>
"""
    html += footer(prefix)
    return html


def main():
    out_dir = os.path.join(ROOT, "coach")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(page())
    print("wrote coach/index.html (subscription CTA: %s)" % ("ON" if SHOW_SUBSCRIPTION else "held"))


if __name__ == "__main__":
    main()
