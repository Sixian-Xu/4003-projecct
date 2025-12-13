import json

INPUT = "/mnt/data/projects/oncotrialLLM/llm/Personal_data_sets/Datasets/Raw_data/random_trials_.json"
OUTPUT = "/mnt/data/projects/oncotrialLLM/llm/Personal_data_sets/Datasets/Raw_data/random_trials.json"

def main():
    with open(INPUT, "r") as f:
        data = json.load(f)

    out = {}

    for nct_id, entry in data.items():
        if "document" in entry:
            out[nct_id] = {"document": entry["document"]}
        else:
            print(f"Warning: No document in {nct_id}")

    with open(OUTPUT, "w") as f:
        json.dump(out, f, indent=2)

    print("Converted file saved to:")
    print(OUTPUT)
    print("Total trials:", len(out))


if __name__ == "__main__":
    main()