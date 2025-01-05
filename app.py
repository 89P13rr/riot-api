import requests
import urllib.parse

# Riot API Key
api_key = 'RGAPI-759a30f4-318d-44fe-91b7-e3fabd5bc9e9'  # API anahtarını buraya ekleyin

def get_summoner_data(summoner_name, region):
    # Sihirdar adını URL encoding yapıyoruz
    encoded_summoner_name = urllib.parse.quote(summoner_name)

    # Riot API'ye istek atıyoruz
    summoner_url = f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{encoded_summoner_name}?api_key={api_key}'
    response = requests.get(summoner_url)

    if response.status_code != 200:
        return {"error": "Sihirdar bulunamadı."}

    summoner_data = response.json()

    # Sihirdarın ID'sini alıyoruz
    summoner_id = summoner_data['id']
    return summoner_id

def get_ranked_data(summoner_id, region):
    # Rank bilgilerini almak için API'den çağrı yapıyoruz
    ranked_url = f'https://{region}.api.riotgames.com/lol/league/v4/entries/by-account/{summoner_id}?api_key={api_key}'
    ranked_response = requests.get(ranked_url)

    if ranked_response.status_code != 200:
        return {"error": "Rank bilgisi alınamadı."}

    ranked_data = ranked_response.json()

    rank = "Unranked"
    lp = "N/A"
    win = 0
    loss = 0

    # Solo 5x5 sıralamaya bakıyoruz
    for entry in ranked_data:
        if entry['queueType'] == 'RANKED_SOLO_5x5':
            rank = entry['tier'] + " " + entry['rank']
            lp = entry['leaguePoints']
            win = entry['wins']
            loss = entry['losses']

    return {
        "rank": rank,
        "lp": lp,
        "win": win,
        "loss": loss
    }

def get_summoner_rank(summoner_name, region):
    summoner_id = get_summoner_data(summoner_name, region)
    if isinstance(summoner_id, dict):  # Error kontrolü
        return summoner_id

    ranked_data = get_ranked_data(summoner_id, region)
    if isinstance(ranked_data, dict):  # Error kontrolü
        return ranked_data

    win_lose = f"{ranked_data['win']}W-{ranked_data['loss']}L"
    return {
        "summoner": summoner_name,
        "region": region,
        "rank": ranked_data['rank'],
        "lp": ranked_data['lp'],
        "win_lose": win_lose
    }

# Test etmek için örnek
summoner_name = 'Telchü'  # Örnek kullanıcı adı
region = 'euw1'  # Örnek bölge (EUW1)
result = get_summoner_rank(summoner_name, region)
print(result)
