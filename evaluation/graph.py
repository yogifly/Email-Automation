import matplotlib.pyplot as plt
import numpy as np

# Metrics
metrics = ['BLEU', 'ROUGE-1', 'ROUGE-L', 'BERTScore', 'NED']

# Values
chatgpt_scores = [0.0134, 0.1684, 0.1263, 0.8582, 0.1520]
your_model_scores = [0.2576, 0.5479, 0.5479, 0.9269, 0.5142]

# X-axis positions
x = np.arange(len(metrics))
width = 0.35

# Plot
plt.figure(figsize=(10,6))
plt.bar(x - width/2, chatgpt_scores, width, label='ChatGPT Response')
plt.bar(x + width/2, your_model_scores, width, label='Your Model Response')

# Labels & Title
plt.xlabel('Evaluation Metrics')
plt.ylabel('Score')
plt.title('Comparison of Email Response Quality')
plt.xticks(x, metrics)
plt.legend()

# Show values on bars
for i in range(len(metrics)):
    plt.text(x[i] - width/2, chatgpt_scores[i] + 0.01, f"{chatgpt_scores[i]:.2f}", ha='center')
    plt.text(x[i] + width/2, your_model_scores[i] + 0.01, f"{your_model_scores[i]:.2f}", ha='center')

plt.tight_layout()
plt.show()