from flask import Flask, request, jsonify
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ==========================
# HOME
# ==========================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "status": "Weather Station API Running"
    })


# ==========================
# UPDATE WEATHER
# ==========================

@app.route("/api/weather/update", methods=["POST"])
def update_weather():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data received"
            }), 400

        weather = {
            "id": 1,
            "temperature": data["temperature"],
            "humidity": data["humidity"],
            "mq7": data["mq7"],
            "pm25": data["pm25"],
            "rain": data["rain"]
        }

        # Create row if it doesn't exist,
        # otherwise update the existing row
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


# ==========================
# GET LATEST WEATHER
# ==========================

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

        return jsonify({
            "success": True,
            "data": result.data
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==========================
# START SERVER
# ==========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )