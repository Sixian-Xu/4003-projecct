import json
from collections import defaultdict

### =============================
### CONFIG
### =============================
GS_FILE = "/mnt/data/projects/oncotrialLLM/llm/Personal_data_sets/Datasets/Golden_standard/random_trials_annotated.json" 
LLM_FILE = "/mnt/data/projects/oncotrialLLM/llm/Personal_data_sets/Results/LLM_extraction/gpt-4.0-turbo_1shot.json"
STRICT_MAP_FILE = "/mnt/data/projects/oncotrialLLM/llm/Personal_data_sets/Results/Ontology_Validation/mapped_strict.json"

OUT_FILE = "/mnt/data/projects/oncotrialLLM/llm/Personal_data_sets/Results/Evaluation/strict_mapping_vs_gs.json"


### ===== TARGET BIOMARKERS =====

TARGET_BIOMARKERS = [
    # ===== BRCA GENERAL =====
    "brca","brca1","brca2","gbrca","brca mutation","pathogenic brca",
    "germline brca","somatic brca","brca-deficient","brca deficiency",
    "brca loss","brca1/2","brca vus","variant of uncertain significance",

    # ===== BRCA SPECIFIC =====
    "brca1 mutation (germline)", "brca1 mutation (somatic)",
    "brca2 mutation (germline)", "brca2 mutation (somatic)",
    "brca1 vus", "brca2 vus", "gbrca1 mutation", "gbrca2 mutation",

    # ===== HER2 / ERBB2 GENERAL =====
    "her2","erbb2","her2+","her2 positive","her2 positive expression",
    "her2-positive","her2-expressing","her2 overexpression",
    "ihc 3+","her2 ihc","her2 ihc 1+ or above",

    # ===== HER2 AMPLIFICATION =====
    "her2 amplification","erbb2 amplification",
    "her2 amplification (ngs)",
    "her2 amplification (ish her2/cep17 ≥ 2.0)",

    # ===== HER2 MUTATIONS =====
    "her2 mutation", "her2 mutant", "erbb2 mutant",
    "her2 l755a","her2 l755s","her2 v777l",
    "her2 v659e","her2 s310f",

    # ===== EXON 20 INSERTIONS =====
    "exon 20 insertion","her2 exon 20 insertion mutation",
    "her2 exon 20 insertion (insyvma)",
    "her2 exon 20 insertion (insgsp)",
    "her2 exon 20 insertion (instgt)",
    "insyvma","insgsp","instgt",

    # ===== HER2 TARGETed =====
    "her2-targeted","anti-her2"
]


### =============================
### HELPER FUNCTIONS
### =============================

def flatten(lst):
    out = []
    for x in lst:
        if isinstance(x, list):
            out.extend(x)
        else:
            out.append(x)
    return out

def is_target(term):
    """Check if term belongs to BRCA/HER2 family."""
    t = term.lower()
    return any(key in t for key in TARGET_BIOMARKERS)


### =============================
### LOAD DATA
### =============================
gs = json.load(open(GS_FILE))
llm = json.load(open(LLM_FILE))
strict_map = json.load(open(STRICT_MAP_FILE))

llm_dict = {x["nct_id"]: x for x in llm}


### =============================
### EVALUATION COUNTERS
### =============================
TP = FP = FN = 0
per_trial_result = {}

### =============================
### MAIN LOOP
### =============================
for nct_id, item in gs.items():

    gs_bm = flatten(item.get("inclusion_biomarker", [])) + \
            flatten(item.get("exclusion_biomarker", []))
    gs_bm = [x.lower() for x in gs_bm if is_target(x)]
    gs_set = set(gs_bm)

    llm_item = llm_dict.get(nct_id, {})
    llm_bm = flatten(llm_item.get("inclusion_biomarker", [])) + \
             flatten(llm_item.get("exclusion_biomarker", []))

    # Keep only biomarkers that had a strict mapping (non-null)
    llm_strict_kept = []
    for bm in llm_bm:
        b = bm.lower()
        if b in strict_map and strict_map[b] is not None and is_target(b):
            llm_strict_kept.append(b)

    llm_set = set(llm_strict_kept)

    # Metrics
    tp = len(gs_set & llm_set)
    fp = len(llm_set - gs_set)
    fn = len(gs_set - llm_set)

    TP += tp
    FP += fp
    FN += fn

    per_trial_result[nct_id] = {
        "gs": list(gs_set),
        "llm_strict": list(llm_set),
        "TP": tp,
        "FP": fp,
        "FN": fn
    }


### =============================
### METRICS
### =============================
precision = TP / (TP + FP) if TP + FP else 0
recall = TP / (TP + FN) if TP + FN else 0
f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0

summary = {
    "TP": TP,
    "FP": FP,
    "FN": FN,
    "Precision": precision,
    "Recall": recall,
    "F1": f1,
    "per_trial": per_trial_result
}

json.dump(summary, open(OUT_FILE, "w"), indent=2)
print("Saved evaluation →", OUT_FILE)
print(f"P={precision:.3f}, R={recall:.3f}, F1={f1:.3f}")