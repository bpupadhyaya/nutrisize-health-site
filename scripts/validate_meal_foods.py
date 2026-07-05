#!/usr/bin/env python3
"""Validate scripts/meal_foods/<plan>.json itemizations against the published
per-meal kcal/macros in assets/data/plans/<plan>.json.

Usage:
  python3 scripts/validate_meal_foods.py            # all plans that have a mapping file
  python3 scripts/validate_meal_foods.py male-teen  # one plan

A meal passes when each of kcal/protein/carbs/fat is within max(12%, floor)
of the published value (floors: 30 kcal, 3 g protein, 5 g carbs, 3 g fat).
Exit code 0 = all validated meals pass, 1 = failures or structural errors.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLANS_DIR = os.path.join(ROOT, "assets", "data", "plans")
FOODS_DIR = os.path.join(ROOT, "scripts", "meal_foods")
DB_PATH = os.path.join(ROOT, "scripts", "food_db.json")

REL_TOL = 0.12
ABS_FLOOR = {"kcal": 30.0, "proteinG": 3.0, "carbsG": 5.0, "fatG": 3.0}
DB_KEY = {"kcal": "calories", "proteinG": "protein", "carbsG": "carbohydrates", "fatG": "fat"}


def compute(foods, db):
    totals = {k: 0.0 for k in DB_KEY}
    for f in foods:
        n = db[f["id"]]["n"]
        scale = f["g"] / 100.0
        for k, dbk in DB_KEY.items():
            totals[k] += n[dbk] * scale
    return totals


def validate_plan(key, db):
    plan = json.load(open(os.path.join(PLANS_DIR, key + ".json")))
    mapping = json.load(open(os.path.join(FOODS_DIR, key + ".json")))
    errors, failures, table = [], 0, []

    for day in plan["week"]:
        day_map = mapping.get(day["day"])
        if day_map is None:
            errors.append(f"missing day: {day['day']}")
            continue
        for meal in day["meals"]:
            foods = day_map.get(meal["meal"])
            if not foods:
                errors.append(f"missing meal: {day['day']}/{meal['meal']}")
                continue
            bad_ids = [f["id"] for f in foods if f["id"] not in db]
            if bad_ids:
                errors.append(f"unknown food ids in {day['day']}/{meal['meal']}: {bad_ids}")
                continue
            got = compute(foods, db)
            row_bad = []
            for k in DB_KEY:
                want = float(meal[k])
                tol = max(abs(want) * REL_TOL, ABS_FLOOR[k])
                if abs(got[k] - want) > tol:
                    row_bad.append(f"{k} {got[k]:.0f} vs {want:.0f}")
            if row_bad:
                failures += 1
                table.append(f"  FAIL {day['day']:<9} {meal['meal']:<9} " + "; ".join(row_bad))
    return errors, failures, table


def main():
    db = json.load(open(DB_PATH))
    if len(sys.argv) > 1:
        keys = [sys.argv[1]]
    else:
        keys = sorted(
            f[:-5] for f in os.listdir(FOODS_DIR) if f.endswith(".json")
        ) if os.path.isdir(FOODS_DIR) else []
    if not keys:
        print("no mapping files found in scripts/meal_foods/")
        return 1

    any_bad = False
    for key in keys:
        errors, failures, table = validate_plan(key, db)
        status = "OK" if not errors and not failures else f"{failures} fail, {len(errors)} structural"
        print(f"{key}: {status}")
        for e in errors:
            print("  ERROR " + e)
        for row in table:
            print(row)
        if errors or failures:
            any_bad = True
    return 1 if any_bad else 0


if __name__ == "__main__":
    sys.exit(main())
