# 4003_Symbolic_AI_Healthcare_project

OncoTrial-Biomarker-Dataset is a curated dataset of oncology clinical trial eligibility texts with gold-standard annotations for HER2/ERBB2 and BRCA1/2 biomarkers, designed for biomarker extraction and ontology mapping research.
The dataset focuses on HER2/ERBB2 and BRCA1/BRCA2 biomarkers and includes raw eligibility text, manually curated gold-standard annotations, and evaluation outputs from large language model (LLM)–based extraction and ontology mapping pipelines.

## Data Source:
https://github.com/BIMSBbioinfo/oncotrialLLM/blob/main/llm/data/interim/random_trials_annotated.json
	-	Eligibility texts were obtained from publicly available oncology clinical trials (ClinicalTrials.gov).
	-	Trials were randomly sampled and filtered to include oncology-related studies.
	-	All data are public, de-identified, and contain no patient-level information.
	-	Annotation Range: HER2 / BRCA

## Gold-Standard Annotation:
```json
{
  "document": "full eligibility text",
  "inclusion_biomarker": [["HER2 positive"]],
  "exclusion_biomarker": [["BRCA1 mutation"]]
}
```

## Evaluation Outputs:
This repository includes multiple evaluation artifacts:
	- LLM-based extraction evaluation
		- Sentence-level 1-shot extraction using GPT-based models
	- Ontology mapping evaluation
		- Strict and lenient string-based matching
	- Oracle ontology mapping
		- Gold-standard biomarkers mapped directly to ontology terms to estimate an upper bound on mapping performance

## Dataset Structure:
```text
OncoTrial_Biomarker_Dataset/
├── Datasets/
│   ├── Raw_data/
│   │   └── random_trials.json
│   │      # Raw eligibility text of oncology clinical trials (unannotated input data)
│   ├── Golden_standard/
│   │   └── random_trials_annotated.json
│   │      # Gold-standard annotations for HER2/BRCA biomarkers (inclusion/exclusion)
│
├── Results/
│   ├── Evaluation/
│   │   ├── llm_extraction_eval.json
│   │   │   # Performance of LLM-based biomarker extraction against gold standard
│   │   ├── strict_mapping_vs_gs.json
│   │   │   # End-to-end evaluation using strict ontology string matching
│   │   ├── lenient_vs_gs.json
│   │   │   # End-to-end evaluation using lenient ontology string matching
│   │   ├── oracle_mapping_results.json
│   │   │   # Oracle ontology mapping results using gold-standard biomarkers
│   │   ├── precision_comparison.png
│   │   │   # Precision comparison across extraction and mapping strategies
│   │   ├── recall_comparison.png
│   │   │   # Recall comparison across extraction and mapping strategies
│   │   └── f1score_comparison.png
│   │       # F1-score comparison across extraction and mapping strategies
│   │
│   ├── LLM_extraction/
│   │   ├── gpt-4.0-turbo_1shot.json
│   │   │   # Raw outputs of GPT-4.0-turbo 1-shot biomarker extraction
│   │   └── biomarker_aggregate.json
│   │       # Aggregated biomarker expressions extracted from all trials
│   │
│   └── Ontology_Validation/
│       ├── mapped_strict.json
│       │   # Ontology mapping results using strict matching rules
│       └── mapped_lenient.json
│           # Ontology mapping results using lenient matching rules
│
├── Scripts_and_Prompt/
│   ├── Evaluation/
│   │   # Scripts for evaluating extraction, mapping, and oracle experiments
│   ├── LLM_extraction/
│   │   # Scripts and prompts for LLM-based biomarker extraction
│   └── Ontology_Validation/
│       # Scripts for ontology construction, normalization, and mapping
│
└── README.md
    # Documentation describing dataset scope, structure, and experimental setup




 
