#!/usr/bin/env python3
"""Export dual-audience detail for the 64 tracked physiological parameters shown
on /parameters/, joining scripts/physiology_tracking.json (the curated 64) to
the app's full physiology_data.json by name.

Every parameter gets a layman view + a clinical quick reference. The DEEPER
clinical reference (differential diagnosis, drug interactions, lab methodology,
medical codes, age-specific notes, global ranges) is included in full only for
FREE-tier parameters; for premium parameters those fields are OMITTED from the
output entirely (not merely hidden) so paid content never ships to the browser —
the popup shows a Physiology Premium plug instead.

Output: assets/data/free/parameter-details.json
Usage:  python3 scripts/export_param_details.py [--app-repo <path>]
"""
import argparse
import json
import os
import re
import sys

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_APP_REPO = os.path.normpath(
    os.path.join(SITE_ROOT, "..", "..", "pvt", "nutrisize-health-claude")
)
TRACKED = os.path.join(SITE_ROOT, "scripts", "physiology_tracking.json")
OUT = os.path.join(SITE_ROOT, "assets", "data", "free", "parameter-details.json")


def norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--app-repo", default=DEFAULT_APP_REPO)
    args = ap.parse_args()

    physio = os.path.join(args.app_repo, "ios", "NutrisizeHealth", "Resources",
                          "physiology_data.json")
    if not os.path.exists(physio):
        sys.exit("Not found: %s" % physio)

    app = json.load(open(physio))["parameters"]
    by_name = {}
    for p in app:
        by_name[norm(p["name"])] = p
        for a in p.get("aliases") or []:
            by_name.setdefault(norm(a), p)

    tracked = json.load(open(TRACKED))
    out, n_free, n_prem, missing = [], 0, 0, []
    for t in tracked["tracked"]:
        p = by_name.get(norm(t["name"]))
        if not p:
            missing.append(t["name"])
            continue
        premium = bool(p.get("premium"))
        entry = {
            "id": p["id"],
            "name": p["name"],
            "system": t.get("system"),
            "freq": t.get("freq"),
            "range": t.get("range"),
            "premium": premium,
            "pronunciation": p.get("pronunciation"),
            # Layman view — always shipped.
            "layman": {
                "simplyPut": p.get("simplyPut"),
                "analogy": p.get("analogy"),
                "whatItTells": t.get("desc"),
                "whenToWorry": p.get("whenToWorry"),
            },
            # Clinical quick reference — always shipped.
            "quickRef": {
                "interpretation": p.get("interpretation"),
                "clinicalPearl": p.get("clinicalPearl"),
                "actionGuidance": p.get("actionGuidance"),
            },
            "citations": p.get("citations") or [],
        }
        # Deep clinical reference — FREE params only; omitted for premium so the
        # paid content is never present in the downloaded JSON.
        if not premium:
            entry["detail"] = {
                "differentialDiagnosis": p.get("differentialDiagnosis"),
                "drugInteractions": p.get("drugInteractions"),
                "labMethodology": p.get("labMethodology"),
                "medicalCodes": p.get("medicalCodes"),
                "ageSpecificNotes": p.get("ageSpecificNotes"),
                "globalRanges": p.get("globalRanges"),
            }
            n_free += 1
        else:
            n_prem += 1
        out.append(entry)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({"parameters": out, "totalParameters": tracked["totalParameters"]},
                  fh, ensure_ascii=False, separators=(",", ":"))
    size = os.path.getsize(OUT) / 1024.0

    # Guardrail: no premium entry may carry the gated 'detail' block.
    leaked = [e["id"] for e in out if e["premium"] and "detail" in e]
    assert not leaked, "premium detail leaked: %s" % leaked
    if missing:
        print("WARNING unmatched:", missing)
    print("parameter-details.json: %d params (%d free w/ full detail, %d premium gated), %.1f KB"
          % (len(out), n_free, n_prem, size))
    print("OK: no premium detail present in output.")


if __name__ == "__main__":
    main()
