import os
import glob
from tqdm import tqdm
from PIL import Image, ImageFile
import piexif
import rasterio
from rasterio.windows import Window
from concurrent.futures import ThreadPoolExecutor
import csv

# === PIL Decompression Bomb Override ===
Image.MAX_IMAGE_PIXELS = None
ImageFile.LOAD_TRUNCATED_IMAGES = True

# === CONFIGURATION ===
INPUT_FOLDER = r"C:/Users/palac/Documents/Oilpalms/input"
OUTPUT_DIR = r"C:/Users/palac/Documents/Oilpalms/scripts/tiles"
CSV_PATH = os.path.join(OUTPUT_DIR, "tile_geolocation.csv")
TILE_SIZE = 640
MAX_WORKERS = 6
SAVE_GEO_CSV = True

os.makedirs(OUTPUT_DIR, exist_ok=True)

# === SUPPORTED FORMATS ===
SUPPORTED_EXTS = ['*.jpg', '*.jpeg', '*.png', '*.tif', '*.tiff']

# === FIND INPUT IMAGES ===
image_paths = []
for ext in SUPPORTED_EXTS:
    image_paths.extend(glob.glob(os.path.join(INPUT_FOLDER, ext)))

print(f"📷 Found {len(image_paths)} input image(s)...")

# === Optional: Geolocation CSV ===
geo_csv_rows = []

# === TILE IMAGE ===
def tile_image(image_path):
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    tile_count = 0

    try:
        if image_path.lower().endswith((".tif", ".tiff")):
            # --- Use rasterio for GeoTIFF ---
            with rasterio.open(image_path) as src:
                width, height = src.width, src.height
                print(f"🌍 GeoTIFF detected: {base_name} ({width}x{height})")

                for y in range(0, height, TILE_SIZE):
                    for x in range(0, width, TILE_SIZE):
                        window = Window(x, y, TILE_SIZE, TILE_SIZE)
                        transform = src.window_transform(window)
                        tile = src.read([1, 2, 3], window=window)  # RGB only
                        tile_img = Image.fromarray(tile.transpose(1, 2, 0)).convert("RGB")

                        tile_name = f"{base_name}_tile_{x}_{y}.jpg"
                        tile_path = os.path.join(OUTPUT_DIR, tile_name)
                        tile_img.save(tile_path, "JPEG")

                        if SAVE_GEO_CSV:
                            lon, lat = transform * (0, 0)
                            geo_csv_rows.append({
                                "Tile": tile_name,
                                "TopLeft_Lon": lon,
                                "TopLeft_Lat": lat
                            })

                        tile_count += 1
                return tile_count

        else:
            # --- Use PIL for non-GeoTIFF ---
            img = Image.open(image_path).convert("RGB")
            width, height = img.size

            try:
                exif_data = piexif.load(img.info.get("exif", b""))
            except Exception:
                exif_data = None
                print(f"⚠️ No EXIF: {base_name}")

            for y in range(0, height, TILE_SIZE):
                for x in range(0, width, TILE_SIZE):
                    box = (x, y, x + TILE_SIZE, y + TILE_SIZE)
                    tile = img.crop(box)

                    tile_name = f"{base_name}_tile_{x}_{y}.jpg"
                    tile_path = os.path.join(OUTPUT_DIR, tile_name)

                    if exif_data:
                        tile.save(tile_path, "JPEG", exif=piexif.dump(exif_data))
                    else:
                        tile.save(tile_path, "JPEG")

                    tile_count += 1
            return tile_count

    except Exception as e:
        print(f"❌ Error processing {base_name}: {e}")
        return 0

# === MULTI-THREADED EXECUTION ===
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    results = list(tqdm(executor.map(tile_image, image_paths), total=len(image_paths), desc="🧩 Tiling with ETA"))

total_tiles = sum(results)
print(f"\n🎉 Done. Total tiles saved: {total_tiles}")

# === OPTIONAL: Save geolocation CSV ===
if SAVE_GEO_CSV and geo_csv_rows:
    with open(CSV_PATH, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Tile", "TopLeft_Lon", "TopLeft_Lat"])
        writer.writeheader()
        writer.writerows(geo_csv_rows)
    print(f"📍 Geo-location CSV saved: {CSV_PATH}")
