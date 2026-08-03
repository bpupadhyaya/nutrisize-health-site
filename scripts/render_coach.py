#!/usr/bin/env python3
"""Render /coach/ — "Meet your Coach": a marketing showcase of the app's
Coach subscription module (Today, Ask the Coach, Coaching, My Plan, Simulate,
Readiness, Insights, Goals & Check-ins, Weekly Review). Hosts the live KPI
demo (targets calibrated to cited WHO/CDC/JAMA/Mayo Clinic/Lancet/AHA
guidance — see REFERENCES) and links the what-if simulator.

Usage: python3 scripts/render_coach.py   (idempotent)
"""
import os

from render_plans import breadcrumb, ROOT, SITE, asset_v, esc, footer, head, iap_plug, nav

SUB_PRICE = "$4.99/month"

FEATURES = [
    ("&#128197;", "Today",
     "Your Coach dashboard: today's targets, what changed since yesterday, and an Explore hub "
     "into everything below."),
    ("&#128172;", "Ask the Coach",
     "Ask a question, get an answer grounded in your own numbers — a private, on-device Q&amp;A "
     "engine, not a generic chatbot."),
    ("&#127891;", "Coaching",
     "Three evidence-based coaches — Nutrition, Fitness, and Health — with 178 cited principles, "
     "plans, myths, and targets from WHO, ACSM, the Dietary Guidelines, and more."),
    ("&#128203;", "My Plan",
     "Your meal and exercise week rebuilds itself from what you actually logged, your goals, "
     "and your trend — and adjusts when progress stalls."),
    ("&#129514;", "Simulate",
     "What-if, weight-trajectory, and meal-timing simulators — see how a change plays out "
     "before you make it."),
    ("&#128267;", "Readiness",
     "A daily readiness read from your sleep, recovery, and vitals, so you know whether today "
     "is a push day or a rest day."),
    ("&#128279;", "Insights",
     "Cross-domain patterns across sleep, food, activity, and vitals — the correlations you "
     "would never spot by eye."),
    ("&#127919;", "Goals &amp; Check-ins",
     "Set the goals that matter to you and check in regularly to keep your plan honest and "
     "your Coach current."),
    ("&#128200;", "Weekly Review",
     "A weekly wrap-up of what moved, what did not, and what to focus on next."),
]

INSIGHTS = [
    ("Sleep &times; heart rate", "Your resting heart rate ran 4 bpm higher on weeks you slept "
     "under 6.5 hours — a signal your recovery was running short."),
    ("Steps &times; sleep", "On days you passed 8,000 steps, you fell asleep faster and slept "
     "about 40 minutes longer that night."),
    ("Late meals &times; morning glucose", "Dinners after 9pm tracked with higher fasting glucose "
     "the next morning — worth shifting earlier."),
]

# The cited sources behind each KPI-demo target — keep in sync with the
# denominators in assets/js/kpi-demo.js.
REFERENCES = [
    ("WHO", "Healthy diet — at least 400g (about 5 servings) of fruit and vegetables a day, the "
     "target behind the Veg &amp; fruit slider (Nutrition Quality, Nutrition Adequacy).",
     "https://www.who.int/news-room/fact-sheets/detail/healthy-diet"),
    ("WHO", "Guidelines on physical activity and sedentary behaviour (2020) — 150 min/week "
     "moderate aerobic activity (about 5 sessions) and muscle-strengthening on 2 or more days "
     "a week, the targets behind Cardio and Strength sessions.",
     "https://www.who.int/publications/i/item/9789240015128"),
    ("CDC / AASM", "About Sleep — adults should get 7 or more hours a night; a joint AASM/Sleep "
     "Research Society consensus panel sets the healthy range at 7-9 hours, the target behind "
     "the Sleep slider.",
     "https://www.cdc.gov/sleep/about/index.html"),
    ("JAMA, 2020", "Association of Daily Step Count and Step Intensity With Mortality Among US "
     "Adults — mortality risk kept falling out to 12,000 steps/day, with 8,000 already capturing "
     "most of the benefit over 4,000. 10,000/day is used as the full-credit target for the Steps "
     "input in Activity Volume, matching the app's own Activity Volume KPI.",
     "https://jamanetwork.com/journals/jama/fullarticle/2763292"),
    ("Mayo Clinic", "Water: How much should you drink every day? — eight 8-ounce glasses a day "
     "is the commonly used general benchmark (individual needs vary; NASEM's Dietary Reference "
     "Intakes put total daily fluid nearer 9-13 cups depending on sex), the target behind the "
     "Water slider.",
     "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/water/art-20044256"),
    ("The Lancet, 2016", "Does physical activity attenuate, or even eliminate, the detrimental "
     "association of sitting time with mortality? — sitting 8 or more hours a day was the "
     "highest-risk band in this pooled analysis of over 1 million adults, the basis for treating "
     "longer Sitting as lower-scoring in Recovery &amp; Sedentary Time.",
     "https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(16)30370-1/abstract"),
    ("American Heart Association", "All About Heart Rate (Pulse) — a normal adult resting heart "
     "rate is 60-100 bpm, and well-trained individuals are often lower (40-60 bpm), the basis "
     "for scoring Resting heart rate in Vitals &amp; Biofeedback.",
     "https://www.heart.org/en/health-topics/high-blood-pressure/the-facts-about-high-blood-pressure/all-about-heart-rate-pulse"),
]


def coach_ref_library(prefix):
    rows = "".join(
        f'<div class="rm-cite"><span>'
        f'<a href="{url}" target="_blank" rel="noopener">{text}</a>'
        f' <span class="rm-src">{esc(org)}</span></span></div>'
        for org, text, url in REFERENCES)
    plug = (f'<div class="app-plug" style="margin-top:24px">'
            f'<img src="{prefix}assets/img/favicon.png" alt="" width="34" height="34">'
            f"<p>This demo is a simplified illustration. In the app, each KPI is computed from "
            f"your own logged nutrition, activity, sleep, and vitals against these and other "
            f'cited targets, personalized to your profile. <a href="{prefix}#download">Get the '
            f'app &rarr;</a></p></div>')
    return ('<div id="ref-library"><p class="rm-legend">The guidelines behind each target in the '
            'KPI demo above. Links open in a new tab.</p>' + rows + plug + "</div>\n")


def page():
    title = "Meet your Coach — Adaptive Plans, Insights & Your 10 Health KPIs | Nutrisize Health"
    desc = ("Coach: adaptive weekly plans, an on-device Ask-the-Coach engine, evidence-based "
            "Nutrition/Fitness/Health coaching, and daily readiness scoring — built on your own "
            "data. $4.99/month, 100% offline. Try the live 10-KPI demo.")
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

    html = head(title, desc, canonical, prefix, extra) + nav(prefix) + breadcrumb(prefix, [("Coach", None)])
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
        <p class="lede" style="margin-top:8px"><strong>{SUB_PRICE}</strong>, cancel anytime — 100% offline, on-device, no cloud, no accounts.</p>
    </div>
</header>

<section class="tint">
    <div class="wrap">
        <div class="section-head">
            <span class="kicker">What the Coach does</span>
            <h2>Intelligence, built on your data</h2>
            <p>Nine ways the app works for you between check-ins — all private, all on your device.</p>
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
        <p style="margin-top:12px"><button class="ref-open" type="button" data-ref-open>&#128218; Sources &amp; references &middot; {len(REFERENCES)} cited</button></p>
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
        <div style="display:flex; flex-wrap:wrap; gap:12px; justify-content:center; margin-top:30px">
            <a class="btn outline" href="../simulator/">Try the what-if simulator &rarr;</a>
            <a class="btn outline" href="../digestion/">Digestion &amp; sleep tool &rarr;</a>
        </div>
    </div>
</section>

<section>
    <div class="wrap">
{iap_plug(prefix, "coach",
          "Ready when you are.",
          "Today, Ask the Coach, Coaching, My Plan, Simulate, Readiness, Insights, Goals &amp; "
          "Check-ins, and Weekly Review live in the Nutrisize Health app — learning from your "
          "data, working on your device. Download the app free, then unlock Coach for "
          f"<strong>{SUB_PRICE}</strong> (cancel anytime).")}
    </div>
</section>

{coach_ref_library(prefix)}
"""
    html += footer(prefix)
    return html


def main():
    out_dir = os.path.join(ROOT, "coach")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(page())
    print(f"wrote coach/index.html ({len(FEATURES)} feature cards, {len(REFERENCES)} references)")


if __name__ == "__main__":
    main()
