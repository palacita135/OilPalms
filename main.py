import os
import sys
import subprocess
import argparse
import shutil
import webbrowser
from glob import glob
from datetime import datetime
from PIL import Image

# === CONFIG ===
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
OUTPUT_DIR = os.path.join(SCRIPTS_DIR, "output")
TILE_DIR = os.path.join(SCRIPTS_DIR, "tiles")
REPORT_BASE = os.path.join(BASE_DIR, "oil_palm_report.html")
MERGED_PATH = os.path.join(OUTPUT_DIR, "merged_result.jpg")
PYTHON_EXEC = sys.executable

# === Script Paths ===
scripts = {
    "tile":      os.path.join(SCRIPTS_DIR, "tile_image.py"),
    "detect":    os.path.join(SCRIPTS_DIR, "detect_tiles.py"),
    "dedupe":    os.path.join(SCRIPTS_DIR, "deduplicate_detections.py"),
    "merge":     os.path.join(SCRIPTS_DIR, "merge_tiles.py"),
    "inject":    os.path.join(SCRIPTS_DIR, "inject_exif_to_merged.py"),
    "export":    os.path.join(SCRIPTS_DIR, "export_geojson.py"),
    "report":    os.path.join(SCRIPTS_DIR, "generate_report.py"),
}

# === Argument Parser ===
parser = argparse.ArgumentParser(description="🧠 Oil Palm Detection Pipeline CLI")
parser.add_argument("--headless", action="store_true", help="Do not open HTML report automatically")
parser.add_argument("--skip-exif", action="store_true", help="Skip EXIF embedding step")
args = parser.parse_args()

# === Timestamped Output ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
report_output = os.path.join(BASE_DIR, f"oil_palm_report_{timestamp}.html")

# === Find EXIF source (if available) ===
def has_exif(img_path):
    try:
        return Image.open(img_path)._getexif() is not None
    except Exception:
        return False

all_images = []
for ext in ["*.jpg", "*.jpeg", "*.png", "*.tif", "*.tiff"]:
    all_images.extend(glob(os.path.join(INPUT_DIR, ext)))

exif_images = [f for f in all_images if has_exif(f)]
if exif_images:
    os.environ["GPS_EXIF_SOURCE"] = exif_images[0]
    print(f"📂 Using EXIF source: {exif_images[0]}")
else:
    os.environ["GPS_EXIF_SOURCE"] = ""
    print("⚠️ No EXIF found — GPS step will be skipped.")

# === Wrapper to run script with logging ===
def run_script(label, path, step_code):
    print(f"\n🔧 {label}")
    ret = subprocess.call([PYTHON_EXEC, path])
    if ret != 0:
        print(f"❌ Failed at {label}")
        sys.exit(step_code)

# === Pipeline ===
run_script("Step 1: Tiling", scripts["tile"], 1)
run_script("Step 2: Detection", scripts["detect"], 2)
run_script("Step 2.6: Deduplication (DBSCAN)", scripts["dedupe"], 26)
run_script("Step 2.7: Merge Dots", scripts["merge"], 27)

# === Conditional EXIF Injection ===
if os.environ["GPS_EXIF_SOURCE"] and not args.skip_exif and os.path.exists(MERGED_PATH):
    run_script("Step 3: Inject GPS EXIF", scripts["inject"], 3)
else:
    print("⚠️ Skipping EXIF embedding")

run_script("Step 4: Export GeoJSON", scripts["export"], 4)
run_script("Step 5: Generate HTML Report", scripts["report"], 5)

# === Save and Open Report ===
if os.path.exists(REPORT_BASE):
    shutil.copyfile(REPORT_BASE, report_output)
    print(f"\n✅ Report saved: {report_output}")
    if not args.headless:
        webbrowser.open(f"file:///{report_output.replace(os.sep, '/')}")
else:
    print(f"❌ Report not found: {REPORT_BASE}")

# === Final Recap ===
print("\n🎯 Pipeline finished.")
print("🖼️ Final image:", MERGED_PATH)
print("📄 Output CSV:", os.path.join(SCRIPTS_DIR, "tiles", "deduplicated_detections.csv"))
print("🌍 GeoJSON:", os.path.join(OUTPUT_DIR, "detection_geojson.geojson"))
print("📊 HTML Report:", report_output)
