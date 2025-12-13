import json
from collections import Counter

INPUT = "/mnt/data/projects/oncotrialLLM/llm/Personal_data_sets/Results/LLM_extraction/gpt-4.0-turbo_1shot.json"
OUTPUT = "/mnt/data/projects/oncotrialLLM/llm/Personal_data_sets/Results/LLM_extraction/biomarker_aggregate.json"

data = json.load(open(INPUT))

counter = Counter()

for item in data:
    for x in item["inclusion_biomarker"]:
        counter[x.strip().lower()] += 1
    for x in item["exclusion_biomarker"]:
        counter[x.strip().lower()] += 1

json.dump(counter, open(OUTPUT, "w"), indent=2)
print("Saved:", OUTPUT)