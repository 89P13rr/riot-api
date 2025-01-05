from flask import Flask, jsonify
import requests

app = Flask(__name__)

# Riot API Anahtarı
RIOT_API_KEY = "
RGAPI-759a30f4-318d-44fe-91b7-e3fabd5bc9e9"

# Ana Sayfa
@app.route('/')
def home():
    return "Riot Games API: Sihirdar Bilgisi Servisi Çalışıyor.", 200

# Sihirdar Bilgisi Al (Rank, Elo, Günlük)
@app.route('/lol/<summoner_name>/<summoner_tag>/<region>/<info>', methods=['GET'])
def get_summoner_info(summoner_name, summoner_tag, region, info):
    try:
        # Sihirdar ID'sini al
        summoner_url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"
        headers = {"X-Riot-Token": RIOT_API_KEY}
        response = requests.get(summoner_url, headers=headers)
        
        if response.status_code != 200:
            return jsonify({"error": "Sihirdar bulunamadı veya API anahtarı hatalı."}), 404

        summoner_data = response.json()
        summoner_id = summoner_data.get("id")
        account_id = summoner_data.get("accountId")
        summoner_level = summoner_data.get("summonerLevel")

        # Rank Bilgisi
        if info == "rank":
            rank_url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
            rank_response = requests.get(rank_url, headers=headers)
            if rank_response.status_code == 200:
                rank_data = rank_response.json()
                if rank_data:
                    ranked_info = rank_data[0]  # İlk mod, örneğin Tek/Çift
                    return jsonify({
                        "summoner": summoner_name,
                        "rank": ranked_info.get("tier") + " " + ranked_info.get("rank"),
                        "lp": ranked_info.get("leaguePoints"),
                        "wins": ranked_info.get("wins"),
                        "losses": ranked_info.get("losses")
                    }), 200
                else:
                    return jsonify({"info": "Rank bilgisi bulunamadı."}), 404
            else:
                return jsonify({"error": "Rank verisine ulaşılamadı."}), 500

        # Elo Bilgisi
        elif info == "elo":
            return jsonify({
                "summoner": summoner_name,
                "level": summoner_level
            }), 200

        # Günlük Maç Bilgisi
        elif info == "daily":
            match_url = f"https://{region}.api.riotgames.com/lol/match/v4/matchlists/by-account/{account_id}?endIndex=5"
            match_response = requests.get(match_url, headers=headers)
            if match_response.status_code == 200:
                match_data = match_response.json()
                matches = match_data.get("matches", [])
                wins = 0
                losses = 0

                # Örnek Maç İşleme
                for match in matches:
                    # Maç Sonucunu Simule Ediyoruz (Gerçek Sonuç İçin Daha Fazla İşlem Gerekebilir)
                    if match.get("queue") == 420:  # Sadece Tek/Çift Kuyruğu Örneği
                        wins += 1  # Kazanma/Kaybetme Ayrımı Gerekebilir

                return jsonify({
                    "summoner": summoner_name,
                    "daily": f"{wins}W - {losses}L"
                }), 200
            else:
                return jsonify({"error": "Günlük maç bilgisi bulunamadı."}), 404

        else:
            return jsonify({"error": "Geçersiz bilgi tipi. 'rank', 'elo' veya 'daily' kullanın."}), 400

    except Exception as e:
        return jsonify({"error": f"Bir hata oluştu: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
