import json
import re

# ---------- paths ----------
GS_PATH = "Personal_data_sets/Datasets/Golden_standard/random_trials_annotated.json"
ONTOLOGY_PATH = "Personal_data_sets/Results/LLM_extraction/biomarker_aggregate.json"
OUTPUT_PATH = "Personal_data_sets/Results/Ontology_Validation/oracle_mapping_results.json"


# ---------- utils ----------
def normalize(text: str) -> str:
    """
    Basic normalization for lenient string matching
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text.strip()


def is_her2_brca(bm: str) -> bool:
    """
    Restrict oracle evaluation to HER2 / BRCA scope
    """
    bm = bm.lower()
    return (
        "her2" in bm
        or "erbb2" in bm
        or "brca1" in bm
        or "brca2" in bm
    )


# ---------- load data ----------
with open(GS_PATH) as f:
    gs_data = json.load(f)

with open(ONTOLOGY_PATH) as f:
    ontology_dict = json.load(f)

# ontology terms = keys of aggregate dict
ontology_terms = list(ontology_dict.keys())
ontology_norm = [normalize(t) for t in ontology_terms]


# ---------- oracle mapping ----------
results = {
    "total_biomarkers": 0,
    "matched": 0,
    "unmatched": 0,
    "details": []
}

for trial_id, trial in gs_data.items():

    # collect GS biomarkers (inclusion + exclusion)
    gs_biomarkers = []

    for group in trial.get("inclusion_biomarker", []):
        gs_biomarkers.extend(group)

    for group in trial.get("exclusion_biomarker", []):
        gs_biomarkers.extend(group)

    for bm in gs_biomarkers:

        # 🔑 restrict oracle evaluation to HER2 / BRCA only
        if not is_her2_brca(bm):
            continue

        results["total_biomarkers"] += 1
        bm_norm = normalize(bm)

        # lenient oracle mapping
        matched_terms = [
            ontology_terms[i]
            for i, o_norm in enumerate(ontology_norm)
            if bm_norm in o_norm or o_norm in bm_norm
        ]

        if matched_terms:
            results["matched"] += 1
            results["details"].append({
                "trial_id": trial_id,
                "gold_biomarker": bm,
                "mapped": True,
                "ontology_terms": matched_terms
            })
        else:
            results["unmatched"] += 1
            results["details"].append({
                "trial_id": trial_id,
                "gold_biomarker": bm,
                "mapped": False,
                "ontology_terms": []
            })


# ---------- save ----------
with open(OUTPUT_PATH, "w") as f:
    json.dump(results, f, indent=2)


# ---------- report ----------
print("Oracle mapping finished.")
print(f"Total GS biomarkers (HER2/BRCA only): {results['total_biomarkers']}")
print(f"Matched: {results['matched']}")
print(f"Unmatched: {results['unmatched']}")

if results["total_biomarkers"] > 0:
    print(f"Oracle recall: {results['matched'] / results['total_biomarkers']:.3f}")
else:
    print("No HER2/BRCA biomarkers found in GS.")