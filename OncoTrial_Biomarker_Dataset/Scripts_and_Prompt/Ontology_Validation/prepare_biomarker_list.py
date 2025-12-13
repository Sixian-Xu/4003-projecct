import json

INPUT = "/mnt/data/projects/oncotrialLLM/llm/Personal_data_sets/Results/LLM_extraction/gpt-3.5-turbo_1shot.json"

# For evaluation
OUTPUT_TRIAL_LEVEL = (
    "/mnt/data/projects/oncotrialLLM/llm/Personal_data_sets/Results/LLM_extraction/"
    "biomarkers_by_trial.json"
)

# For mapping
OUTPUT_UNIQUE = (
    "/mnt/data/projects/oncotrialLLM/llm/Personal_data_sets/Results/LLM_extraction/"
    "biomarker_list_all_unique.json"
)


def extract_biomarkers(entry):
    """Extract biomarkers from inclusion + exclusion fields."""
    biomarkers = []

    for group in entry.get("inclusion_biomarker", []):
        biomarkers.extend(group if isinstance(group, list) else [group])

    for group in entry.get("exclusion_biomarker", []):
        biomarkers.extend(group if isinstance(group, list) else [group])

    return biomarkers


def main():
    with open(INPUT, "r") as f:
        data = json.load(f)

    predicted = data["results"][0]["Precited"]

    trial_level_dict = {}  # e.g., { "trial_0": [...], "trial_1": [...] }
    unique_set = set()

    for idx, entry in enumerate(predicted):
        trial_id = f"trial_{idx}"
        biomarkers = extract_biomarkers(entry)

        trial_level_dict[trial_id] = biomarkers

        for b in biomarkers:
            unique_set.add(b)

    # --- Save trial-level biomarker dictionary ---
    with open(OUTPUT_TRIAL_LEVEL, "w") as f:
        json.dump(trial_level_dict, f, indent=2)

    # --- Save unique biomarker list ---
    unique_list = sorted(list(unique_set))
    with open(OUTPUT_UNIQUE, "w") as f:
        json.dump(unique_list, f, indent=2)

    print(f"Saved trial-level biomarker list → {OUTPUT_TRIAL_LEVEL}")
    print(f"Saved unique biomarker list → {OUTPUT_UNIQUE}")
    print(f"Total unique biomarkers: {len(unique_list)}")


if __name__ == "__main__":
    main()