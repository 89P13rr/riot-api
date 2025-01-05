import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Riot API Key'iniz (Kendi API key'inizi buraya ekleyin)
RIOT_API_KEY = 'RGAPI-759a30f4-318d-44fe-91b7-e3fabd5bc9e9'  # Bunu gerçek API anahtarınızla değiştirin

# Riot API base URL'si
RIOT_API_URL = "https://api.riotgames.com/lol"

# Bölge ve Summoner API endpoint'leri
SUMMONER_URL = "/lol/summoner/v4/summoners/by-account/"

@app.route("/summoner", methods=["GET"])
def get_summoner_info():
    # Parametreleri al
    name = request.args.get('name')
    region = request.args.get('region')

    if not name or not region:
        return jsonify({"error": "Sihirdar adı ve bölge gereklidir."}), 400

    # Name parametresini 'name/tag' formatında bekliyoruz
    try:
        name_tag = name.split('/')
        summoner_name = name_tag[0]  # Telchü
        summoner_tag = name_tag[1]   # TELCH
    except IndexError:
        return jsonify({"error": "Geçerli bir sihirdar adı ve tag'ı girin."}), 400

    # Riot API'ye istek gönder
    summoner_url = f"{RIOT_API_URL}/lol/summoner/v4/summoners/by-name/{summoner_name}"
    headers = {
        "X-Riot-Token": RIOT_API_KEY
    }

    try:
        response = requests.get(summoner_url, headers=headers)
        summoner_data = response.json()

        if response.status_code != 200:
            return jsonify({"error": "Sihirdar bulunamadı."}), 404
        
        # Kullanıcıya ait bilgileri al
        summoner_id = summoner_data['id']
        summoner_rank_url = f"{RIOT_API_URL}/lol/league/v4/entries/by-summoner/{summoner_id}"

        # Sihirdar'ın elosunu ve günlük skor bilgilerini al
        rank_response = requests.get(summoner_rank_url, headers=headers)
        rank_data = rank_response.json()

        if rank_response.status_code != 200:
            return jsonify({"error": "Rank bilgileri alınamadı."}), 404

        # Rank bilgilerini al
        rank_info = []
        for rank in rank_data:
            rank_info.append({
                "queue": rank.get('queueType'),
                "tier": rank.get('tier'),
                "rank": rank.get('rank'),
                "wins": rank.get('wins'),
                "losses": rank.get('losses')
            })

        # Formatlı şekilde cevabı döndür
        formatted_response = {
            "Sihirdar Adı": f"{summoner_name}#{summoner_tag}",
            "Bölge": region,
            "Rank Bilgileri": rank_info,
            "Genel Bilgiler": {
                "Sihirdar ID": summoner_id,
                "Total Kazanma": sum([rank['wins'] for rank in rank_info]),
                "Total Kaybetme": sum([rank['losses'] for rank in rank_info])
            }
        }

        return jsonify(formatted_response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Flask'ı dış dünyaya açmak için 0.0.0.0 ve Render'ın verdiği port üzerinden çalıştır
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render, PORT değişkenini otomatik olarak sağlar
    app.run(host="0.0.0.0", port=port, debug=True)
