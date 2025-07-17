import csv
import numpy as np
from sklearn.cluster import DBSCAN

INPUT_CSV = r"C:/Users/palac/Documents/OilPalms/scripts/tiles/detections.csv"
OUTPUT_CSV = r"C:/Users/palac/Documents/OilPalms/scripts/tiles/deduplicated_detections.csv"

# DBSCAN params
EPS = 30  # high-res : 10-15 ; low-res : 20-30 ; dense : 8-12
MIN_SAMPLES = 1  # allow single detections to be kept

# Load detections
detections = []
coords = []

with open(INPUT_CSV, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        x = float(row['X'])
        y = float(row['Y'])

        coords.append([x, y])
        detections.append({
            'Tile': row['Tile'],
            'Class': row['Class'],
            'Conf': float(row['Conf']),
            'X': x,
            'Y': y,
            'W': float(row['W']),
            'H': float(row['H'])
        })

coords = np.array(coords)
db = DBSCAN(eps=EPS, min_samples=MIN_SAMPLES).fit(coords)
labels = db.labels_

# Group by cluster label
clustered = {}
for label, det in zip(labels, detections):
    clustered.setdefault(label, []).append(det)

# Keep top-confidence detection per cluster
deduped = []
for cluster_id, group in clustered.items():
    best = max(group, key=lambda d: d['Conf'])
    deduped.append(best)

# Write output
with open(OUTPUT_CSV, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=["Tile", "Class", "Conf", "X", "Y", "W", "H"])
    writer.writeheader()
    for det in deduped:
        writer.writerow(det)

print(f"✅ DBSCAN deduplicated detections saved to: {OUTPUT_CSV}")
print(f"📦 Original: {len(detections)} → Deduplicated: {len(deduped)}")
