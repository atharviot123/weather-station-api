from flask import Flask, request, jsonify
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("URL:", SUPABASE_URL)
print("KEY:", SUPABASE_KEY)

@app.route("/")
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

        weather = {
            "temperature": data["temperature"],
            "humidity": data["humidity"],
            "mq7": data["mq7"],
            "pm25": data["pm25"],
            "rain": data["rain"]
        }

        supabase.table("weather_data") \
            .update(weather) \
            .eq("id", 1) \
            .execute()

        return jsonify({
            "success": True,
            "message": "Weather Updated"
        })

    except Exception as e:

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

        response = supabase.table("weather_data") \
            .select("*") \
            .eq("id", 1) \
            .execute()

        return jsonify(response.data)

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)