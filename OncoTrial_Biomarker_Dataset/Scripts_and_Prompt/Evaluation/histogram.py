import matplotlib.pyplot as plt
import os

# ============================
# Output directory
# ============================

OUT_DIR = "/mnt/data/projects/oncotrialLLM/llm/Personal_data_sets/Results/Evaluation"

# Create folder if not exists
os.makedirs(OUT_DIR, exist_ok=True)

# ============================
# Data
# ============================

methods = ["LLM-only", "Strict", "Lenient"]

precision = [0.275, 0.316, 0.286]
recall = [0.226, 0.097, 0.129]
f1 = [0.248, 0.148, 0.178]

# Columbia Blue
blue = "#1E5AA8"

# ============================
# 1. Precision Plot
# ============================

plt.figure(figsize=(8, 6))
plt.bar(methods, precision, color=blue)
plt.ylim(0, 0.4)
plt.ylabel("Precision", fontsize=14)
plt.title("Precision Comparison", fontsize=16)
plt.grid(axis='y', alpha=0.3)

plt.savefig(os.path.join(OUT_DIR, "precision_comparison.png"), 
            dpi=300, bbox_inches="tight")
plt.close()


# ============================
# 2. Recall Plot
# ============================

plt.figure(figsize=(8, 6))
plt.bar(methods, recall, color=blue)
plt.ylim(0, 0.4)
plt.ylabel("Recall", fontsize=14)
plt.title("Recall Comparison", fontsize=16)
plt.grid(axis='y', alpha=0.3)

plt.savefig(os.path.join(OUT_DIR, "recall_comparison.png"), 
            dpi=300, bbox_inches="tight")
plt.close()


# ============================
# 3. F1-score Plot
# ============================

plt.figure(figsize=(8, 6))
plt.bar(methods, f1, color=blue)
plt.ylim(0, 0.4)
plt.ylabel("F1-score", fontsize=14)
plt.title("F1-score Comparison", fontsize=16)
plt.grid(axis='y', alpha=0.3)

plt.savefig(os.path.join(OUT_DIR, "f1score_comparison.png"),
            dpi=300, bbox_inches="tight")
plt.close()

print(f"Saved all plots to: {OUT_DIR}")