from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# -----------------------------
# Database Configuration
# -----------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "emergency_resources.db")


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        address TEXT NOT NULL,
        phone TEXT,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL
    )
    """)

    conn.commit()
    conn.close()


init_db()


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------
# Distance Calculation (Pure Python)
# -----------------------------

def calculate_distance(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2

    R = 6371.0  # Earth radius in km

    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


# -----------------------------
# Routes
# -----------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/resources", methods=["POST"])
def get_resources():
    try:
        data = request.get_json()

        user_lat = data.get("latitude")
        user_lon = data.get("longitude")

        if user_lat is None or user_lon is None:
            return jsonify({"error": "Invalid location data"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM resources")
        resources = cursor.fetchall()
        conn.close()

        resources_with_distance = []

        for resource in resources:
            distance = calculate_distance(
                user_lat, user_lon,
                resource["latitude"], resource["longitude"]
            )

            resources_with_distance.append({
                "id": resource["id"],
                "name": resource["name"],
                "type": resource["type"],
                "address": resource["address"],
                "phone": resource["phone"],
                "latitude": resource["latitude"],
                "longitude": resource["longitude"],
                "distance": round(distance, 2)
            })

        resources_with_distance.sort(key=lambda x: x["distance"])

        return jsonify({
            "success": True,
            "resources": resources_with_distance[:10]
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy"
    })


# -----------------------------
# Local Run (Render uses Gunicorn)
# -----------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

