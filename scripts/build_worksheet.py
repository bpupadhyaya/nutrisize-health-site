#!/usr/bin/env python3
"""Build the interactive weekly worksheet from one shared core:
  - plans/worksheet/index.html            (site page: nav + footer + site CSS)
  - assets/downloads/nutrisize-weekly-worksheet.html  (standalone, fully offline)

Usage: python3 scripts/build_worksheet.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://nutrisize.health"

CORE = """
<div class="ws-grid">
    <div class="ws-panel">
        <h3>&#128202; Your numbers</h3>
        <div class="ws-field">
            <label for="sex">Sex</label>
            <select id="sex"><option value="m">Male</option><option value="f">Female</option></select>
        </div>
        <div class="ws-row2">
            <div class="ws-field">
                <label for="age">Age (years)</label>
                <input id="age" type="number" min="15" max="100" placeholder="e.g. 30">
            </div>
            <div class="ws-field">
                <label for="units">Units</label>
                <select id="units"><option value="metric">Metric (cm, kg)</option><option value="imperial">Imperial (in, lb)</option></select>
            </div>
        </div>
        <div class="ws-row2">
            <div class="ws-field">
                <label for="height" id="heightLabel">Height (cm)</label>
                <input id="height" type="number" min="90" max="250" step="0.5" placeholder="e.g. 170">
            </div>
            <div class="ws-field">
                <label for="weight" id="weightLabel">Weight (kg)</label>
                <input id="weight" type="number" min="25" max="300" step="0.1" placeholder="e.g. 68">
            </div>
        </div>
        <div class="ws-field">
            <label for="activity">Activity level</label>
            <select id="activity">
                <option value="1.2">Sedentary — mostly sitting</option>
                <option value="1.375">Lightly active — 1&ndash;3 workouts/week</option>
                <option value="1.55" selected>Moderately active — 3&ndash;5 workouts/week</option>
                <option value="1.725">Very active — 6&ndash;7 workouts/week</option>
            </select>
        </div>
        <div class="ws-field">
            <label for="goal">Goal</label>
            <select id="goal">
                <option value="0" selected>Maintain weight</option>
                <option value="-400">Lose gradually (&minus;400 kcal/day)</option>
                <option value="300">Gain gradually (+300 kcal/day)</option>
            </select>
        </div>
        <div class="ws-results">
            <div class="ws-out"><div class="v" id="oBmi">&ndash;</div><div class="k" id="oBmiK">BMI</div></div>
            <div class="ws-out"><div class="v" id="oBmr">&ndash;</div><div class="k">BMR kcal/day</div></div>
            <div class="ws-out"><div class="v" id="oTdee">&ndash;</div><div class="k">TDEE kcal/day</div></div>
            <div class="ws-out"><div class="v" id="oTarget">&ndash;</div><div class="k">Daily target kcal</div></div>
            <div class="ws-out blue"><div class="v" id="oProtein">&ndash;</div><div class="k">Protein g/day</div></div>
            <div class="ws-out blue"><div class="v" id="oCarbs">&ndash;</div><div class="k">Carbs g/day</div></div>
            <div class="ws-out blue"><div class="v" id="oFat">&ndash;</div><div class="k">Fat g/day</div></div>
            <div class="ws-out blue"><div class="v" id="oFiber">&ndash;</div><div class="k">Fiber g/day</div></div>
            <div class="ws-out"><div class="v" id="oWater">&ndash;</div><div class="k">Water L/day</div></div>
        </div>
        <p class="ws-note">BMR uses the Mifflin&ndash;St&nbsp;Jeor equation (ages 15+). Protein is
        sized per kg of body weight, fat at 30% of calories, carbs fill the rest, fiber at
        14&nbsp;g per 1,000&nbsp;kcal. Educational estimates — not medical advice.</p>
    </div>

    <div class="ws-panel">
        <h3>&#128197; Plan your week</h3>
        <p class="ws-note" style="margin:0 0 12px">Enter the calories you plan for each meal —
        totals, color coding, and the weekly summary update as you type. Your entries stay in
        this browser only.</p>
        <div class="table-scroll" style="box-shadow:none">
        <table class="ws-week" id="wsWeek">
            <thead><tr>
                <th>Day</th><th>Breakfast</th><th>Lunch</th><th>Snack</th><th>Dinner</th>
                <th>Total</th><th>Exercise min</th><th>Intensity</th><th>Burn</th>
            </tr></thead>
            <tbody></tbody>
        </table>
        </div>
        <div class="ws-summary">
            <div class="ws-out"><div class="v" id="sAvg">&ndash;</div><div class="k">Avg intake kcal/day</div></div>
            <div class="ws-out"><div class="v" id="sVsTarget">&ndash;</div><div class="k">vs. your target</div></div>
            <div class="ws-out blue"><div class="v" id="sExMin">&ndash;</div><div class="k">Exercise min/week</div></div>
            <div class="ws-out blue"><div class="v" id="sBurn">&ndash;</div><div class="k">Est. burn kcal/week</div></div>
        </div>
        <div class="plan-cta no-print" style="justify-content:flex-start; margin-top:18px">
            <button class="btn" onclick="window.print()" type="button">&#128424;&#65039; Print / save as PDF</button>
            <button class="btn outline" onclick="wsReset()" type="button">Reset week</button>
        </div>
        <p class="ws-note">Aim for your daily total to land near your target (green = within 5%,
        amber = within 12%). Exercise burn is a rough estimate from duration, intensity, and your
        weight (METs method).</p>
    </div>
</div>
"""

JS = """
<script>
(function () {
    var DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];
    var MEALS = ["b","l","s","d"];
    var METS = { light: 3.0, moderate: 5.0, vigorous: 8.0 };
    var $ = function (id) { return document.getElementById(id); };
    var state = {};
    try { state = JSON.parse(localStorage.getItem("nutrisizeWorksheet") || "{}"); } catch (e) { state = {}; }

    // build week rows
    var tbody = $("wsWeek").tBodies[0];
    DAYS.forEach(function (day, i) {
        var tr = document.createElement("tr");
        var cells = '<td class="day">' + day + "</td>";
        MEALS.forEach(function (m) {
            cells += '<td><input type="number" min="0" max="4000" data-k="' + m + i + '" placeholder="kcal"></td>';
        });
        cells += '<td class="total" data-t="' + i + '">&ndash;</td>';
        cells += '<td><input type="number" min="0" max="600" data-k="x' + i + '" placeholder="min"></td>';
        cells += '<td><select data-k="v' + i + '">' +
                 '<option value="light">Light</option>' +
                 '<option value="moderate" selected>Moderate</option>' +
                 '<option value="vigorous">Vigorous</option></select></td>';
        cells += '<td class="total" data-b="' + i + '">&ndash;</td>';
        tr.innerHTML = cells;
        tbody.appendChild(tr);
    });

    var FIELDS = ["sex", "age", "units", "height", "weight", "activity", "goal"];

    function restore() {
        FIELDS.forEach(function (id) { if (state[id] !== undefined) $(id).value = state[id]; });
        document.querySelectorAll("[data-k]").forEach(function (el) {
            var v = state["w_" + el.getAttribute("data-k")];
            if (v !== undefined) el.value = v;
        });
    }

    function save() {
        FIELDS.forEach(function (id) { state[id] = $(id).value; });
        document.querySelectorAll("[data-k]").forEach(function (el) {
            state["w_" + el.getAttribute("data-k")] = el.value;
        });
        try { localStorage.setItem("nutrisizeWorksheet", JSON.stringify(state)); } catch (e) {}
    }

    function num(id) { var v = parseFloat($(id).value); return isFinite(v) ? v : NaN; }
    function fmt(n) { return isFinite(n) ? Math.round(n).toLocaleString() : "\\u2013"; }

    var target = NaN, weightKg = NaN;

    function calcProfile() {
        var imperial = $("units").value === "imperial";
        $("heightLabel").textContent = imperial ? "Height (in)" : "Height (cm)";
        $("weightLabel").textContent = imperial ? "Weight (lb)" : "Weight (kg)";
        var h = num("height"), w = num("weight"), age = num("age");
        if (imperial) { h = h * 2.54; w = w * 0.45359237; }
        weightKg = w;
        var bmi = (h > 0 && w > 0) ? w / Math.pow(h / 100, 2) : NaN;
        var bmr = NaN;
        if (h > 0 && w > 0 && age > 0) {
            bmr = 10 * w + 6.25 * h - 5 * age + ($("sex").value === "m" ? 5 : -161);
        }
        var tdee = bmr * parseFloat($("activity").value);
        target = tdee + parseFloat($("goal").value);
        var gPerKg = parseFloat($("goal").value) === 0 ? 1.2 : 1.6;
        var protein = w > 0 ? Math.max(0.8 * w, gPerKg * w) : NaN;
        var fatG = target * 0.30 / 9;
        var carbsG = (target - protein * 4 - fatG * 9) / 4;
        $("oBmi").textContent = isFinite(bmi) ? bmi.toFixed(1) : "\\u2013";
        var cat = !isFinite(bmi) ? "BMI" : bmi < 18.5 ? "BMI \\u00b7 underweight" :
                  bmi < 25 ? "BMI \\u00b7 healthy range" : bmi < 30 ? "BMI \\u00b7 overweight" : "BMI \\u00b7 obese";
        $("oBmiK").textContent = cat;
        $("oBmr").textContent = fmt(bmr);
        $("oTdee").textContent = fmt(tdee);
        $("oTarget").textContent = fmt(target);
        $("oProtein").textContent = fmt(protein);
        $("oCarbs").textContent = fmt(carbsG);
        $("oFat").textContent = fmt(fatG);
        $("oFiber").textContent = fmt(target * 14 / 1000);
        $("oWater").textContent = w > 0 ? (w * 0.035).toFixed(1) : "\\u2013";
    }

    function calcWeek() {
        var days = 0, sum = 0, exMin = 0, burn = 0;
        DAYS.forEach(function (_, i) {
            var t = 0, any = false;
            MEALS.forEach(function (m) {
                var el = document.querySelector('[data-k="' + m + i + '"]');
                var v = parseFloat(el.value);
                if (isFinite(v)) { t += v; any = true; }
            });
            var cell = document.querySelector('[data-t="' + i + '"]');
            cell.className = "total";
            if (any) {
                cell.textContent = t.toLocaleString();
                days++; sum += t;
                if (isFinite(target) && target > 0) {
                    var dev = Math.abs(t - target) / target;
                    cell.classList.add(dev <= 0.05 ? "ok" : dev <= 0.12 ? "near" : "off");
                }
            } else { cell.innerHTML = "&ndash;"; }
            var mins = parseFloat(document.querySelector('[data-k="x' + i + '"]').value);
            var met = METS[document.querySelector('[data-k="v' + i + '"]').value];
            var bcell = document.querySelector('[data-b="' + i + '"]');
            if (isFinite(mins) && mins > 0 && isFinite(weightKg) && weightKg > 0) {
                var b = met * weightKg * mins / 60;
                exMin += mins; burn += b;
                bcell.textContent = "\\u2212" + Math.round(b).toLocaleString();
            } else { bcell.innerHTML = "&ndash;"; }
        });
        $("sAvg").textContent = days ? Math.round(sum / days).toLocaleString() : "\\u2013";
        $("sVsTarget").textContent = (days && isFinite(target) && target > 0)
            ? (sum / days / target * 100).toFixed(0) + "%" : "\\u2013";
        $("sExMin").textContent = exMin ? Math.round(exMin).toLocaleString() : "\\u2013";
        $("sBurn").textContent = burn ? Math.round(burn).toLocaleString() : "\\u2013";
    }

    function recalc() { calcProfile(); calcWeek(); save(); }

    window.wsReset = function () {
        document.querySelectorAll("#wsWeek input").forEach(function (el) { el.value = ""; });
        document.querySelectorAll("#wsWeek select").forEach(function (el) { el.value = "moderate"; });
        recalc();
    };

    document.addEventListener("input", recalc);
    document.addEventListener("change", recalc);
    restore();
    recalc();
})();
</script>
"""

STANDALONE_CSS = """
:root { --green-900:#0b3d2e; --green-800:#0f5b40; --green-700:#14684c; --green-600:#178a5e;
  --green-500:#1fa971; --green-100:#e3f5ec; --blue-700:#0b4f8a; --blue-600:#1268b3;
  --blue-100:#e5f0fa; --amber-500:#d97706; --red-500:#dc2626; --ink:#12211b; --ink-soft:#40544a;
  --ink-faint:#6b7f74; --paper:#fff; --paper-tint:#f4faf7; --line:#dcebe3; --radius:14px;
  --shadow:0 4px 24px rgba(11,61,46,0.08); }
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif;
  color:var(--ink); background:var(--paper-tint); line-height:1.65; padding:32px 20px; }
.wshead { max-width:1160px; margin:0 auto 26px; }
.wshead h1 { color:var(--green-900); font-size:28px; letter-spacing:-0.02em; }
.wshead p { color:var(--ink-soft); font-size:14.5px; margin-top:6px; }
.wshead a { color:var(--blue-600); }
.wsmain { max-width:1160px; margin:0 auto; }
.table-scroll { overflow-x:auto; }
.btn { display:inline-block; background:var(--green-600); color:#fff; border:none; cursor:pointer;
  border-radius:10px; padding:12px 24px; font-weight:700; font:inherit; font-weight:700; }
.btn.outline { background:transparent; border:2px solid var(--green-600); color:var(--green-700); }
.plan-cta { display:flex; gap:12px; flex-wrap:wrap; }
"""


def read(path):
    with open(os.path.join(ROOT, path)) as f:
        return f.read()


def site_page():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Weekly Worksheet — Nutrisize Health</title>
    <meta name="description" content="Free auto-calculating nutrition and exercise worksheet: your BMI, BMR, TDEE, calorie target and macros — then plan your week and watch it total itself.">
    <link rel="canonical" href="{SITE}/plans/worksheet/">
    <meta property="og:title" content="Interactive Weekly Worksheet — Nutrisize Health">
    <meta property="og:description" content="Auto-calculating nutrition and exercise worksheet: BMI, BMR, TDEE, targets, and a self-totaling week planner.">
    <meta property="og:url" content="{SITE}/plans/worksheet/">
    <meta property="og:image" content="{SITE}/assets/img/og-image.png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Nutrisize Health">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:image" content="{SITE}/assets/img/og-image.png">
    <link rel="icon" type="image/png" href="../../assets/img/favicon.png">
    <link rel="apple-touch-icon" href="../../assets/img/apple-touch-icon.png">
    <link rel="manifest" href="/site.webmanifest">
    <meta name="theme-color" content="#0b3d2e">
    <link rel="stylesheet" href="../../assets/fonts/inter.css">
    <link rel="stylesheet" href="../../assets/css/style.css">
    <link rel="stylesheet" href="../../assets/css/plans.css">
</head>
<body>

<nav>
    <div class="nav-inner">
        <a href="../../" class="nav-logo">
            <img src="../../assets/img/favicon.png" alt="" width="34" height="34">
            Nutrisize Health
        </a>
        <ul class="nav-links">
            <li><a href="../">Plans</a></li>
            <li><a href="../../foods/">Foods</a></li>
            <li><a href="../../nutrients/">Nutrients</a></li>
            <li><a href="../../exercises/">Exercises</a></li>
            <li><a href="../../parameters/">Parameters</a></li>
            <li><a href="../../connections/">Connections</a></li>
            <li><a href="../../coach/">Coach</a></li>
            <li><a href="../../learn/">Learn</a></li>
            <li><a href="../../#download" class="nav-cta">Get the App</a></li>
        </ul>
        <button class="mobile-menu-btn" onclick="document.querySelector('.nav-links').classList.toggle('show')" aria-label="Menu">&#9776;</button>
    </div>
</nav>

<div class="page-title"><div class="wrap">
    <div style="font-size:13.5px; color:var(--ink-faint); margin-bottom:8px"><a href="../" style="color:var(--green-700); font-weight:600">Sample Weekly Plans</a> / Worksheet</div>
    <h1>&#129513; Interactive Weekly Worksheet</h1>
    <p class="meta">Enter your numbers — everything below calculates itself. Nothing leaves your browser.</p>
</div></div>

<section style="padding-top:20px">
    <div class="wrap">
{CORE}
        <div class="plan-cta no-print" style="margin-top:26px">
            <a class="btn outline" href="../../assets/downloads/nutrisize-weekly-worksheet.html" download>&#11015;&#65039; Download offline copy (HTML)</a>
            <a class="btn outline" href="../../assets/downloads/nutrisize-weekly-worksheet-blank.pdf" download>&#128424;&#65039; Printable blank sheet (PDF)</a>
        </div>
        <div class="notice" style="margin-top:26px">
            <strong>Educational tool only.</strong> Estimates use standard population equations and
            are not medical advice. For live tracking with 4,995 foods, 5,404 exercises, and 200+
            physiological parameters, <a href="../../#download">get the Nutrisize Health app</a>.
        </div>
    </div>
</section>
{JS}
<footer>
    <div class="footer-inner">
        <ul class="footer-links">
            <li><a href="../">Plans</a></li>
            <li><a href="../../foods/">Foods</a></li>
            <li><a href="../../nutrients/">Nutrients</a></li>
            <li><a href="../../exercises/">Exercises</a></li>
            <li><a href="../../parameters/">Parameters</a></li>
            <li><a href="../../connections/">Connections</a></li>
            <li><a href="../../coach/">Coach</a></li>
            <li><a href="../../learn/">Learn</a></li>
            <li><a href="../../about/">About</a></li>
            <li><a href="../../privacy/">Privacy Policy</a></li>
            <li><a href="../../disclaimer/">Disclaimer</a></li>
            <li><a href="../../support/">Support</a></li>
            <li><a href="../../survey/">Survey</a></li>
            <li><a href="https://equalinformation.com" target="_blank" rel="noopener">EqualInformation</a></li>
        </ul>
        <p class="footer-copy">Contact: <a href="mailto:contact@nutrisize.health">contact@nutrisize.health</a> &middot; <a href="mailto:nutrisize.universal@gmail.com">nutrisize.universal@gmail.com</a><br>
            &copy; 2026 EqualInformation, LLC. All rights reserved.</p>
    </div>
</footer>

</body>
</html>
"""


def standalone_page(plans_css):
    # keep only the worksheet-relevant rules from plans.css (ws-*, table-scroll, print)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nutrisize Health — Weekly Worksheet (offline)</title>
    <style>
{STANDALONE_CSS}
{plans_css}
    </style>
</head>
<body>

<div class="wshead">
    <h1>&#129513; Nutrisize Health — Weekly Worksheet</h1>
    <p>Offline copy — open this file in any browser; it calculates automatically and saves your
    entries locally. From <a href="{SITE}/plans/">nutrisize.health/plans</a>. Educational only —
    not medical advice.</p>
</div>
<div class="wsmain">
{CORE}
</div>
{JS}
</body>
</html>
"""


def main():
    plans_css = read("assets/css/plans.css")
    # keep worksheet + print sections only (they're self-contained rule blocks)
    keep = []
    for block in plans_css.split("/* ----------"):
        header = block.split("*/")[0].lower()
        if "worksheet" in header or "print" in header:
            keep.append("/* ----------" + block)
    ws_css = "\n".join(keep)

    out1 = os.path.join(ROOT, "plans", "worksheet")
    os.makedirs(out1, exist_ok=True)
    with open(os.path.join(out1, "index.html"), "w") as f:
        f.write(site_page())
    print("wrote plans/worksheet/index.html")

    out2 = os.path.join(ROOT, "assets", "downloads")
    os.makedirs(out2, exist_ok=True)
    with open(os.path.join(out2, "nutrisize-weekly-worksheet.html"), "w") as f:
        f.write(standalone_page(ws_css))
    print("wrote assets/downloads/nutrisize-weekly-worksheet.html")


if __name__ == "__main__":
    main()
