import csv
import numpy as np
import matplotlib.pyplot as plt


#Load CSV data
filename = "county_happiness_with_reddit_feedback_normalized.csv" 
data = []

with open(filename, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            data.append({
                "county": row["County"],
                "WeightedSentiment": float(row["WeightedSentiment"]),
                "WeightedNetwork": float(row["WeightedNetwork"]),
                "WeightedFeedback": float(row["WeightedFeedback"]),
                "HappinessScore": float(row["HappinessScore"]),
                "Cluster": int(row["Cluster"]),
                "ClusterLabel": row["ClusterLabel"]
            })
        except ValueError:
            continue  # skip malformed rows

if not data:
    raise ValueError("No valid rows found in CSV.")

# Visualization
plt.figure(figsize=(12, 8))
colors = ["#e74c3c", "#2ecc71", "#3498db", "#f1c40f"]  # up to 4 clusters

# Get unique clusters
unique_clusters = sorted(set(d["Cluster"] for d in data))

for cluster in unique_clusters:
    cluster_points = [d for d in data if d["Cluster"] == cluster]
    x = [d["HappinessScore"] for d in cluster_points]
    y = [d["WeightedNetwork"] for d in cluster_points]
    sizes = [d["HappinessScore"] * 5 for d in cluster_points]  # scale dot sizes
    labels_ = [d["county"] for d in cluster_points]
    
    # Use ClusterLabel for legend
    cluster_label = cluster_points[0]["ClusterLabel"] if cluster_points else f"Cluster {cluster}"

    plt.scatter(x, y, s=sizes, color=colors[cluster % len(colors)], alpha=0.6, label=cluster_label)
    
    # Annotate counties
    for i, name in enumerate(labels_):
        plt.text(x[i] + 0.5, y[i] + 0.5, name, fontsize=8)

plt.title("Texas County Happiness Clusters (HappinessScore vs Network Reliability)")
plt.xlabel("HappinessScore")
plt.ylabel("Weighted Network Reliability")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("texas_happiness_clusters.png", dpi=300)
plt.show()


