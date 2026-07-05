# Meal-nutrition popup — follow-ups (handoff)

**Done (commit 3048cc4):** tapping any meal row in the day tables opens a fixed-overlay popup with
that meal's **Calories / Protein / Carbs / Fat** as %DV bars (FDA 2,000-kcal Daily Values) + numeric
grams. Closes on × / outside-tap / Esc; keyboard-accessible; page never shifts; mobile bottom-sheet.

**Done (this pass):** both pending items shipped via one build-time data pipeline.
Every meal now also shows **Fiber** (%DV vs 28 g), **Sodium** (%DV vs 2,300 mg), **Total sugar**
(grams only — FDA defines a DV for *added* sugar, which this data doesn't carry), and a collapsible
**Vitamins & minerals** section (11 vitamins + 7 minerals, %DV vs FDA adult DVs).

**Done (follow-up):** per-food breakdown, matching the mobile app. The popup's "Foods in this
meal" section lists every constituent food with its portion and kcal; each expands to that food's
full 25-nutrient panel (macros + fiber/sugar/sodium + all micros, %DV) for its portion. The page
blob now carries a per-page food table (`foods`: name + per-100g values in FOOD_NUTRIENT_ORDER)
plus per-meal food lists (`meals[nid].i`: [food index, grams]); the popup multiplies per-100g by
grams client-side. Per-food fiber applies the day scale (`meals[nid].s`) so foods sum to their
meal and meals sum to the day.

## How it works

- `scripts/food_db.json` — 593 foods (id, name, nutrientsPer100g: kcal + macros + fiber/sugar/sodium
  + 18 micros), a trimmed derivative of the mobile app's food database
  (`nutrisize-health-claude/web/public/foods_*.json`). Build-time only; never shipped to the browser.
  Units: vitamins A/D/K/B9/B12 + selenium in µg; C/E/B1/B2/B3/B6 + minerals in mg.
- `scripts/meal_foods/<plan>.json` — each of the 280 meals itemized as `[{id, grams}]` against the
  food DB, keyed by day → meal name. Curated so recomputed kcal/macros match the published per-meal
  numbers.
- `scripts/validate_meal_foods.py` — the honesty guard. Recomputes kcal/protein/carbs/fat from the
  itemization and fails any meal off by more than max(12%, small-absolute-floor) from the published
  values. **Run it after editing any mapping.** All 280 meals pass.
- `scripts/render_plans.py` — `meal_nutrient_blob()` sums the 21 extended nutrients per meal
  (NUTRIENT_ORDER must stay in sync with NUTR in plan-popup.js — blob values are positional arrays)
  and embeds one compact `<script type="application/json" id="nutri-data">` blob per plan page.
  Per-meal fiber is scaled per day so meals sum exactly to the published `mealTotals.fiberG`.
  **Regenerate all pages after any change:** `python3 scripts/render_plans.py`
- `assets/js/plan-popup.js` — lazily parses `#nutri-data` on first tap; falls back to macros-only
  if the blob is missing or corrupt. `assets/css/plans.css` — `.nm-micros` grid + fiber/sodium bar
  colors.

Page cost: ~+6.5 KB gzipped per plan page (9.6 → ~16 KB) including the per-food breakdown.
No extra HTTP requests; A/B-measured load and popup-open timings unchanged vs the original site.

## Notes / known limits

- Micronutrient values are **educational estimates** derived from the curated itemizations, not
  lab-analyzed recipe data. Framing on the page stays "educational estimate".
- The published plan macros for the child/teen plans pair high kcal with low protein, which forced
  unrealistically small meat portions in the itemizations (e.g. 10–20 g chicken) to stay within the
  protein tolerance. If plan macros are ever rebalanced, revisit those mappings.
- No cucumber/crackers/cereal/falafel/pancake entries in the food DB — agents substituted the
  nutritionally closest items (zucchini, rice-cake, component decompositions); substitutions are
  consistent across plans.
