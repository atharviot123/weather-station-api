from flask import Flask, request, jsonify
from supabase import create_client
from dotenv import load_dotenv
from flask_cors import CORS
from datetime import datetime, timezone
import os

# =========================================================
# LOAD .ENV
# =========================================================

load_dotenv()


# =========================================================
# CREATE FLASK APP
# =========================================================

app = Flask(__name__)

CORS(app)


# =========================================================
# RASPBERRY PI HEARTBEAT VARIABLE
# =========================================================

last_pi_heartbeat = None


# =========================================================
# SUPABASE CREDENTIALS
# =========================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


# =========================================================
# CHECK SUPABASE CREDENTIALS
# =========================================================

if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL is missing")

if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY is missing")


# =========================================================
# CONNECT TO SUPABASE
# =========================================================

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# =========================================================
# HOME
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "status": "Weather Station API Running"
    }), 200


# =========================================================
# UPDATE WEATHER
# =========================================================

@app.route("/api/weather/update", methods=["POST"])
def update_weather():

    try:

        # Get JSON sent by Raspberry Pi
        data = request.get_json()

        print("DATA RECEIVED:", data)

        # Check data
        if not data:

            return jsonify({
                "success": False,
                "error": "No JSON data received"
            }), 400

        # Create weather object
        weather = {
            "id": 1,
            "temperature": data.get("temperature"),
            "humidity": data.get("humidity"),
            "mq7": data.get("mq7"),
            "pm25": data.get("pm25"),
            "rain": data.get("rain")
        }

        print("DATA TO SUPABASE:", weather)

        # Insert or update row
        result = (
            supabase
            .table("weather_data")
            .upsert(weather)
            .execute()
        )

        print("SUPABASE RESULT:", result.data)

        return jsonify({
            "success": True,
            "message": "Weather Updated",
            "data": result.data
        }), 200

    except Exception as e:

        print("SUPABASE ERROR:", str(e))

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================================================
# GET LATEST WEATHER
# =========================================================

@app.route("/api/weather/latest", methods=["GET"])
def latest_weather():

    try:

        result = (
            supabase
            .table("weather_data")
            .select("*")
            .eq("id", 1)
            .execute()
        )

        print("LATEST DATA:", result.data)

        return jsonify({
            "success": True,
            "data": result.data
        }), 200

    except Exception as e:

        print("GET WEATHER ERROR:", str(e))

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================================================
# RASPBERRY PI HEARTBEAT
# =========================================================

@app.route("/api/pi/heartbeat", methods=["POST"])
def pi_heartbeat():

    global last_pi_heartbeat

    last_pi_heartbeat = datetime.now(timezone.utc)

    print("RASPBERRY PI HEARTBEAT RECEIVED")

    return jsonify({
        "online": True
    }), 200


# =========================================================
# RASPBERRY PI STATUS
# =========================================================

@app.route("/api/pi/status", methods=["GET"])
def pi_status():

    global last_pi_heartbeat

    # No heartbeat received yet
    if last_pi_heartbeat is None:

        return jsonify({
            "online": False
        }), 200

    # Calculate how long ago the Pi sent heartbeat
    seconds = (
        datetime.now(timezone.utc) - last_pi_heartbeat
    ).total_seconds()

    # Pi is considered online if heartbeat
    # was received within the last 10 seconds
    online = seconds <= 10

    print(
        "RASPBERRY PI STATUS:",
        "ONLINE" if online else "OFFLINE"
    )

    return jsonify({
        "online": online
    }), 200


# =========================================================
# RUN FLASK
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )