from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Riot API Key'inizi buraya yazın
RIOT_API_KEY = "RGAPI-759a30f4-318d-44fe-91b7-e3fabd5bc9e9"

# Bölge haritaları
REGION_MAP = {
    "tr": "TR1",
    "euw": "EUW1",
    "na": "NA1",
    "kr": "KR",
    # Diğer bölgeler eklenebilir
}

@app.route('/lol/<summoner_name>/<summoner_tag>/<info>/<region>', methods=['GET'])
def get_summoner_data(summoner_name, summoner_tag, info, region):
    """
    Riot API'den sihirdar bilgisi almak için endpoint.
    :param summoner_name: Sihirdarın adı.
    :param summoner_tag: Sihirdar tagı.
    :param info: İstenen bilgi türü (rank, elo, score).
    :param region: Bölge (tr, euw, vs).
    :return: JSON formatında sihirdar bilgisi.
    """
    # Bölge kontrolü
    if region not in REGION_MAP:
        return jsonify({"error": "Geçersiz bölge seçimi!"}), 400

    # Tam sihirdar adını oluştur
    full_summoner_name = f"{summoner_name}#{summoner_tag}"

    # Riot API'den sihirdar bilgisi çekmek için URL
    summoner_url = f"https://{REGION_MAP[region]}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{full_summoner_name}"
    response = requests.get(summoner_url, headers={"X-Riot-Token": RIOT_API_KEY})

    # Hata kontrolü
    if response.status_code != 200:
        return jsonify({"error": "Sihirdar bulunamadı veya API erişim hatası."}), 404

    # Sihirdar bilgilerini al
    summoner_data = response.json()
    summoner_id = summoner_data['id']
    summoner_name = summoner_data['name']

    # İstenen bilgi türüne göre işlem yap
    if info == "rank":
        # Rank bilgilerini almak için League API'sini kullan
        rank_url = f"https://{REGION_MAP[region]}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
        rank_response = requests.get(rank_url, headers={"X-Riot-Token": RIOT_API_KEY})

        if rank_response.status_code != 200:
            return jsonify({"error": "Rank bilgisi alınamadı."}), 404

        rank_data = rank_response.json()
        if not rank_data:
            return jsonify({"info": f"{summoner_name} (Rank Bilgisi Yok)"}), 200

        # Rank bilgilerini döndür
        rank_info = rank_data[0]
        tier = rank_info['tier']
        rank = rank_info['rank']
        lp = rank_info['leaguePoints']

        return jsonify({
            "info": f"{summoner_name} (Tek/Çift) » {tier} {rank} ({lp} LP)"
        })

    elif info == "elo":
        # Elo bilgisi rank API'sinden alındı, yukarıdakiyle aynı
        return get_summoner_data(summoner_name, summoner_tag, "rank", region)

    elif info == "score":
        # Günlük galibiyet ve mağlubiyet bilgisi
        match_url = f"https://{REGION_MAP[region]}.api.riotgames.com/lol/match/v4/matchlists/by-account/{summoner_id}"
        match_response = requests.get(match_url, headers={"X-Riot-Token": RIOT_API_KEY})

        if match_response.status_code != 200:
            return jsonify({"error": "Maç bilgisi alınamadı."}), 404

        match_data = match_response.json()
        total_matches = len(match_data['matches'])
        total_wins = sum(1 for match in match_data['matches'] if match['stats']['win'])

        return jsonify({
            "info": f"{summoner_name} (Bugün) » {total_wins}W - {total_matches - total_wins}L"
        })

    else:
        return jsonify({"error": "Geçersiz bilgi türü. Kullanılabilir türler: rank, elo, score"}), 400


if __name__ == '__main__':
    app.run(debug=True)
