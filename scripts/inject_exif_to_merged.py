import os
from PIL import Image
import piexif

# === Configuration ===
MERGED_IMAGE = r"C:/Users/palac/Documents/OilPalms/scripts/output/merged_result.jpg"
OUTPUT_IMAGE = MERGED_IMAGE.replace("merged_result.jpg", "merged_with_exif.jpg")

# === 1. Get source image path from env
ORIGINAL_IMAGE = os.environ.get("GPS_EXIF_SOURCE")

# === 2. Validate source
if not ORIGINAL_IMAGE or not os.path.exists(ORIGINAL_IMAGE):
    print("⚠️ GPS_EXIF_SOURCE not set or file missing. Skipping EXIF injection.")
    exit(0)

try:
    exif_dict = piexif.load(ORIGINAL_IMAGE)
    if not exif_dict or not exif_dict.get("GPS"):
        print("⚠️ No GPS metadata found in EXIF. Skipping injection.")
        exit(0)

    exif_bytes = piexif.dump(exif_dict)
except Exception as e:
    print(f"⚠️ Failed to extract EXIF: {e}. Skipping injection.")
    exit(0)

# === 3. Inject into merged image
try:
    merged = Image.open(MERGED_IMAGE)
    merged.save(OUTPUT_IMAGE, "jpeg", exif=exif_bytes)
    print(f"✅ EXIF metadata injected into: {OUTPUT_IMAGE}")
except Exception as e:
    print(f"❌ Failed to save merged image with EXIF: {e}")
    exit(1)
