from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Riot API Key (anahtarını buraya yaz)
API_KEY = "RGAPI-759a30f4-318d-44fe-91b7-e3fabd5bc9e9"

@app.route("/summoner", methods=["GET"])
def get_summoner_info():
    sihirdar_adi = request.args.get("name")
    region = request.args.get("region")

    if not sihirdar_adi or not region:
        return jsonify({"error": "Sihirdar adı ve bölge gereklidir."}), 400

    # Riot API URL'si
    url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{sihirdar_adi}"
    headers = {"X-Riot-Token": API_KEY}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": "Sihirdar bulunamadı veya API hatası."}), response.status_code

    return jsonify(response.json())

if __name__ == "__main__":
    app.run(debug=True)
