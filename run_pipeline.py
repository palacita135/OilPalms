import os
import subprocess
import sys
from glob import glob
import webbrowser
from datetime import datetime
import shutil
from PIL import Image

# === CONFIGURATION ===
PYTHON_EXEC = sys.executable
PROJECT_ROOT = r"C:/Users/palac/Documents/OilPalms"

INPUT_DIR     = os.path.join(PROJECT_ROOT, "input")
SCRIPTS_DIR   = os.path.join(PROJECT_ROOT, "scripts")
OUTPUT_DIR    = os.path.join(SCRIPTS_DIR, "output")
TILE_DIR      = os.path.join(SCRIPTS_DIR, "tiles")
MERGED_PATH   = os.path.join(OUTPUT_DIR, "merged_result.jpg")
REPORT_BASE   = os.path.join(PROJECT_ROOT, "oil_palm_report.html")

# === Script Paths ===
tile_script    = os.path.join(SCRIPTS_DIR, "tile_image.py")
detect_script  = os.path.join(SCRIPTS_DIR, "detect_tiles.py")
dedup_script   = os.path.join(SCRIPTS_DIR, "deduplicate_detections.py")
merge_script   = os.path.join(SCRIPTS_DIR, "merge_tiles.py")
inject_script  = os.path.join(SCRIPTS_DIR, "inject_exif_to_merged.py")
export_script  = os.path.join(SCRIPTS_DIR, "export_geojson.py")
report_script  = os.path.join(SCRIPTS_DIR, "generate_report.py")

# === Timestamped HTML report path ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
report_output = os.path.join(PROJECT_ROOT, f"oil_palm_report_{timestamp}.html")

# === Scan for first image with EXIF ===
def has_exif(path):
    try:
        return Image.open(path)._getexif() is not None
    except Exception:
        return False

supported_exts = ["*.jpg", "*.jpeg", "*.png", "*.tif", "*.tiff"]
all_images = []
for ext in supported_exts:
    all_images.extend(glob(os.path.join(INPUT_DIR, ext)))

jpg_files = [img for img in sorted(all_images) if has_exif(img)]
if jpg_files:
    os.environ["GPS_EXIF_SOURCE"] = jpg_files[0]
    print(f"📂 Using original EXIF source: {jpg_files[0]}")
else:
    print("⚠️ No EXIF metadata found in any input. GPS embedding will be skipped.")
    os.environ["GPS_EXIF_SOURCE"] = ""  # Explicitly unset

# === Step 1: Tiling ===
print("🔪 Step 1: Tiling image...")
if subprocess.call([PYTHON_EXEC, tile_script]) != 0:
    print("❌ Failed at tile_image.py")
    sys.exit(1)

# === Step 2: Detection ===
print("\n🧠 Step 2: Detecting oil palms in tiles...")
if subprocess.call([PYTHON_EXEC, detect_script]) != 0:
    print("❌ Failed at detect_tiles.py")
    sys.exit(2)

# === Step 2.6: Deduplication (DBSCAN) ===
print("\n📌 Step 2.6: Deduplicating detections...")
if subprocess.call([PYTHON_EXEC, dedup_script]) != 0:
    print("❌ Failed at deduplicate_detections.py")
    sys.exit(26)

# === Step 2.7: Merge Tiles with Dots ===
print("\n🧩 Step 2.7: Merging tiles with detection dots...")
if subprocess.call([PYTHON_EXEC, merge_script]) != 0:
    print("❌ Failed at merge_tiles.py")
    sys.exit(27)

# === Step 3: Inject EXIF (if available) ===
print("\n📍 Step 3: Embedding GPS metadata...")
if os.environ.get("GPS_EXIF_SOURCE") and os.path.exists(MERGED_PATH):
    ret3 = subprocess.call([PYTHON_EXEC, inject_script], env=os.environ.copy())
    if ret3 != 0:
        print("❌ Failed at inject_exif_to_merged.py")
        sys.exit(3)
elif not os.environ.get("GPS_EXIF_SOURCE"):
    print("⚠️ Skipped EXIF injection (no source available).")
else:
    print(f"❌ Merged image not found at: {MERGED_PATH}")
    sys.exit(4)

# === Step 4: Export GeoJSON ===
print("\n🌍 Step 4: Exporting GeoJSON...")
if subprocess.call([PYTHON_EXEC, export_script]) != 0:
    print("❌ Failed at export_geojson.py")
    sys.exit(4)

# === Step 5: Generate HTML Report ===
print("\n📊 Step 5: Generating HTML report...")
if subprocess.call([PYTHON_EXEC, report_script]) != 0:
    print("❌ Failed at generate_report.py")
    sys.exit(5)

# === Step 6: Rename report with timestamp ===
if os.path.exists(REPORT_BASE):
    shutil.copyfile(REPORT_BASE, report_output)
    print(f"✅ HTML Report saved as: {report_output}")

    # === Step 7: Open the report ===
    print("\n🌐 Opening HTML report...")
    webbrowser.open(f"file:///{report_output.replace(os.sep, '/')}")
else:
    print(f"❌ Report not found at: {REPORT_BASE}")

# === Final Summary ===
print("\n✅ All done! Check the output folder for results:")
print("🖼️ merged_with_exif.jpg")
print("📄 deduplicated_detections.csv")
print("🌍 detection_geojson.geojson")
print(f"📊 {os.path.basename(report_output)}")
