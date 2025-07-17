import os
import csv
from glob import glob
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

# === CONFIGURATION ===
TILE_DIR = r"C:/Users/palac/Documents/OilPalms/scripts/tiles"
DETECTIONS_CSV = os.path.join(TILE_DIR, "deduplicated_detections.csv")  # ✅ using deduplicated CSV
OUTPUT_IMAGE = os.path.join(os.path.dirname(TILE_DIR), "output", "merged_result.jpg")

os.makedirs(os.path.dirname(OUTPUT_IMAGE), exist_ok=True)

# === Step 1: Load all tiles and calculate canvas size ===
print("🧩 Step 2.5: Merging tiles with detection dots...")

tiles = []
max_x, max_y = 0, 0
tile_w, tile_h = 0, 0

for tile_path in glob(os.path.join(TILE_DIR, "*.jpg")):
    tile_name = os.path.basename(tile_path)
    parts = tile_name.replace(".jpg", "").split("_")

    try:
        x_offset = int(parts[-2])
        y_offset = int(parts[-1])
    except ValueError:
        print(f"⚠️ Skipped malformed tile name: {tile_name}")
        continue

    img = Image.open(tile_path)
    tile_w, tile_h = img.size

    max_x = max(max_x, x_offset + tile_w)
    max_y = max(max_y, y_offset + tile_h)

    tiles.append((img, x_offset, y_offset))

print(f"🖼️ Creating canvas: {max_x} x {max_y}")
merged = Image.new("RGB", (max_x, max_y))

# === Step 2: Paste tiles ===
for img, x, y in tqdm(tiles, desc="🧱 Pasting tiles"):
    merged.paste(img, (x, y))

# === Step 3: Draw detection dots ===
dot_count = 0
if os.path.exists(DETECTIONS_CSV):
    draw = ImageDraw.Draw(merged)

    with open(DETECTIONS_CSV, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            x = float(row['X'])
            y = float(row['Y'])
            class_name = row['Class'].lower()

            radius = 12
            color = "red" if class_name == "oil palm" else "blue"
            draw.ellipse([(x - radius, y - radius), (x + radius, y + radius)], fill=color, outline=color)
            dot_count += 1

    print(f"✅ {dot_count} detection dots drawn from: {DETECTIONS_CSV}")
else:
    print("⚠️ No deduplicated_detections.csv found. Skipping dot drawing.")

# === Step 4: Overlay dot count text ===
text = f"Detected Oil Palms: {dot_count}"
font = ImageFont.load_default()
draw.text((10, 10), text, fill="yellow", font=font)

# === Step 5: Save final image ===
merged.save(OUTPUT_IMAGE)
print(f"✅ Merged image saved to: {OUTPUT_IMAGE}")
