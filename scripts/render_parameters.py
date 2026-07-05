#!/usr/bin/env python3
"""Render /parameters/ — sample of the app's System → Human → Tracking view:
essential physiological parameters grouped by check-in cadence, with normal
ranges. Data: scripts/physiology_tracking.json (trimmed export of the app's
physiology_data.json).

Usage: python3 scripts/render_parameters.py   (idempotent)
"""
import json
import os

from render_plans import ROOT, SITE, app_plug, esc, footer, head, nav, DISCLAIMER

DATA = os.path.join(ROOT, "scripts", "physiology_tracking.json")

CADENCES = [
    ("daily", "Daily", "Quick self-checks — no lab needed, most take under a minute."),
    ("weekly", "Weekly", "A slower-moving picture: trends that only show over several days."),
    ("monthly", "Monthly", "Worth a calendar reminder — patterns, symptoms, and home trends."),
    ("quarterly", "Quarterly", "Seasonal check-ins, often alongside a routine visit."),
]


def cadence_table(rows):
    body = "".join(f"""            <tr>
                <td class="pname">{esc(r["name"])}</td>
                <td>{esc(r["system"])}</td>
                <td class="change">{esc(r["range"])}</td>
                <td>{esc(r["desc"])}</td>
            </tr>
""" for r in rows)
    return f"""        <div class="table-scroll">
        <table class="param-table">
            <thead><tr><th>Parameter</th><th>Body system</th><th>Typical healthy range</th><th>What it tells you</th></tr></thead>
            <tbody>
{body}            </tbody>
        </table>
        </div>
"""


def page(data):
    tracked = data["tracked"]
    by_freq = {}
    for t in tracked:
        by_freq.setdefault(t["freq"], []).append(t)
    n_total, n_sys = data["totalParameters"], data["totalSystems"]

    title = "Physiological Parameters — What to Track and Healthy Ranges | Nutrisize Health"
    desc = (f"The {len(tracked)} essential physiological parameters worth monitoring — daily "
            f"vitals to annual labs — with typical healthy ranges, from the Nutrisize Health "
            f"app's library of {n_total} parameters across {n_sys} body systems.")
    canonical = f"{SITE}/parameters/"
    prefix = "../"

    jsonld = f"""    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type": "ListItem", "position": 1, "name": "Home", "item": "{SITE}/"}},
        {{"@type": "ListItem", "position": 2, "name": "Physiological Parameters", "item": "{canonical}"}}
      ]
    }}
    </script>
"""
    html = head(title, desc, canonical, prefix, jsonld) + nav(prefix)
    html += f"""
<header class="hero hero-sub">
    <div class="wrap">
        <h1>Physiological <span class="accent">Parameters</span></h1>
        <p class="tagline">Know your numbers — and how often to check them.</p>
        <p class="lede">
            In the app, <strong>System &rarr; Human &rarr; Tracking</strong> watches the
            {len(tracked)} parameters that matter most, on a cadence from daily vitals to annual
            labs. This page is that view, opened up for learning: each parameter with its body
            system, typical healthy range, and what it tells you.
        </p>
    </div>
</header>
"""
    for key, label, sub in CADENCES:
        rows = by_freq.get(key, [])
        if not rows:
            continue
        tint = ' class="tint"' if label in ("Daily", "Monthly") else ""
        html += f"""
<section{tint}>
    <div class="wrap">
        <div class="section-head">
            <span class="kicker">{label} &middot; {len(rows)} parameters</span>
            <h2>Check {label.lower()}</h2>
            <p>{sub}</p>
        </div>
{cadence_table(rows)}    </div>
</section>
"""

    annual = by_freq.get("annual", [])
    chips = "".join(f'<span class="chip">{esc(t["name"])}</span>' for t in annual)
    html += f"""
<section class="tint">
    <div class="wrap">
        <div class="section-head">
            <span class="kicker">Annual &middot; {len(annual)} parameters</span>
            <h2>Once a year, with your bloodwork</h2>
            <p>Most of these come from a routine annual panel — lipids, liver and kidney
            function, thyroid, vitamins, and blood counts. In the app, each one has its range,
            interpretation, and links to the conditions it flags.</p>
        </div>
        <div class="chips">{chips}</div>
{app_plug(prefix, f"These {len(tracked)} are the essentials. The app carries all {n_total} "
                  f"parameters across {n_sys} body systems — each with normal ranges, "
                  "interpretation of high and low values, and disease links — and tracks "
                  "yours over time, on your device.")}
{DISCLAIMER.replace("../../disclaimer/", "../disclaimer/")}    </div>
</section>
"""
    html += footer(prefix)
    return html


def main():
    with open(DATA) as f:
        data = json.load(f)
    out_dir = os.path.join(ROOT, "parameters")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(page(data))
    print("wrote parameters/index.html (%d tracked params)" % len(data["tracked"]))


if __name__ == "__main__":
    main()
