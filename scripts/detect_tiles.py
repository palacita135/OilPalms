import os
import glob
import csv
from ultralytics import YOLO
from pathlib import Path
from tqdm import tqdm

# Updated TILE_DIR to reflect actual saved tiles directory
TILE_DIR = r"C:/Users/palac/Documents/Oilpalms/scripts/tiles"
MODEL_PATH = r"C:/Users/palac/Documents/Oilpalms/model/best.pt"
OUTPUT_CSV = os.path.join(TILE_DIR, "detections.csv")

CLASS_NAMES = ['Oil Palm', 'VOP']

# Ensure model exists
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"❌ Model file not found: {MODEL_PATH}")

# Get tile images
tile_paths = glob.glob(os.path.join(TILE_DIR, "*.jpg"))
if not tile_paths:
    raise FileNotFoundError(f"❌ No tile images found in {TILE_DIR}")

# Load model
model = YOLO(MODEL_PATH)

# Prepare output
with open(OUTPUT_CSV, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Tile", "Class", "Conf", "X", "Y", "W", "H"])

    for tile_path in tqdm(tile_paths, desc="🧠 Detecting tiles"):
        tile_name = Path(tile_path).name

        try:
            x_offset = int(tile_name.split("_")[-2])
            y_offset = int(tile_name.split("_")[-1].split(".")[0])
        except (IndexError, ValueError):
            print(f"⚠️ Skipping file with unexpected name format: {tile_name}")
            continue

        results = model(tile_path)[0]
        for box in results.boxes:
            cls = int(box.cls.item())
            conf = float(box.conf.item())
            x_center, y_center, w, h = map(float, box.xywh[0])

            abs_x = x_center + x_offset
            abs_y = y_center + y_offset

            writer.writerow([tile_name, CLASS_NAMES[cls], round(conf, 3), abs_x, abs_y, w, h])

print(f"\n✅ Detection CSV saved to {OUTPUT_CSV}")
