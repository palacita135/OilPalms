import os
import csv
from datetime import datetime

# === Configuration ===
PROJECT_ROOT = r"C:/Users/palac/Documents/Oilpalms"
TILE_DIR     = os.path.join(PROJECT_ROOT, "scripts", "tiles")
OUTPUT_DIR   = os.path.join(PROJECT_ROOT, "scripts", "output")
REPORT_DIR   = os.path.join(PROJECT_ROOT, "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

CSV_PATH     = os.path.join(TILE_DIR, "deduplicated_detections.csv")
MERGED_IMAGE = os.path.join(OUTPUT_DIR, "merged_with_exif.jpg")
GEOJSON_PATH = os.path.join(OUTPUT_DIR, "detection_geojson.geojson")

# === Output Report Filename ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_NAME = f"oil_palm_report_{timestamp}.html"
REPORT_PATH = os.path.join(REPORT_DIR, REPORT_NAME)

# === Count Classes ===
count_oil_palm = 0
count_vop = 0
total = 0

if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"❌ Deduplicated Detection CSV not found: {CSV_PATH}")

with open(CSV_PATH, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cls = row['Class'].lower()
        if cls == 'oil palm':
            count_oil_palm += 1
        elif cls == 'vop':
            count_vop += 1
        total += 1

# === Build HTML ===
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Oil Palm Detection Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', sans-serif;
            margin: 40px;
            background-color: #f4f4f4;
            color: #333;
            transition: background 0.3s, color 0.3s;
        }}
        .dark-mode {{
            background-color: #1e1e1e;
            color: #f4f4f4;
        }}
        h1, h2 {{
            color: #2c3e50;
        }}
        .dark-mode h1, .dark-mode h2 {{
            color: #e0e0e0;
        }}
        .stats {{
            margin-top: 20px;
            padding: 20px;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        .dark-mode .stats {{
            background-color: #2c2c2c;
            box-shadow: none;
        }}
        .stats p {{
            font-size: 18px;
        }}
        a {{
            color: #2980b9;
            text-decoration: none;
        }}
        .dark-mode a {{
            color: #79baff;
        }}
        .preview {{
            margin-top: 30px;
        }}
        img {{
            max-width: 100%;
            border-radius: 10px;
            border: 1px solid #ccc;
            cursor: zoom-in;
        }}
        .dark-mode img {{
            border-color: #444;
        }}
        .fullscreen {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.9);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }}
        .fullscreen img {{
            max-width: 95%;
            max-height: 95%;
            border: 5px solid #fff;
        }}
        .toggle {{
            margin-top: 10px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <h1>🌴 Oil Palm Detection Report</h1>
    <p><strong>Generated:</strong> {timestamp}</p>

    <div class="toggle">
        <label><input type="checkbox" id="darkToggle"> 🌙 Toggle Dark Mode</label>
    </div>

    <div class="stats">
        <h2>📊 Detection Summary</h2>
        <p>🟢 Oil Palm Trees: <strong>{count_oil_palm}</strong></p>
        <p>🔵 VOPs: <strong>{count_vop}</strong></p>
        <p>🧮 Total Detections: <strong>{total}</strong></p>
    </div>

    <div class="stats">
        <h2>📂 Download Files</h2>
        <ul>
            <li><a href="../scripts/output/merged_with_exif.jpg" download>📷 Merged Image with EXIF</a></li>
            <li><a href="../scripts/tiles/detections.csv" download>📄 deduplicated_detections.csv</a></li>
            <li><a href="../scripts/output/detection_geojson.geojson" download>🌍 GeoJSON</a></li>
        </ul>
    </div>

    <div class="preview">
        <h2>🖼️ Merged Image Preview</h2>
        <img id="previewImg" src="../scripts/output/merged_with_exif.jpg" alt="Merged Image">
    </div>

    <div class="fullscreen" id="fullscreen">
        <img id="fullImg" src="">
    </div>

    <script>
        const toggle = document.getElementById('darkToggle');
        const body = document.body;

        toggle.addEventListener('change', () => {{
            body.classList.toggle('dark-mode');
        }});

        const previewImg = document.getElementById('previewImg');
        const fullscreen = document.getElementById('fullscreen');
        const fullImg = document.getElementById('fullImg');

        previewImg.addEventListener('click', () => {{
            fullImg.src = previewImg.src;
            fullscreen.style.display = 'flex';
        }});

        fullscreen.addEventListener('click', () => {{
            fullscreen.style.display = 'none';
        }});
    </script>
</body>
</html>
"""

# === Save HTML file ===
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(html)

# Save a base copy for auto-preview
legacy = os.path.join(PROJECT_ROOT, "oil_palm_report.html")
with open(legacy, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Enhanced HTML Report saved to: {REPORT_PATH}")
