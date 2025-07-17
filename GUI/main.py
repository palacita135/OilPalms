from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json

app = Flask(__name__, static_folder='static', template_folder='templates')

GEOJSON_PATH = 'detection_geojson.geojson'

@app.route('/')
def index():
    return render_template('map.html')

@app.route('/geojson')
def geojson():
    if not os.path.exists(GEOJSON_PATH):
        return jsonify({"type": "FeatureCollection", "features": []})
    with open(GEOJSON_PATH, 'r') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/save', methods=['POST'])
def save():
    data = request.get_json()
    with open(GEOJSON_PATH, 'w') as f:
        json.dump(data, f, indent=2)
    return jsonify({"status": "GeoJSON saved successfully ✅"})

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
