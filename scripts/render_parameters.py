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


GRADE_NOTE = ("Evidence grades follow the app's scale: A — meta-analyses and large randomized "
              "trials; B — cohort studies and clinical guidelines; C — expert consensus and "
              "standard references.")


def ref_library(data):
    """Hidden inline reference library (#ref-library) shown in the sources
    window: every tracked parameter's citations, grade-badged and linked."""
    freq_label = {"daily": "Daily", "weekly": "Weekly", "monthly": "Monthly",
                  "quarterly": "Quarterly", "annual": "Annual"}
    parts = [f'<p class="rm-legend">{GRADE_NOTE} Links open in a new tab.</p>']
    for t in data["tracked"]:
        if not t["citations"]:
            continue
        parts.append(f'<h4>{esc(t["name"])} <span class="rm-sys">{esc(t["system"])} &middot; '
                     f'{freq_label.get(t["freq"], t["freq"])}</span></h4>')
        for c in t["citations"]:
            grade = (c.get("grade") or "").lower()
            badge = (f'<span class="rm-grade {esc(grade)}">{esc(grade.upper())}</span>'
                     if grade else "")
            src = f' <span class="rm-src">{esc(c["source"])}</span>' if c.get("source") else ""
            parts.append(
                f'<div class="rm-cite">{badge}<span>'
                f'<a href="{esc(c["url"])}" target="_blank" rel="noopener">{esc(c["text"])}</a>'
                f'{src}</span></div>')
    parts.append(
        '<div class="app-plug" style="margin-top:24px">'
        '<img src="../assets/img/favicon.png" alt="" width="34" height="34">'
        f'<p>These are the citations behind the {len(data["tracked"])} tracked parameters. '
        f'In the app, every one of the {data["totalParameters"]} parameters carries its evidence '
        f'— {data["totalCitations"]} graded citations in all — readable right where you track. '
        '<a href="../#download">Get the app &rarr;</a></p></div>')
    return '<div id="ref-library">' + "".join(parts) + "</div>\n"


def page(data):
    tracked = data["tracked"]
    by_freq = {}
    for t in tracked:
        by_freq.setdefault(t["freq"], []).append(t)
    n_total, n_sys = data["totalParameters"], data["totalSystems"]
    n_cits = sum(len(t["citations"]) for t in tracked)

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
        <p style="margin-top:14px;">
            <button class="ref-open" type="button" data-ref-open>&#128218; Sources &amp; references
            <span style="font-weight:500; color:#8a9a91;">&middot; {n_cits} graded citations</span></button>
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
        <p style="text-align:center; margin-top:22px;">
            <button class="ref-open" type="button" data-ref-open>&#128218; See the sources &amp; references
            behind these ranges</button>
        </p>
{DISCLAIMER.replace("../../disclaimer/", "../disclaimer/")}    </div>
</section>
"""
    html += ref_library(data)
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
