import os
import csv
import json

# === Corrected CSV path ===
CSV_PATH = r"C:/Users/palac/Documents/Oilpalms/scripts/tiles/deduplicated_detections.csv"
OUTPUT_PATH = r"C:/Users/palac/Documents/Oilpalms/scripts/output/detection_geojson.geojson"

features = []

with open(CSV_PATH, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        class_name = row['Class']
        x = float(row['X'])
        y = float(row['Y'])

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [x, y]  # Note: not actual lat/lon
            },
            "properties": {
                "class": class_name,
                "confidence": float(row['Conf']),
                "tile": row['Tile']
            }
        }
        features.append(feature)

geojson = {
    "type": "FeatureCollection",
    "features": features
}

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
with open(OUTPUT_PATH, 'w') as f:
    json.dump(geojson, f, indent=2)

print(f"🌍 GeoJSON export completed: {OUTPUT_PATH}")
