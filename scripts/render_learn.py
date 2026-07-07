#!/usr/bin/env python3
"""Render /learn/ — a knowledge hub: guided learning tracks that tie together the
site's cited resources (nutrient encyclopedia, parameters, connections,
digestion, plans), plus a set of concise foundational explainers on settled
nutrition and exercise science, attributed to the standard bodies the rest of
the site cites (WHO, NIH/IOM, USDA, ACSM). No app-code content is reused.

Usage: python3 scripts/render_learn.py
"""
import os

from render_plans import breadcrumb, ROOT, SITE, esc, footer, head, iap_plug, nav

# --- Foundational explainers (original, concise, attributed) ---------------
# Content is standard, well-established physiology/nutrition science written for
# this site; each carries its authoritative sources.

ARTICLES = [
    {
        "slug": "energy-balance",
        "title": "Energy balance: BMR, TDEE, and how your body spends calories",
        "track": "Nutrition",
        "intro": "Weight change comes down to energy in versus energy out. Understanding where "
                 "your calories go makes every other nutrition decision clearer.",
        "sections": [
            ("Your body's baseline: BMR",
             "Basal metabolic rate (BMR) is the energy your body uses at complete rest just to "
             "stay alive — heartbeat, breathing, temperature, cell repair. It is the largest part "
             "of most people's daily burn, typically 60–70%. BMR rises with body size and muscle "
             "mass and falls gradually with age. The Mifflin–St Jeor equation is the most accurate "
             "common estimate."),
            ("Add your day: TDEE",
             "Total daily energy expenditure (TDEE) is BMR plus everything you do: the thermic "
             "effect of digesting food (about 10% of intake), the energy of deliberate exercise, "
             "and the often-underrated energy of everyday movement — walking, fidgeting, standing "
             "(known as NEAT). TDEE is what you actually burn in a day."),
            ("Why deficits shrink as you go",
             "Eat below your TDEE and you lose weight; above it and you gain. But as body weight "
             "changes, BMR and TDEE change with it, so a fixed calorie target produces a smaller "
             "and smaller gap over time — which is why steady progress naturally slows. Recomputing "
             "your numbers as you go keeps expectations realistic."),
        ],
        "links": [("See it in action", "../../simulator/", "What-if simulator"),
                  ("Plan your own week", "../../plans/worksheet/", "Interactive worksheet")],
        "sources": [("NIH / IOM", "Dietary Reference Intakes for Energy", "https://www.nal.usda.gov/human-nutrition-and-food-safety/dri-calculator"),
                    ("Mifflin MD, St Jeor ST, et al.", "A new predictive equation for resting energy expenditure. Am J Clin Nutr. 1990.", "https://pubmed.ncbi.nlm.nih.gov/2305711/")],
    },
    {
        "slug": "macronutrients",
        "title": "Macronutrients: protein, carbohydrate, and fat",
        "track": "Nutrition",
        "intro": "The three macronutrients supply all of your energy and most of your body's raw "
                 "materials. Here is what each one does and roughly how much you need.",
        "sections": [
            ("Protein — the builder",
             "Protein provides amino acids for muscle, enzymes, hormones, and immune molecules, and "
             "yields 4 kcal per gram. General health needs are around 0.8 g per kg of body weight; "
             "active people and those building or preserving muscle benefit from 1.2–1.6 g/kg or more. "
             "Protein is also the most satiating macronutrient."),
            ("Carbohydrate — the fuel",
             "Carbohydrates are the body's preferred quick energy, at 4 kcal per gram, and the main "
             "fuel for the brain and hard exercise. Quality matters more than quantity: whole grains, "
             "legumes, fruit, and vegetables bring fiber that slows absorption and steadies blood "
             "sugar, unlike refined sugars and starches."),
            ("Fat — the reserve and regulator",
             "Dietary fat carries fat-soluble vitamins, builds cell membranes, and makes hormones, at "
             "9 kcal per gram. Favor unsaturated fats from fish, nuts, seeds, and olive oil; keep "
             "saturated fat moderate and avoid industrial trans fats. A common target is roughly 25–35% "
             "of calories from fat."),
        ],
        "links": [("Look up any nutrient", "../../nutrients/", "Nutrient encyclopedia"),
                  ("Compare foods", "../../foods/", "Food Explorer")],
        "sources": [("USDA / HHS", "Dietary Guidelines for Americans, 2020–2025", "https://www.dietaryguidelines.gov/"),
                    ("NIH ODS", "Nutrient Recommendations and Databases", "https://ods.od.nih.gov/HealthInformation/nutrientrecommendations.aspx")],
    },
    {
        "slug": "micronutrients",
        "title": "Micronutrients: vitamins and minerals in small but vital amounts",
        "track": "Nutrition",
        "intro": "You need micronutrients in milligrams or micrograms, not grams — but a shortfall in "
                 "any one can have outsized effects.",
        "sections": [
            ("What they do",
             "Vitamins and minerals are cofactors: they switch on the reactions that turn food into "
             "energy, build blood and bone, run nerves and muscles, and defend against damage. Because "
             "the body makes few of them, most must come from a varied diet."),
            ("Why variety wins",
             "No single food covers every micronutrient. Eating across colors and food groups — leafy "
             "greens, colorful vegetables and fruit, legumes, whole grains, dairy or fortified "
             "alternatives, and a range of proteins — is the most reliable way to cover the full set."),
            ("Common shortfalls",
             "Even in well-fed populations, vitamin D, iron (especially for menstruating women), "
             "calcium, magnesium, and fiber are frequently under-consumed. Knowing your own gaps — "
             "rather than supplementing blindly — is the smarter approach."),
        ],
        "links": [("Browse all 75 nutrients", "../../nutrients/", "Nutrient encyclopedia"),
                  ("What moves your labs", "../../connections/", "Connections Explorer")],
        "sources": [("NIH ODS", "Vitamin and mineral fact sheets", "https://ods.od.nih.gov/factsheets/list-all/"),
                    ("WHO", "Micronutrients", "https://www.who.int/health-topics/micronutrients")],
    },
    {
        "slug": "fitt-principle",
        "title": "The FITT principle: how to structure exercise",
        "track": "Movement",
        "intro": "FITT — Frequency, Intensity, Time, and Type — is the simple framework behind almost "
                 "every good training plan.",
        "sections": [
            ("The four levers",
             "Frequency is how often you train; Intensity is how hard; Time is how long each session "
             "lasts; Type is the kind of activity — aerobic, strength, flexibility, or balance. Adjust "
             "one lever at a time to make a plan easier or harder without guesswork."),
            ("The baseline to aim for",
             "Adults are advised to get at least 150–300 minutes of moderate aerobic activity (or "
             "75–150 vigorous) per week, plus muscle-strengthening work on two or more days, and — for "
             "older adults — balance training. Any movement counts, and more is generally better up to "
             "a point."),
            ("Progress gradually",
             "Increase just one FITT variable at a time and by small steps to let the body adapt "
             "without injury. Consistency over months beats intensity for a week."),
        ],
        "links": [("Browse 2,504 exercises", "../../exercises/", "Exercise Explorer"),
                  ("See sample weeks by age", "../../plans/", "Sample plans")],
        "sources": [("WHO", "Guidelines on physical activity and sedentary behaviour (2020)", "https://www.who.int/publications/i/item/9789240015128"),
                    ("ACSM", "Guidelines for Exercise Testing and Prescription", "https://www.acsm.org/")],
    },
    {
        "slug": "progressive-overload",
        "title": "Progressive overload: how the body gets stronger",
        "track": "Movement",
        "intro": "Muscles, bones, heart, and lungs adapt to the demands you place on them. Keep the "
                 "demand rising, gently, and they keep improving.",
        "sections": [
            ("Stress, then adapt",
             "Training is a stress; recovery is when the body rebuilds a little stronger than before "
             "(supercompensation). If the stress never increases, adaptation stops — the body has no "
             "reason to change. This is why the same workout, forever, plateaus."),
            ("Ways to add load",
             "You can progress by adding weight, doing more reps or sets, shortening rest, improving "
             "range or control, or increasing frequency. Small, steady increases — on the order of "
             "a few percent — are enough and are far safer than big jumps."),
            ("Respect the ceiling",
             "More is not always better. Progress needs adequate recovery, sleep, and protein; pushing "
             "load faster than the body can adapt invites overuse injury. Deload weeks are a feature, "
             "not a failure."),
        ],
        "links": [("Find exercises by muscle", "../../exercises/", "Exercise Explorer"),
                  ("What training changes in you", "../../connections/", "Connections Explorer")],
        "sources": [("ACSM", "Progression Models in Resistance Training for Healthy Adults", "https://pubmed.ncbi.nlm.nih.gov/19204579/"),
                    ("NSCA", "Essentials of Strength Training and Conditioning", "https://www.nsca.com/")],
    },
    {
        "slug": "recovery-and-sleep",
        "title": "Recovery and sleep: the other half of training",
        "track": "Movement",
        "intro": "Fitness is built during recovery, not during the workout. Sleep is the most powerful "
                 "recovery tool you have.",
        "sections": [
            ("Why rest builds fitness",
             "Adaptation — stronger muscle, denser bone, a more efficient heart — happens between "
             "sessions, fueled by protein, sleep, and time. Train the same tissue again before it has "
             "recovered and you dig a hole instead of building."),
            ("Sleep is non-negotiable",
             "Most adults need 7–9 hours. Deep sleep drives growth-hormone release and tissue repair; "
             "too little blunts recovery, raises resting heart rate, impairs glucose control, and "
             "increases injury and illness risk. Protecting sleep protects everything else."),
            ("Signs you need more",
             "Persistently elevated resting heart rate, poor sleep, low mood, nagging soreness, and "
             "stalled progress are the body asking for rest. An easy week often unlocks the next jump."),
        ],
        "links": [("Track vitals & sleep", "../../parameters/", "Physiological parameters"),
                  ("Time meals to your sleep", "../../digestion/", "Digestion & sleep tool")],
        "sources": [("CDC", "About Sleep and Sleep Health", "https://www.cdc.gov/sleep/"),
                    ("NIH", "Sleep and physical performance", "https://pubmed.ncbi.nlm.nih.gov/29963348/")],
    },
]

TRACKS = [
    ("Nutrition", "&#127822;", "How food becomes energy and raw material — and how to read what's on "
     "your plate.", "Nutrition"),
    ("Movement", "&#127939;", "How the body adapts to exercise, and how to structure training that "
     "works.", "Movement"),
    ("Your body", "&#129728;", "The numbers that describe your health, and what moves them.", None),
]


def source_list(sources):
    rows = "".join(
        f'<div class="cx-ref"><span>'
        f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(t)}</a>'
        f' <span class="cx-src">&mdash; {esc(org)}</span></span></div>'
        for org, t, u in sources)
    return f'<div class="pd-sec"><h4>Sources</h4><div class="cx-refs">{rows}</div></div>'


def article_page(art, prefix="../../"):
    title = f"{art['title']} | Nutrisize Health"
    desc = esc(art["intro"])[:180]
    canonical = f"{SITE}/learn/{art['slug']}/"
    jsonld = f"""    <link rel="stylesheet" href="{prefix}assets/css/explorer.css?v=1">
    <script type="application/ld+json">
    {{"@context":"https://schema.org","@type":"Article","headline":"{esc(art['title'])}",
      "author":{{"@type":"Organization","name":"Nutrisize Health"}},
      "publisher":{{"@type":"Organization","name":"EqualInformation, LLC"}},
      "mainEntityOfPage":"{canonical}"}}
    </script>
"""
    html = head(title, desc, canonical, prefix, jsonld) + nav(prefix) + breadcrumb(prefix, [("Learn", prefix + "learn/"), (art["title"], None)])
    html += f"""
<header class="hero hero-sub">
    <div class="wrap">
        <h1 style="font-size:clamp(28px,4vw,42px)">{esc(art['title'])}</h1>
        <p class="tagline">{esc(art['track'])} &middot; foundations</p>
        <p class="lede">{esc(art['intro'])}</p>
    </div>
</header>

<section>
    <div class="wrap" style="max-width:760px">
"""
    for h, body in art["sections"]:
        html += f'        <div class="pd-sec"><h4 style="font-size:15px">{esc(h)}</h4><p class="pd-row" style="font-size:15px">{esc(body)}</p></div>\n'
    if art.get("links"):
        chips = "".join(f'<a class="cx-badge food" href="{esc(u)}">{esc(t)}</a>' for _, u, t in art["links"])
        html += f'        <div class="pd-sec"><h4>Put it to use</h4><div class="cx-foodlist">{chips}</div></div>\n'
    html += "        " + source_list(art["sources"]) + "\n"
    html += f"""        <div class="notice" style="margin-top:22px">
            <strong>Educational overview only.</strong> General information, not medical or dietary
            advice. Individual needs vary. See our <a href="{prefix}disclaimer/">full disclaimer</a>.
        </div>
    </div>
</section>
"""
    html += footer(prefix)
    return html


def hub_page(prefix="../"):
    title = "Learn — Nutrition & Exercise Science, in Plain Language | Nutrisize Health"
    desc = ("Guided tracks through nutrition and exercise science, plus concise foundations on energy "
            "balance, macronutrients, the FITT principle, progressive overload, and recovery — with "
            "sources, and links into the tools that put them to use.")
    canonical = f"{SITE}/learn/"
    jsonld = f"""    <script type="application/ld+json">
    {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {{"@type":"ListItem","position":1,"name":"Home","item":"{SITE}/"}},
      {{"@type":"ListItem","position":2,"name":"Learn","item":"{canonical}"}}]}}
    </script>
"""
    html = head(title, desc, canonical, prefix, jsonld) + nav(prefix) + breadcrumb(prefix, [("Learn", None)])
    html += f"""
<header class="hero hero-sub">
    <div class="wrap">
        <h1><span class="accent">Learn</span> the fundamentals</h1>
        <p class="tagline">The science behind the numbers, in plain language.</p>
        <p class="lede">
            Short, sourced foundations on how food and movement actually work &mdash; then links
            straight into the tools and libraries that let you apply them. Start anywhere.
        </p>
    </div>
</header>

<section class="tint">
    <div class="wrap">
        <div class="section-head"><span class="kicker">Foundations</span>
            <h2>Start with the essentials</h2>
            <p>Six short reads that make everything else on the site click.</p></div>
        <div class="grid">
"""
    icons = {"Nutrition": "&#127822;", "Movement": "&#127939;"}
    for i, art in enumerate(ARTICLES):
        html += f"""            <a class="card" href="{prefix}learn/{art['slug']}/" style="text-decoration:none; color:inherit">
                <div class="icon{' blue' if i % 2 else ''}">{icons.get(art['track'], '&#128218;')}</div>
                <h3>{esc(art['title'].split(':')[0])}</h3>
                <p>{esc(art['intro'])}</p>
            </a>
"""
    html += """        </div>
    </div>
</section>

<section>
    <div class="wrap">
        <div class="section-head"><span class="kicker">Go deeper</span>
            <h2>Explore by track</h2>
            <p>Each track links into the site's cited libraries and interactive tools.</p></div>
        <div class="grid">
"""
    track_links = {
        "Nutrition": [("Nutrient encyclopedia", "nutrients/"), ("Food Explorer", "foods/"),
                      ("Digestion & sleep", "digestion/"), ("Sample plans", "plans/")],
        "Movement": [("Exercise Explorer", "exercises/"), ("Sample plans", "plans/"),
                     ("Connections Explorer", "connections/")],
        "Your body": [("Physiological parameters", "parameters/"), ("Connections Explorer", "connections/"),
                      ("Meet your Coach", "coach/")],
    }
    for label, icon, blurb, _ in TRACKS:
        links = "".join(f'<a class="cx-badge food" href="{prefix}{u}">{esc(t)}</a>'
                        for t, u in track_links[label])
        html += f"""            <div class="card">
                <div class="icon">{icon}</div>
                <h3>{esc(label)}</h3>
                <p>{esc(blurb)}</p>
                <div class="cx-foodlist" style="margin-top:12px">{links}</div>
            </div>
"""
    html += f"""        </div>
    </div>
</section>

<section class="tint">
    <div class="wrap">
{iap_plug(prefix, "learn",
          "Turn understanding into a habit.",
          "Reading is the start; the app is where you apply it day to day — logging, tracking, and "
          "adapting to your own numbers. Free to download, private by design.")}
    </div>
</section>
"""
    html += footer(prefix)
    return html


def main():
    base = os.path.join(ROOT, "learn")
    os.makedirs(base, exist_ok=True)
    with open(os.path.join(base, "index.html"), "w") as f:
        f.write(hub_page())
    for art in ARTICLES:
        d = os.path.join(base, art["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w") as f:
            f.write(article_page(art))
    print("wrote learn/ hub + %d articles" % len(ARTICLES))


if __name__ == "__main__":
    main()
