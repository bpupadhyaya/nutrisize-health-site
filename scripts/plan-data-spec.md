# Sample Weekly Plan — Data Specification

Each file `assets/data/plans/<key>.json` holds one demographic category's sample week
(nutrition + exercise) for a **normal, healthy person** of that group. Educational only —
no medical advice, no supplements, no brand names.

## Fixed profile constants (do not change)

| key | gender | ageGroup | ageRange | refAge | heightCm | weightKg | targetKcal | proteinG |
|---|---|---|---|---|---|---|---|---|
| male-child | Male | Child | 6–11 | 9 | 133 | 29 | 1800 | 34 |
| male-teen | Male | Teenager | 12–17 | 15 | 170 | 58 | 2600 | 65 |
| male-young-adult | Male | Young adult | 18–35 | 27 | 176 | 72 | 2700 | 115 |
| male-middle-age | Male | Middle age | 36–55 | 45 | 176 | 79 | 2400 | 110 |
| male-older-adult | Male | Older adult | 56+ | 68 | 173 | 76 | 2200 | 95 |
| female-child | Female | Child | 6–11 | 9 | 132 | 28 | 1600 | 34 |
| female-teen | Female | Teenager | 12–17 | 15 | 162 | 52 | 2000 | 52 |
| female-young-adult | Female | Young adult | 18–35 | 27 | 163 | 60 | 2100 | 90 |
| female-middle-age | Female | Middle age | 36–55 | 45 | 162 | 66 | 2000 | 85 |
| female-older-adult | Female | Older adult | 56+ | 68 | 159 | 64 | 1800 | 77 |

Compute `bmi` = weightKg / (heightCm/100)^2, rounded to 1 decimal.
BMR: Mifflin-St Jeor for adults; Schofield for <18 (round to nearest 10).
Activity level: "Moderately active" for all groups (children/teens phrased as
"Active play / sports (typical for age)").

## Macro & fiber rules

- Protein = table value above (g/day). Fat 25–32% of kcal. Carbs = remainder.
- Fiber target ≈ 14 g per 1000 kcal (children: use age RDA ≈ age+5 to age+10 g).
- Sodium max 2300 mg (children 1500–1800 mg). Added sugar < 10% kcal.
- Water: adults M 3.0 L, F 2.2 L; teens 2.4/1.9 L; children 1.7 L.

## JSON schema (exact keys)

```json
{
  "key": "male-young-adult",
  "gender": "Male",
  "ageGroup": "Young adult",
  "ageRange": "18–35",
  "refAge": 27,
  "profile": {
    "heightCm": 176, "weightKg": 72, "bmi": 23.2,
    "bmrKcal": 1710, "activity": "Moderately active",
    "tdeeKcal": 2650, "targetKcal": 2700,
    "proteinG": 115, "carbsG": 355, "fatG": 85, "fiberG": 38,
    "waterL": 3.0, "sodiumMgMax": 2300, "addedSugarGMax": 34
  },
  "physiologicalParams": [
    {"name": "Resting heart rate", "typical": "60–75 bpm",
     "expectedChange": "Down 3–8 bpm over 8–12 weeks",
     "driver": "Aerobic sessions increase stroke volume"}
  ],
  "week": [
    {
      "day": "Monday",
      "meals": [
        {"meal": "Breakfast", "items": "Oatmeal with blueberries, walnuts; low-fat milk",
         "kcal": 520, "proteinG": 22, "carbsG": 78, "fatG": 14}
      ],
      "mealTotals": {"kcal": 2690, "proteinG": 116, "carbsG": 352, "fatG": 86, "fiberG": 37},
      "exercise": {"activity": "Brisk walk + bodyweight strength circuit",
                   "durationMin": 45, "intensity": "Moderate",
                   "kcalBurned": 320, "focus": "Cardio + full-body strength"},
      "highlight": "One short sentence on why this day is shaped this way."
    }
  ],
  "micronutrients": [
    {"name": "Calcium", "target": "1000 mg", "percentMet": 104,
     "keySources": "Milk, yogurt, kale"}
  ],
  "changes": {
    "nutrition": ["4–5 bullets: physiological changes this eating pattern drives"],
    "exercise": ["4–5 bullets: physiological changes this movement pattern drives"]
  },
  "notes": "1–2 sentences of category-specific guidance."
}
```

## Content rules

- `week`: exactly 7 entries, Monday→Sunday. Each day exactly 4 meals:
  Breakfast, Lunch, Snack, Dinner (in that order).
- Real everyday foods with portions implied by kcal; cuisine variety across the week
  (e.g. Mediterranean, Asian, Latin, classic American); no repeated dinner in a week.
- Arithmetic MUST hold: mealTotals.kcal = sum of the 4 meals' kcal (exact);
  same for proteinG/carbsG/fatG (exact sums). Weekly mean kcal within ±3% of targetKcal.
  Macro energy (4P+4C+9F) within ±8% of mealTotals.kcal each day.
- `exercise`: age-appropriate. Children = active play/sports; teens = sports/PE;
  adults = cardio + strength mix; older adults = walking, strength, balance,
  flexibility (fall prevention). Include 1 lighter/rest-style day (stretching/easy walk).
  kcalBurned realistic for the body weight (roughly METs x weight x hours).
- `physiologicalParams`: 7–8 rows. Adults: resting HR, blood pressure, fasting glucose,
  LDL/HDL, VO2max, body-fat %, muscle mass, sleep quality. Children/teens: growth &
  bone development, motor skills, aerobic fitness, healthy weight trajectory, sleep,
  focus/mood — NOT adult disease markers.
- `micronutrients`: 8 rows — calcium, iron, potassium, vitamin D, vitamin C,
  vitamin B12, magnesium, zinc (folate instead of B12 for females 18–55).
  Targets = NIH RDA for the group; percentMet 85–130 (realistic from food).
- Tone: encouraging, factual, plain English. No medical claims, no "cures",
  no supplements, no brand names.
