# Meal-nutrition popup — follow-ups (handoff)

**Done (commit 3048cc4):** tapping any meal row in the day tables opens a fixed-overlay popup with
that meal's **Calories / Protein / Carbs / Fat** as %DV bars (FDA 2,000-kcal Daily Values) + numeric
grams. Closes on × / outside-tap / Esc; keyboard-accessible; page never shifts; mobile bottom-sheet.

**Files:**
- `assets/js/plan-popup.js` — event-delegated open/close + bar rendering (no deps). Extend `ORDER`
  and `DV` to add more nutrients.
- `assets/css/plans.css` — popup + `.nm-*` bar styles (per-macro colors), `.meal-row` hover/focus.
- `scripts/render_plans.py` — `esc_attr()`; meal `<tr>`s carry `class="meal-row" role="button"
  tabindex="0"` + `data-meal/items/kcal/protein/carbs/fat`; `head()` includes the popup script.
- **Regenerate all 10 plan pages after any change:** `python3 scripts/render_plans.py`

## Pending

### 1. Fiber / sodium / sugar context
Honest data limit: these exist only at **day/plan** level, not per meal —
`week[].mealTotals.fiberG` (per day) and `profile.sodiumMgMax` / `profile.addedSugarGMax` (per
plan) in `assets/data/plans/*.json`. Options: surface day-total fiber in the popup **labeled
"day total"**, or extend the JSON + `render_plans.py` with per-meal fiber/sodium/sugar (estimates —
keep the site's "educational estimate" framing).

### 2. Per-food micronutrients (match the mobile app)
A **data project**. The site's plan data is per-MEAL kcal + 3 macros, with foods as a free-text
`items` string. To match the app's full vitamins/minerals-per-food:
1. Itemize each meal's foods into discrete items.
2. Attach a nutrient database (kcal + macros + micros per serving). **Reuse the mobile app's
   food-nutrient database** — repo `bpupadhyaya/nutrisize-health-claude`.
3. Render micronutrient bars in the popup alongside the macro bars (extend `ORDER`/`DV` in
   plan-popup.js; feed values via `data-*` or a per-meal JSON lookup).

Keep everything educational-only (no medical/dietary advice), matching the rest of the site.
