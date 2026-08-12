#!/usr/bin/env python3
"""Render /health/ — "The Health library": a marketing showcase of the app's
Health module, 91 cited guide topics spanning mental health, women's/men's/
reproductive health, chronic conditions, life stages, and everyday care.
Included with every Coach subscription at no extra charge (folded in 2026-08-11
— see render_coach.py's HEALTH_SUB_NOTE). All topic titles below are taken
verbatim from the app's own healthGuideTopics list (Android:
app/src/main/java/com/nutrisize/health/ui/screens/HealthGuideTopics.kt, iOS:
HealthHubView.swift's healthNavItems) — do not invent titles that aren't in
that source list.

Usage: python3 scripts/render_health.py   (idempotent)
"""
import os

from render_plans import breadcrumb, ROOT, SITE, esc, footer, head, iap_plug, nav, store_urls

SUB_PRICE = "$4.99/month"
TOPIC_COUNT = 91
CITATION_KEYS = 83  # verified floor across both platforms (Android 83 / iOS 89 keys)
CITATION_TOTAL = CITATION_KEYS * 3

# Six illustrative groupings of real topic titles (verbatim from
# HealthGuideTopics.kt) for scannability on this page. The app itself does
# NOT group topics into these sections — all 91 live in one flat,
# search-filtered library by design. Don't claim otherwise in copy.
GROUPS = [
    ("Mental health & wellbeing", "&#129504;", [
        "Mental Health", "Anxiety Recovery", "Depression Recovery", "PTSD Recovery",
        "CBT Basics", "OCD Guide", "Bipolar Disorder", "Social Anxiety",
        "Anger Management", "ADHD Guide", "ADHD in Adults", "Teen Mental Health",
        "Children's Mental Health", "Men's Mental Health", "Autism Spectrum",
        "BPD Awareness", "Compassion Fatigue", "Eating Disorders",
        "Veterans Mental Health", "Recovery Support",
    ]),
    ("Women's, men's & reproductive health", "&#9895;&#65039;", [
        "Women's Health", "Men's Health", "Pregnancy", "Pregnancy Nutrition",
        "Postpartum Support", "Menopause Guide", "Perimenopause Guide",
        "Pelvic Floor Health", "Reproductive Health", "Preconception Health",
        "Infertility Guide", "Miscarriage Support", "STI Prevention",
        "Men's Midlife Health", "LGBTQ+ Health", "LGBTQ+ Youth",
        "Sexual Health: Older Adults",
    ]),
    ("Chronic conditions & disease management", "&#128151;", [
        "Chronic Conditions", "Chronic Pain", "Diabetes Management", "Heart Health",
        "Kidney Health", "Autoimmune Guide", "Lupus Guide", "Multiple Sclerosis",
        "Fibromyalgia Guide", "Asthma Guide", "Migraine Management",
        "Stroke Recovery", "Thyroid Health", "Chronic Fatigue", "Parkinson's Guide",
        "Cancer Screening", "Living with HIV", "Gut Microbiome",
        "Celiac & Gut Health",
    ]),
    ("Life stages & preventive care", "&#128197;", [
        "Child Health", "Elder Care", "Senior Health Guide", "Active Aging",
        "Preventive Health Calendar", "Genetic Testing", "Organ Donation",
        "Navigating Healthcare",
    ]),
    ("Sleep, body & everyday care", "&#128564;", [
        "Sleep Health", "Sleep Disorders", "Sleep Hygiene", "Dental Health Guide",
        "Eye Health", "Vision Care Guide", "Skin Care Guide",
        "Posture & Back Health", "Hormone Health", "Weight Management",
        "Water Safety", "First Aid",
    ]),
    ("Nutrition, fitness & recovery", "&#127939;", [
        "Nutrition Guide", "Nutrition Deep Dive", "Mindful Eating",
        "Athletic Training", "Sports Injury Recovery",
    ]),
]

# Real organizations behind the Health library's citations (verified against
# android/.../HealthCitations.kt) — general homepage links only; the app's own
# per-guide "Sources" section links the specific page cited for that topic.
SOURCE_ORGS = [
    ("CDC", "https://www.cdc.gov/"),
    ("NIH / MedlinePlus", "https://medlineplus.gov/"),
    ("Mayo Clinic", "https://www.mayoclinic.org/"),
    ("NIMH", "https://www.nimh.nih.gov/"),
    ("National Institute on Aging", "https://www.nia.nih.gov/"),
    ("ACOG", "https://www.acog.org/"),
    ("WHO", "https://www.who.int/"),
    ("HHS Office on Women's Health", "https://www.womenshealth.gov/"),
    ("SAMHSA", "https://www.samhsa.gov/"),
    ("AAP HealthyChildren.org", "https://www.healthychildren.org/"),
    ("American Heart Association", "https://www.heart.org/"),
    ("American Diabetes Association", "https://diabetes.org/"),
    ("National Kidney Foundation", "https://www.kidney.org/"),
    ("American Cancer Society", "https://www.cancer.org/"),
    ("U.S. Dept. of Veterans Affairs", "https://www.va.gov/"),
]


def page():
    title = "The Health Library — 91 Cited Guides on Real Medical Topics | Nutrisize Health"
    desc = ("The Health library: 91 cited guides on mental health, women's & men's health, "
            "chronic conditions, life stages, and everyday care — sourced from CDC, NIH, Mayo "
            "Clinic, WHO, and 50+ more. Included free with Coach, $4.99/month.")
    canonical = f"{SITE}/health/"
    prefix = "../"

    extra = f"""    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type": "ListItem", "position": 1, "name": "Home", "item": "{SITE}/"}},
        {{"@type": "ListItem", "position": 2, "name": "Health Library", "item": "{canonical}"}}
      ]
    }}
    </script>
"""
    ios, android = store_urls("health")
    store_row = f"""        <div class="store-buttons" style="margin:22px 0">
            <a href="{ios}" target="_blank" rel="noopener"><img class="badge-ios" src="{prefix}assets/img/app-store-badge.svg" alt="Download on the App Store" height="54"></a>
            <a href="{android}" target="_blank" rel="noopener"><img class="badge-play" src="{prefix}assets/img/google-play-badge.png" alt="Get it on Google Play" height="80"></a>
        </div>
"""

    group_cards = "".join(
        f"""            <div class="card">
                <div class="icon{' blue' if i % 2 else ''}">{icon}</div>
                <h3>{esc(name)}</h3>
                <p class="tool-note" style="margin-top:8px">{" &middot; ".join(esc(t) for t in topics[:6])}{" &middot; more" if len(topics) > 6 else ""}</p>
            </div>
""" for i, (name, icon, topics) in enumerate(GROUPS))

    total_shown = sum(len(topics) for _, _, topics in GROUPS)

    source_chips = "".join(
        f'<a class="chip" href="{url}" target="_blank" rel="noopener" style="text-decoration:none">{esc(name)}</a>\n            '
        for name, url in SOURCE_ORGS)

    html = head(title, desc, canonical, prefix, extra) + nav(prefix) + breadcrumb(prefix, [("Health", None)])
    html += f"""
<header class="hero hero-sub">
    <div class="wrap">
        <h1>The <span class="accent">Health</span> library</h1>
        <p class="tagline">{TOPIC_COUNT} cited guides on the health topics that actually come up in real life.</p>
        <p class="lede">
            From managing a chronic condition to navigating menopause, supporting a child's mental
            health, or just building better sleep habits — the Health library is {TOPIC_COUNT}
            in-depth, cited guides, one searchable library, no folders to dig through.
        </p>
        <p class="lede" style="margin-top:8px"><strong>Included with Coach</strong> — {SUB_PRICE},
            cancel anytime. No separate charge for Health. 100% offline, on-device, no cloud,
            no accounts. <a href="{prefix}coach/">See everything Coach includes &rarr;</a></p>
        {store_row}
    </div>
</header>

<section class="tint">
    <div class="wrap">
        <div class="section-head">
            <span class="kicker">What's inside</span>
            <h2>{TOPIC_COUNT} guides, six ways to browse this page</h2>
            <p>In the app it's one flat, instantly searchable library &mdash; grouped here just to
            make this page easier to scan. {total_shown} of the {TOPIC_COUNT} guides are named
            below; the rest are a search away in the app.</p>
        </div>
        <div class="grid">
{group_cards}        </div>
    </div>
</section>

<section>
    <div class="wrap">
        <div class="section-head">
            <span class="kicker">Every guide is cited</span>
            <h2>Grounded in real medical guidance, not generic advice</h2>
            <p>{CITATION_KEYS}+ guides carry their own end-of-article source list &mdash; three
            citations each, {CITATION_TOTAL}+ in total &mdash; drawn from 50+ authoritative medical
            and public-health bodies, including:</p>
        </div>
        <div class="chips" style="justify-content:center">
            {source_chips}
        </div>
        <p class="tool-note" style="text-align:center; margin-top:22px; max-width:720px; margin-left:auto; margin-right:auto">
            Each guide's own citations live at the bottom of that guide in the app, with a direct
            link to the source. This library is educational information, not medical advice &mdash;
            <a href="{prefix}disclaimer/">read the full disclaimer</a>.
        </p>
    </div>
</section>

<section class="tint">
    <div class="wrap">
        <div class="section-head">
            <span class="kicker">One subscription, two libraries</span>
            <h2>Health comes bundled with Coach</h2>
            <p>Health used to be its own $4.99/month add-on. As of August 2026 it's folded
            into Coach at no extra charge &mdash; subscribe once and you get the adaptive plans,
            Ask the Coach, and 10 health KPIs of <a href="{prefix}coach/">Coach</a>, plus all
            {TOPIC_COUNT} Health guides, together.</p>
        </div>
        <div style="display:flex; flex-wrap:wrap; gap:12px; justify-content:center; margin-top:10px">
            <a class="btn outline" href="{prefix}coach/">Meet your Coach &rarr;</a>
            <a class="btn outline" href="{prefix}parameters/">See the 200+ tracked parameters &rarr;</a>
        </div>
    </div>
</section>

<section>
    <div class="wrap">
{iap_plug(prefix, "health",
          "Read it free in the app, right now.",
          f"All {TOPIC_COUNT} Health guides live in the Nutrisize Health app, right alongside "
          f"your Coach. Download the app free, then unlock Coach + Health together for "
          f"<strong>{SUB_PRICE}</strong> (cancel anytime).")}
    </div>
</section>
"""
    html += footer(prefix)
    return html


def main():
    out_dir = os.path.join(ROOT, "health")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(page())
    print(f"wrote health/index.html ({len(GROUPS)} topic groups, {sum(len(t) for _,_,t in GROUPS)} topics shown, {len(SOURCE_ORGS)} source orgs)")


if __name__ == "__main__":
    main()
