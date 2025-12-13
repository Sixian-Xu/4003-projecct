import json
from openai import OpenAI

client = OpenAI()

PROMPT_FILE = "/mnt/data/projects/oncotrialLLM/llm/Personal_data_sets/Scripts_and_Prompt/LLM_extraction/biomarker_extraction_1shot.txt"
INPUT_FILE = "/mnt/data/projects/oncotrialLLM/llm/Personal_data_sets/Datasets/Raw_data/random_trials.json"
OUTPUT_FILE = "/mnt/data/projects/oncotrialLLM/llm/Personal_data_sets/Results/LLM_extraction/gpt-4.0-turbo_1shot.json"


def load_prompt():
    with open(PROMPT_FILE, "r") as f:
        return f.read()


def extract_structured(text):
    prompt = load_prompt().replace("{{trial_text}}", text)

    resp = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )

    return resp.choices[0].message.content


def main():
    data = json.load(open(INPUT_FILE))

    results = []

    for nct_id, entry in data.items():
        print(f"Extracting → {nct_id}")

        text = entry.get("document", "")
        raw_output = extract_structured(text)

        # Parse JSON output
        try:
            parsed = json.loads(raw_output)
        except:
            parsed = {
                "inclusion_biomarker": [],
                "exclusion_biomarker": []
            }

        results.append({
            "nct_id": nct_id,
            "inclusion_biomarker": parsed.get("inclusion_biomarker", []),
            "exclusion_biomarker": parsed.get("exclusion_biomarker", [])
        })

    json.dump(results, open(OUTPUT_FILE, "w"), indent=2)
    print("Saved →", OUTPUT_FILE)


if __name__ == "__main__":
    main()