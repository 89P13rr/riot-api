import os  # Ortam değişkenlerini almak için
from flask import Flask, request, jsonify
import requests
import urllib.parse

app = Flask(__name__)

# Riot API Key (kendi anahtarını buraya koymalısın)
API_KEY = "RGAPI-759a30f4-318d-44fe-91b7-e3fabd5bc9e9"

@app.route('/summoner', methods=['GET'])
def get_summoner_data():
    # URL'den parametreleri alıyoruz
    raw_name = request.args.get('name')  # Sihirdar adı ve tag
    region = request.args.get('region')  # Bölge

    # Parametre kontrolü
    if not raw_name or not region:
        return jsonify({"error": "Sihirdar adı ve bölge gereklidir."}), 400

    try:
        # Sihirdar adı ve tag'ı ayrıştırma
        if "#" in raw_name:
            summoner_name, summoner_tag = raw_name.split("#")
        else:
            return jsonify({"error": "Geçerli bir sihirdar adı ve tag formatı giriniz. Örn: Telchü#Telch"}), 400

        # Türkçe ve özel karakterleri encode ederek URL'ye uygun hale getiriyoruz
        encoded_name = urllib.parse.quote(summoner_name)

        # 1. Sihirdar bilgilerini alıyoruz
        summoner_url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{encoded_name}"
        summoner_response = requests.get(summoner_url, headers={"X-Riot-Token": API_KEY})
        summoner_data = summoner_response.json()

        if summoner_response.status_code != 200:
            return jsonify({"error": "Sihirdar bulunamadı."}), 404

        summoner_id = summoner_data['id']   # Encrypted Summoner ID
        puuid = summoner_data['puuid']     # PUUID

        # 2. Rank bilgilerini alıyoruz
        rank_url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
        rank_response = requests.get(rank_url, headers={"X-Riot-Token": API_KEY})
        rank_data = rank_response.json()

        if not rank_data:
            return jsonify({"error": "Rank bilgisi bulunamadı."}), 404

        rank_info = rank_data[0]  # İlk sıralama bilgisi
        tier = rank_info['tier']
        rank = rank_info['rank']
        lp = rank_info['leaguePoints']
        wins = rank_info['wins']
        losses = rank_info['losses']

        # 3. Son 24 saatteki maç bilgilerini çekiyoruz
        matches_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20"
        matches_response = requests.get(matches_url, headers={"X-Riot-Token": API_KEY})
        matches = matches_response.json()

        daily_wins = 0
        daily_losses = 0

        for match_id in matches:
            match_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
            match_response = requests.get(match_url, headers={"X-Riot-Token": API_KEY})
            match_data = match_response.json()

            # Kazanç/kayıp kontrolü
            participants = match_data['info']['participants']
            for player in participants:
                if player['puuid'] == puuid:
                    if player['win']:
                        daily_wins += 1
                    else:
                        daily_losses += 1

        # JSON formatında sonuç döndürüyoruz
        return jsonify({
            "rank": f"{tier} {rank}",
            "elo": lp,
            "daily_wins": daily_wins,
            "daily_losses": daily_losses
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Render platformu için port ayarlarını yapıyoruz
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render otomatik olarak PORT değişkenini verir
    app.run(host='0.0.0.0', port=port)  # Flask'ı doğru porta ve host'a bağlıyoruz
