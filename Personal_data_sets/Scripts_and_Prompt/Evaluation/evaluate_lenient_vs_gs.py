import json
from collections import defaultdict

### =============================
### CONFIG
### =============================
GS_FILE = "/mnt/data/projects/oncotrialLLM/llm/Personal_data_sets/Datasets/Golden_standard/random_trials_annotated.json"
LLM_FILE = "/mnt/data/projects/oncotrialLLM/llm/Personal_data_sets/Results/LLM_extraction/gpt-4.0-turbo_1shot.json"
MAP_FILE = "/mnt/data/projects/oncotrialLLM/llm/Personal_data_sets/Results/Ontology_Validation/mapped_lenient.json"

OUT_FILE = "/mnt/data/projects/oncotrialLLM/llm/Personal_data_sets/Results/Evaluation/lenient_vs_gs.json"

### TARGET BIOMARKERS 
TARGET_BIOMARKERS = [
    "brca", "brca1", "brca2", "gbrca",
    "germline brca", "somatic brca",
    "brca mutation", "pathogenic brca",
    "brca-deficient", "brca deficiency",
    "brca loss", "brca1/2", "brca vus",
    "variant of uncertain significance",
    "her2", "erbb2", "her2+", "her2 positive",
    "her2 positive expression", "her2-positive",
    "her2-expressing", "her2 overexpression",
    "her2 ihc", "ihc 3+", "her2 ihc 1+ or above",
    "her2 amplification", "erbb2 amplification",
    "her2 amplification (ngs)",
    "her2 amplification (ish her2/cep17 ≥ 2.0)",
    "her2 mutation", "her2 mutant", "erbb2 mutant",
    "her2 l755a", "her2 l755s", "her2 v777l",
    "her2 v659e", "her2 s310f",
    "exon 20 insertion", "her2 exon 20 insertion mutation",
    "her2 exon 20 insertion (insyvma)",
    "her2 exon 20 insertion (insgsp)",
    "her2 exon 20 insertion (instgt)",
    "insyvma", "insgsp", "instgt",
    "her2-targeted", "anti-her2"
]

### =============================
### Helpers
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
    t = term.lower()
    return any(key in t for key in TARGET_BIOMARKERS)

### =============================
### Load files
### =============================
gs = json.load(open(GS_FILE))
llm = json.load(open(LLM_FILE))
mapping = json.load(open(MAP_FILE))

llm_dict = {x["nct_id"]: x for x in llm}

### =============================
### Evaluation counters
### =============================
TP = FP = FN = 0
per_trial_result = {}

### =============================
### Main evaluation loop
### =============================
for nct_id, item in gs.items():

    # GS biomarkers
    gs_bm = flatten(item.get("inclusion_biomarker", [])) + \
            flatten(item.get("exclusion_biomarker", []))
    gs_bm = [x.lower() for x in gs_bm if is_target(x)]
    gs_set = set(gs_bm)

    # LLM extraction
    llm_item = llm_dict.get(nct_id, {})
    extracted = flatten(llm_item.get("inclusion_biomarker", [])) + \
                flatten(llm_item.get("exclusion_biomarker", []))
    extracted = [x.lower() for x in extracted if is_target(x)]

    # Mapping results
    mapped_set = set()
    for term in extracted:
        mapped_entry = mapping.get(term)
        if mapped_entry and mapped_entry.get("mapped", True) is not None:
            mapped_set.add(term)

    # Compute metrics
    tp = len(gs_set & mapped_set)
    fp = len(mapped_set - gs_set)
    fn = len(gs_set - mapped_set)

    TP += tp
    FP += fp
    FN += fn

    per_trial_result[nct_id] = {
        "GS": list(gs_set),
        "LLM+Mapped": list(mapped_set),
        "TP": tp, "FP": fp, "FN": fn
    }

### =============================
### Final metrics
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
print("Saved lenient vs GS evaluation →", OUT_FILE)
print(f"P={precision:.3f}, R={recall:.3f}, F1={f1:.3f}")