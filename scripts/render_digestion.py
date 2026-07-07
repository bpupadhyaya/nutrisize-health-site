#!/usr/bin/env python3
"""Render /digestion/ — Digestion & sleep-impact tool. Exports the app's
digestion dataset to assets/data/free/digestion.json (foods with digestion +
absorption times, combination effects), then emits a page with an interactive
"will this meal keep me up?" calculator plus reference tables for digestion time
by food group and for food-combination effects.

Usage: python3 scripts/render_digestion.py [--app-repo <path>]
"""
import argparse
import json
import os
import re

from render_plans import ROOT, SITE, asset_v, esc, footer, head, iap_plug, nav

DEFAULT_APP_REPO = os.path.normpath(os.path.join(ROOT, "..", "..", "pvt", "nutrisize-health-claude"))
OUT_DATA = os.path.join(ROOT, "assets", "data", "free", "digestion.json")


def titleize(slug):
    return re.sub(r"([a-z])([A-Z])", r"\1 \2", slug).replace("-", " ").strip().title()


def camel_words(s):
    return re.sub(r"([a-z])([A-Z])", r"\1 \2", str(s)).title()


def export(app_repo):
    src = os.path.join(app_repo, "ios", "NutrisizeHealth", "Resources", "digestion_data.json")
    d = json.load(open(src))
    foods = []
    for cat, val in d["categoryDefaults"].items():
        foods.append({"name": titleize(cat), "cat": cat, "digest": val.get("digestionHours"),
                      "absorb": val.get("absorptionHours"), "note": val.get("note")})
    for key, val in d["specificFoods"].items():
        foods.append({"name": titleize(key), "cat": key.split("-")[0], "digest": val.get("digestionHours"),
                      "absorb": val.get("absorptionHours"), "note": val.get("note")})
    foods.sort(key=lambda f: f["name"])
    combos = [{"name": re.sub(r"([a-z])([A-Z])", r"\1 \2", k).title(),
               "hours": v.get("additionalHours"), "note": v.get("note")}
              for k, v in d["combinationEffects"].items()]
    out = {"foods": foods, "combinationEffects": combos,
           "categoryDefaults": d["categoryDefaults"], "sources": d.get("sources", [])}
    os.makedirs(os.path.dirname(OUT_DATA), exist_ok=True)
    json.dump(out, open(OUT_DATA, "w"), ensure_ascii=False, separators=(",", ":"))
    return d, len(foods)


def page(d):
    title = "Digestion Time & Sleep-Impact Calculator — Will Your Dinner Keep You Up? | Nutrisize Health"
    desc = ("See how long foods take to digest and whether your evening meal is still working at "
            "bedtime. Plus digestion times by food group and how food combinations slow things "
            "down. Free and instant.")
    canonical = f"{SITE}/digestion/"
    prefix = "../"

    extra = f"""    <link rel="stylesheet" href="{prefix}assets/css/tools.css?v={asset_v('assets/css/tools.css')}">
    <link rel="stylesheet" href="{prefix}assets/css/explorer.css?v={asset_v('assets/css/explorer.css')}">
    <script src="{prefix}assets/js/digestion.js?v={asset_v('assets/js/digestion.js')}" defer></script>
    <script type="application/ld+json">
    {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {{"@type":"ListItem","position":1,"name":"Home","item":"{SITE}/"}},
      {{"@type":"ListItem","position":2,"name":"Digestion & Sleep","item":"{canonical}"}}]}}
    </script>
"""
    # Reference: digestion by food group
    cat_rows = "".join(
        f'<tr><td class="pname">{esc(titleize(cat))}</td>'
        f'<td class="change">{v.get("digestionHours")}&ndash;{round((v.get("digestionHours",0)+v.get("absorptionHours",0)),1)} h</td>'
        f'<td>{esc(v.get("note",""))}</td></tr>'
        for cat, v in sorted(d["categoryDefaults"].items(),
                             key=lambda kv: kv[1].get("digestionHours", 0)))

    combo_rows = "".join(
        f'<tr><td class="pname">{esc(camel_words(k))}</td>'
        f'<td class="change">+{v.get("additionalHours")} h</td><td>{esc(v.get("note",""))}</td></tr>'
        for k, v in d["combinationEffects"].items())

    src_line = ", ".join(esc(s) for s in d.get("sources", [])[:4])

    html = head(title, desc, canonical, prefix, extra) + nav(prefix)
    html += f"""
<header class="hero hero-sub">
    <div class="wrap">
        <h1>Digestion &amp; <span class="accent">Sleep</span></h1>
        <p class="tagline">Will tonight's dinner still be digesting when you go to bed?</p>
        <p class="lede">
            Eating too close to bedtime, or too heavy, can leave your body still digesting when
            you're trying to sleep. Build your evening meal below, set your dinner and bedtime, and
            see where you land &mdash; then browse how long different foods and combinations take.
        </p>
    </div>
</header>

<section>
    <div class="wrap">
        <div class="tool-grid">
            <div class="tool-panel">
                <h3>&#127869;&#65039; Tonight's meal</h3>
                <div class="tool-field">
                    <label for="dg-search">Add a food</label>
                    <input id="dg-search" list="dg-foods" placeholder="Type a food&hellip;" autocomplete="off">
                    <datalist id="dg-foods"></datalist>
                </div>
                <p style="margin:0 0 14px"><button class="btn outline" id="dg-add" type="button" style="padding:8px 16px">Add to meal</button></p>
                <div class="tool-row2">
                    <div class="tool-field"><label for="dg-dinner">Dinner time</label>
                        <input id="dg-dinner" type="time" value="18:30"></div>
                    <div class="tool-field"><label for="dg-bed">Bedtime</label>
                        <input id="dg-bed" type="time" value="22:30"></div>
                </div>
                <p class="tool-note">Times digesting are estimates from food type — actual digestion
                varies with portion, health, and metabolism.</p>
            </div>
            <div class="tool-out" id="dg-result"></div>
        </div>

{iap_plug(prefix, "digestion",
          "Time your meals to your sleep, every day.",
          "The Nutrisize Health app knows the digestion profile of thousands of foods and can nudge "
          "you when a late, heavy meal might cost you sleep — tuned to what you actually eat and "
          "when. Private, on your device.")}
    </div>
</section>

<section class="tint">
    <div class="wrap">
        <div class="section-head">
            <span class="kicker">Reference</span>
            <h2>How long food takes to digest, by group</h2>
            <p>Total time to clear the stomach and absorb, fastest first.</p>
        </div>
        <div class="table-scroll"><table class="param-table"><thead><tr>
            <th>Food group</th><th>Time to digest</th><th>Why</th></tr></thead>
            <tbody>{cat_rows}</tbody></table></div>
    </div>
</section>

<section>
    <div class="wrap">
        <div class="section-head">
            <span class="kicker">Reference</span>
            <h2>What slows digestion down</h2>
            <p>Combinations on your plate change how long the whole meal takes.</p>
        </div>
        <div class="table-scroll" style="max-width:820px; margin:0 auto"><table class="param-table"><thead><tr>
            <th>Combination</th><th>Adds</th><th>Effect</th></tr></thead>
            <tbody>{combo_rows}</tbody></table></div>
        <p class="tool-note" style="text-align:center; margin-top:16px">Sources: {src_line}.
        Educational reference only &mdash; not medical advice.</p>
    </div>
</section>
"""
    html += footer(prefix)
    return html


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--app-repo", default=DEFAULT_APP_REPO)
    args = ap.parse_args()
    d, n = export(args.app_repo)
    out_dir = os.path.join(ROOT, "digestion")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(page(d))
    print("wrote digestion/index.html + digestion.json (%d foods)" % n)


if __name__ == "__main__":
    main()
