import requests

def get_rank_and_elo(summoner_name, region):
    # API anahtarınızı burada yazın
    api_key = 'RGAPI-759a30f4-318d-44fe-91b7-e3fabd5bc9e9'  # Buraya kendi API anahtarınızı yazın
    
    # Riot API'den sihirdar bilgilerini çekiyoruz
    summoner_url = f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={api_key}'
    response = requests.get(summoner_url)
    
    if response.status_code != 200:
        return {"error": "Sihirdar bulunamadı."}
    
    summoner_data = response.json()
    summoner_id = summoner_data['id']
    
    # Sihirdarın rank bilgilerini alıyoruz
    ranked_url = f'https://{region}.api.riotgames.com/lol/league/v4/entries/by-account/{summoner_id}?api_key={api_key}'
    ranked_response = requests.get(ranked_url)
    
    if ranked_response.status_code != 200:
        return {"error": "Rank bilgisi alınamadı."}
    
    ranked_data = ranked_response.json()

    # Rank ve LP bilgilerini düzenliyoruz
    rank = "Unranked"
    elo = 0
    lp = "N/A"
    win = 0
    loss = 0
    
    for entry in ranked_data:
        if entry['queueType'] == 'RANKED_SOLO_5x5':
            rank = entry['tier'] + " " + entry['rank']
            lp = entry['leaguePoints']
            elo = lp * 10  # LP'yi ELO'ya çeviriyoruz (örnek: LP * 10)
            win = entry['wins']
            loss = entry['losses']

    win_lose = f"{win}W-{loss}L"

    # JSON formatında düzenli yanıt dönüyoruz
    return {
        "summoner": summoner_name,
        "region": region,
        "rank": rank,
        "elo": elo,
        "lp": lp,
        "win_lose": win_lose
    }

# API üzerinden test etmek için örnek
summoner_name = 'Telchü'  # Örnek kullanıcı adı
region = 'euw1'  # Örnek bölge (EUW1)
result = get_rank_and_elo(summoner_name, region)
print(result)
