import os
import webbrowser

# === Configuration ===
REPORT_PATH = r"C:/Users/palac/Documents/Oilpalms/oil_palm_report.html"

# === Check if report exists ===
if not os.path.exists(REPORT_PATH):
    print(f"❌ Report file not found at: {REPORT_PATH}")
    exit(1)

# === Convert to file URL and open in browser ===
file_url = f"file:///{REPORT_PATH.replace(os.sep, '/')}"
webbrowser.open(file_url)

print(f"🌐 Opening Oil Palm Detection Report at:\n{file_url}")
