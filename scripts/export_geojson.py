import os
import csv
import json
from PIL import Image

# === Configurable paths ===
CSV_PATH = r"C:/Users/palac/Documents/Oilpalms/scripts/tiles/deduplicated_detections.csv"
IMAGE_PATH = r"C:/Users/palac/Documents/Oilpalms/scripts/output/merged_result.jpg"
OUTPUT_PATH = r"C:/Users/palac/Documents/Oilpalms/scripts/output/detection_geojson_corrected.geojson"

# === Load image to get width and height ===
image = Image.open(IMAGE_PATH)
image_width, image_height = image.size
print(f"🖼️ Loaded image with dimensions: {image_width} x {image_height}")

features = []

# === Read and transform detection data ===
with open(CSV_PATH, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        class_name = row['Class']
        x = float(row['X'])
        y = float(row['Y'])

        # Apply 180° rotation (mirror X and Y)
        corrected_x = x
        corrected_y = image_height - y

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [corrected_x, corrected_y]
            },
            "properties": {
                "class": class_name,
                "confidence": float(row['Conf']),
                "tile": row['Tile']
            }
        }
        features.append(feature)

# === Save to GeoJSON ===
geojson = {
    "type": "FeatureCollection",
    "features": features
}

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
with open(OUTPUT_PATH, 'w') as f:
    json.dump(geojson, f, indent=2)

print(f"✅ Rotated + flipped GeoJSON saved to: {OUTPUT_PATH}")
