# ==============================
# FULL CODE: LINE GRAPH COMPARISON
# ==============================

import matplotlib.pyplot as plt

# ------------------------------
# Step 1: Define Metrics
# ------------------------------
metrics = ['BLEU', 'ROUGE-1', 'ROUGE-L', 'BERTScore', 'NED']

# ------------------------------
# Step 2: Define Scores
# ------------------------------
chatgpt_scores = [0.0134, 0.1684, 0.1263, 0.8582, 0.1520]
your_model_scores = [0.2576, 0.5479, 0.5479, 0.9269, 0.5142]

# ------------------------------
# Step 3: Create Plot
# ------------------------------
plt.figure(figsize=(10,6))

plt.plot(metrics, chatgpt_scores, marker='o', linewidth=2, label='ChatGPT Response')
plt.plot(metrics, your_model_scores, marker='o', linewidth=2, label='Your Model Response')

# ------------------------------
# Step 4: Add Labels & Title
# ------------------------------
plt.xlabel('Evaluation Metrics')
plt.ylabel('Score')
plt.title('Model Comparison Across Metrics')

# ------------------------------
# Step 5: Show Values on Points
# ------------------------------
for i in range(len(metrics)):
    plt.text(metrics[i], chatgpt_scores[i] + 0.02, f"{chatgpt_scores[i]:.2f}", ha='center')
    plt.text(metrics[i], your_model_scores[i] + 0.02, f"{your_model_scores[i]:.2f}", ha='center')

# ------------------------------
# Step 6: Add Grid & Legend
# ------------------------------
plt.grid(True)
plt.legend()

# ------------------------------
# Step 7: Save Graph (Optional)
# ------------------------------
plt.savefig("model_comparison_line_graph.png", dpi=300)

# ------------------------------
# Step 8: Display Graph
# ------------------------------
plt.show()