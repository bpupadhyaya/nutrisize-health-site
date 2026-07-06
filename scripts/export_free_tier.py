#!/usr/bin/env python3
"""Export the FREE-TIER subset of the Nutrisize Health app databases to
static JSON for the website's explorers and generated pages.

Reads the app repo's SQLite databases (foods.db, exercises.db) and writes:

  assets/data/free/foods.json                one file, all free foods (full detail)
  assets/data/free/exercises-index.json      slim list for search/filter UI
  assets/data/free/exercises/<category>.json per-category detail files

Only rows with is_premium = 0 are ever exported — premium content must not
reach the public site. Re-run after any app database update:

  python3 scripts/export_free_tier.py [--app-repo /path/to/nutrisize-health-claude]
"""

import argparse
import json
import os
import re
import sqlite3
import sys

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_APP_REPO = os.path.normpath(
    os.path.join(SITE_ROOT, "..", "..", "pvt", "nutrisize-health-claude")
)
OUT_DIR = os.path.join(SITE_ROOT, "assets", "data", "free")


def parse_json_field(value):
    """DB TEXT columns hold JSON blobs; tolerate NULL/empty/plain text."""
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return value
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return value  # plain-text field, keep as-is


def slugify(name):
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "item"


def export_foods(db_path):
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row

    servings = {}
    for row in con.execute(
        "SELECT food_id, description, grams FROM food_serving_sizes"
    ):
        servings.setdefault(row["food_id"], []).append(
            {"label": row["description"], "grams": row["grams"]}
        )

    citations = {}
    for row in con.execute(
        "SELECT food_id, source, title, url, year, evidence_grade FROM food_citations"
    ):
        citations.setdefault(row["food_id"], []).append(
            {
                "source": row["source"],
                "title": row["title"],
                "url": row["url"],
                "year": row["year"],
                "grade": row["evidence_grade"],
            }
        )

    foods = []
    for row in con.execute(
        """SELECT id, name, category, subcategory, region, description,
                  seasonality, nutrient_density_score, is_staple,
                  nutrients_per_100g, allergens, common_preparations,
                  glycemic_index_category, anti_inflammatory_score,
                  physiology_links_direct, exercise_positive, exercise_negative,
                  exercise_timing_best, optimization_note
           FROM foods WHERE is_premium = 0 ORDER BY name"""
    ):
        foods.append(
            {
                "id": row["id"],
                "slug": slugify(row["name"]),
                "name": row["name"],
                "category": row["category"],
                "subcategory": row["subcategory"],
                "region": row["region"],
                "description": row["description"],
                "seasonality": parse_json_field(row["seasonality"]),
                "densityScore": row["nutrient_density_score"],
                "isStaple": bool(row["is_staple"]),
                "nutrientsPer100g": parse_json_field(row["nutrients_per_100g"]),
                "allergens": parse_json_field(row["allergens"]),
                "preparations": parse_json_field(row["common_preparations"]),
                "giCategory": row["glycemic_index_category"],
                "antiInflammatoryScore": row["anti_inflammatory_score"],
                "physiologyLinks": parse_json_field(row["physiology_links_direct"]),
                "exercisePositive": parse_json_field(row["exercise_positive"]),
                "exerciseNegative": parse_json_field(row["exercise_negative"]),
                "exerciseTimingBest": row["exercise_timing_best"],
                "optimizationNote": row["optimization_note"],
                "servingSizes": servings.get(row["id"], []),
                "citations": citations.get(row["id"], []),
            }
        )
    con.close()

    # slugs must be unique — per-food SEO pages will use them as URLs
    seen = {}
    for f in foods:
        if f["slug"] in seen:
            f["slug"] = "%s-%s" % (f["slug"], f["id"].lower())
        seen[f["slug"]] = True

    return foods


def export_exercises(db_path):
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row

    index = []
    details = {}  # category -> [exercise]
    for row in con.execute(
        """SELECT id, name, category, subcategory, muscle_group_primary,
                  muscle_group_secondary, equipment, difficulty, simply_put,
                  how_to_perform, sets_reps, calorie_burn, calorie_burn_score,
                  met_value, common_mistakes, breathing_cues, contraindications,
                  physiology_links
           FROM exercises WHERE is_premium = 0 ORDER BY name"""
    ):
        cat = row["category"] or "other"
        index.append(
            {
                "id": row["id"],
                "name": row["name"],
                "category": cat,
                "subcategory": row["subcategory"],
                "musclePrimary": row["muscle_group_primary"],
                "equipment": row["equipment"],
                "difficulty": row["difficulty"],
                "met": parse_json_field(row["met_value"]),
                "burnScore": row["calorie_burn_score"],
            }
        )
        details.setdefault(cat, []).append(
            {
                "id": row["id"],
                "name": row["name"],
                "subcategory": row["subcategory"],
                "musclePrimary": row["muscle_group_primary"],
                "muscleSecondary": row["muscle_group_secondary"],
                "equipment": row["equipment"],
                "difficulty": row["difficulty"],
                "simplyPut": row["simply_put"],
                "howTo": row["how_to_perform"],
                "setsReps": parse_json_field(row["sets_reps"]),
                "calorieBurn": parse_json_field(row["calorie_burn"]),
                "met": parse_json_field(row["met_value"]),
                "commonMistakes": parse_json_field(row["common_mistakes"]),
                "breathingCues": parse_json_field(row["breathing_cues"]),
                "contraindications": parse_json_field(row["contraindications"]),
                "physiologyLinks": parse_json_field(row["physiology_links"]),
            }
        )
    con.close()
    return index, details


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, separators=(",", ":"))
    return os.path.getsize(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--app-repo", default=DEFAULT_APP_REPO)
    args = ap.parse_args()

    res = os.path.join(args.app_repo, "ios", "NutrisizeHealth", "Resources")
    foods_db = os.path.join(res, "foods.db")
    exercises_db = os.path.join(res, "exercises.db")
    for p in (foods_db, exercises_db):
        if not os.path.exists(p):
            sys.exit("Database not found: %s" % p)

    foods = export_foods(foods_db)
    size = write_json(os.path.join(OUT_DIR, "foods.json"), {"foods": foods})
    print("foods.json: %d free foods, %.1f KB" % (len(foods), size / 1024.0))

    index, details = export_exercises(exercises_db)
    size = write_json(
        os.path.join(OUT_DIR, "exercises-index.json"), {"exercises": index}
    )
    print(
        "exercises-index.json: %d free exercises, %.1f KB"
        % (len(index), size / 1024.0)
    )
    for cat, items in sorted(details.items()):
        fname = os.path.join(OUT_DIR, "exercises", "%s.json" % slugify(cat))
        size = write_json(fname, {"category": cat, "exercises": items})
        print(
            "exercises/%s.json: %d items, %.1f KB"
            % (slugify(cat), len(items), size / 1024.0)
        )

    # Guardrail: confirm no premium rows leaked
    con = sqlite3.connect(foods_db)
    free_foods = con.execute(
        "SELECT count(*) FROM foods WHERE is_premium = 0"
    ).fetchone()[0]
    con.close()
    assert len(foods) == free_foods, "food count mismatch vs is_premium=0"
    con = sqlite3.connect(exercises_db)
    free_ex = con.execute(
        "SELECT count(*) FROM exercises WHERE is_premium = 0"
    ).fetchone()[0]
    con.close()
    assert len(index) == free_ex, "exercise count mismatch vs is_premium=0"
    print("OK: exports match is_premium=0 counts exactly.")


if __name__ == "__main__":
    main()
