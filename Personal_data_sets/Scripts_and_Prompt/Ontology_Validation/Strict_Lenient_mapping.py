"""
Ontology Mapping Script
------------------------------------------
This script performs ontology mapping for extracted biomarkers using:
1. Normalization (spacing, unicode, alias unification)
2. Canonical term standardization (maps HER2/BRCA variants to NCIt canonical forms)
3. UMLS search (exact + fuzzy)
4. NCIt search (exact + fuzzy)
5. Strict mapping (exact canonical match only)
6. Lenient mapping (fuzzy substring match)

Strict results reflect high-confidence matches.
Lenient results improve coverage for downstream evaluation.
"""

import json
import requests
import time
import os
import re


### ============================================================
###  CONFIG
### ============================================================

INPUT_FILE = "/mnt/data/projects/oncotrialLLM/llm/Personal_data_sets/Results/LLM_extraction/biomarker_aggregate.json"

OUT_STRICT  = "/mnt/data/projects/oncotrialLLM/llm/Personal_data_sets/Results/Ontology_Validation/mapped_strict.json"
OUT_LENIENT = "/mnt/data/projects/oncotrialLLM/llm/Personal_data_sets/Results/Ontology_Validation/mapped_lenient.json"

UMLS_API_KEY = os.getenv("UMLS_API_KEY")
UMLS_VERSION = os.getenv("UMLS_VERSION", "current")



### ============================================================
###  PART 1 — NORMALIZATION + CANONICAL MAPPING
### ============================================================

GENE_ALIASES = {
    "her2": "erbb2",
    "neu": "erbb2",
    "brca-1": "brca1",
    "brca-2": "brca2"
}

# Canonical NCIt-standard terms
CANONICAL_MAP = {
    "her2 amplification": "erbb2 gene amplification",
    "erbb2 amplification": "erbb2 gene amplification",

    "her2 positive": "her2 positive neoplasm",
    "her2-positive": "her2 positive neoplasm",
    "her2 positive expression": "her2 positive neoplasm",
    "her2 positive breast cancer": "her2 positive neoplasm",

    "her2 exon 20 insertion": "erbb2 exon 20 insertion mutation",
    "her2 exon20 insertion": "erbb2 exon 20 insertion mutation",
    "her2 exon 20 insertion mutation": "erbb2 exon 20 insertion mutation",

    "her2 l755s": "erbb2 l755s",
    "her2 l755a": "erbb2 l755a",
    "her2 v777l": "erbb2 v777l",
    "her2 s310f": "erbb2 s310f",
    "her2 v659e": "erbb2 v659e",

    "brca1 mutation": "brca1 gene mutation",
    "brca2 mutation": "brca2 gene mutation",
    "gbrca1 mutation": "brca1 gene mutation",
    "gbrca2 mutation": "brca2 gene mutation",

    "brca1 mutation (germline)": "brca1 gene mutation",
    "brca1 mutation (somatic)": "brca1 gene mutation",
    "brca2 mutation (germline)": "brca2 gene mutation",
    "brca2 mutation (somatic)": "brca2 gene mutation",

    "germline brca mutation": "brca gene mutation",
    "somatic brca mutation": "brca gene mutation",
}


def normalize_biomarker(term):
    """Normalize and canonicalize biomarker terminology."""

    t = term.lower().strip()

    # Remove text inside parentheses
    t = re.sub(r"\(.*?\)", "", t).strip()

    # Normalize unicode dashes
    t = t.replace("–", "-").replace("—", "-")

    # Normalize whitespace
    t = re.sub(r"\s+", " ", t)

    # Normalize gene aliases
    for k, v in GENE_ALIASES.items():
        t = t.replace(k, v)

    # Canonical mapping
    if t in CANONICAL_MAP:
        t = CANONICAL_MAP[t]

    return t.strip()



### ============================================================
###  PART 2 — UMLS + NCIt Search
### ============================================================

def umls_search(term):
    """UMLS search with word-based matching."""
    url = f"https://uts-ws.nlm.nih.gov/rest/search/{UMLS_VERSION}"
    params = {
        "string": term,
        "searchType": "words",
        "apiKey": UMLS_API_KEY
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code != 200:
            return []
        return r.json().get("result", {}).get("results", [])
    except:
        return []


def ncit_search(term):
    """NCIt EVS REST API search."""
    url = "https://api-evsrest.nci.nih.gov/api/v1/concepts/search"
    params = {"keyword": term}

    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code != 200:
            return []
        return r.json().get("concepts", [])
    except:
        return []



### ============================================================
###  PART 3 — STRICT & LENIENT MATCHING
### ============================================================

def strict_match(normalized, umls_results, ncit_results):
    """Strict match: exact canonical match."""

    # UMLS strict
    for r in umls_results:
        if r.get("name", "").lower() == normalized:
            return {
                "ontology": "UMLS",
                "code": r["ui"],
                "preferred_term": r["name"],
                "match_type": "strict"
            }

    # NCIt strict
    for c in ncit_results:
        if c.get("preferredName", "").lower() == normalized:
            return {
                "ontology": "NCIt",
                "code": c["code"],
                "preferred_term": c["preferredName"],
                "match_type": "strict"
            }

    return None


def lenient_match(normalized, umls_results, ncit_results):
    """Lenient match: fuzzy substring."""

    # Fuzzy UMLS
    for r in umls_results:
        name = r.get("name", "").lower()
        if normalized in name or name in normalized:
            return {
                "ontology": "UMLS",
                "code": r["ui"],
                "preferred_term": r["name"],
                "match_type": "lenient"
            }

    # Fuzzy NCIt
    for c in ncit_results:
        name = c.get("preferredName", "").lower()
        if normalized in name or name in normalized:
            return {
                "ontology": "NCIt",
                "code": c["code"],
                "preferred_term": c["preferredName"],
                "match_type": "lenient"
            }

    return None



### ============================================================
###  PART 4 — MAIN PIPELINE
### ============================================================

def main():
    biomarkers = json.load(open(INPUT_FILE))
    mapped_strict = {}
    mapped_lenient = {}

    print(f"\nTotal biomarkers to map: {len(biomarkers)}\n")

    for b in biomarkers:

        normalized = normalize_biomarker(b)
        print(f"\n→ Mapping: \"{b}\" → normalized: \"{normalized}\"")

        umls_results = umls_search(normalized)
        ncit_results = ncit_search(normalized)

        mapped_strict[b] = strict_match(normalized, umls_results, ncit_results)
        mapped_lenient[b] = lenient_match(normalized, umls_results, ncit_results)

        time.sleep(0.25)  # rate limit protection

    json.dump(mapped_strict, open(OUT_STRICT, "w"), indent=2)
    json.dump(mapped_lenient, open(OUT_LENIENT, "w"), indent=2)

    print("\n✓ Strict mapping saved:", OUT_STRICT)
    print("✓ Lenient mapping saved:", OUT_LENIENT)



if __name__ == "__main__":
    main()