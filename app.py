from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Riot API key
RIOT_API_KEY = "YOUR_RIOT_API_KEY"  # Riot API key'inizi buraya yazın

# Bölge haritalarını Riot Games API ile uyumlu hale getirmek
REGION_MAP = {
    "euw": "EUW1",
    "na": "NA1",
    "eune": "EUN1",
    "kr": "KR",
    "br": "BR1",
    # Diğer bölge kodlarını buraya ekleyebilirsiniz
}

# Kullanıcıdan alınan bilgilerle URL'yi oluşturup, API'den veri çekelim
@app.route('/summoner', methods=['GET'])
def get_summoner_info():
    summoner_name = request.args.get('name')
    summoner_tag = request.args.get('tag')
    region = request.args.get('region').lower()

    # Bölgeyi kontrol et ve Riot API'ye uygun hale getir
    if region not in REGION_MAP:
        return jsonify({"error": "Geçersiz bölge!"}), 400

    # API URL'ini oluştur
    api_url = f"https://{REGION_MAP[region]}.api.riotgames.com/lol/summoner/v4/summoners/by-account/{summoner_name}"

    # Riot API'ye istek gönder
    response = requests.get(api_url, headers={"X-Riot-Token": RIOT_API_KEY})

    if response.status_code != 200:
        return jsonify({"error": "Sihirdar bulunamadı."}), 404
    
    data = response.json()

    # Verileri al
    summoner_level = data['summonerLevel']
    summoner_id = data['id']

    # Rank ve maç verilerini almak için rank API'sine istek gönderelim
    rank_url = f"https://{REGION_MAP[region]}.api.riotgames.com/lol/league/v4/entries/by-account/{summoner_id}"
    rank_response = requests.get(rank_url, headers={"X-Riot-Token": RIOT_API_KEY})

    if rank_response.status_code != 200:
        return jsonify({"error": "Rank bilgisi alınamadı."}), 404

    rank_data = rank_response.json()

    # Rank bilgilerini düzenleyelim
    if rank_data:
        rank_info = rank_data[0]
        rank = rank_info['tier'] + " " + rank_info['rank']
        lp = rank_info['leaguePoints']
    else:
        rank = "Unranked"
        lp = 0

    # Günlük maç bilgilerini alalım
    match_url = f"https://{REGION_MAP[region]}.api.riotgames.com/lol/match/v4/matchlists/by-account/{summoner_id}"
    match_response = requests.get(match_url, headers={"X-Riot-Token": RIOT_API_KEY})

    if match_response.status_code != 200:
        return jsonify({"error": "Maç bilgisi alınamadı."}), 404
    
    match_data = match_response.json()
    total_wins = sum(1 for match in match_data['matches'] if match['stats']['win'])
    total_losses = len(match_data['matches']) - total_wins

    # Sonuçları döndürelim
    result = {
        "summoner_name": summoner_name,
        "summoner_tag": summoner_tag,
        "rank": rank,
        "elo": lp,
        "wins": total_wins,
        "losses": total_losses,
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
