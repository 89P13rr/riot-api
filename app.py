import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# Riot API URL'sini buraya ekleyin
riot_api_url = "https://api.riotgames.com/lol/"

# Riot API anahtarınızı buraya ekleyin
riot_api_key = 'RGAPI-759a30f4-318d-44fe-91b7-e3fabd5bc9e9'

# Kullanıcı bilgilerini almak için bir endpoint
@app.route('/<username>/<tag>/<region>', methods=['GET'])
def get_summoner_info(username, tag, region):
    try:
        # API'ye doğru endpoint üzerinden istek yapma
        url = f"{riot_api_url}summoner/v4/summoners/by-name/{username}%23{tag}"
        response = requests.get(url, headers={'X-Riot-Token': riot_api_key})

        # API yanıtını kontrol etme
        if response.status_code == 200:
            data = response.json()
            # Yanıttan gerekli bilgileri çıkaralım
            summoner_id = data['id']
            summoner_name = data['name']
            summoner_level = data['summonerLevel']

            # ELO ve Rank bilgisi için bir başka endpoint
            rank_url = f"{riot_api_url}league/v4/entries/by-account/{summoner_id}"
            rank_response = requests.get(rank_url, headers={'X-Riot-Token': riot_api_key})
            
            if rank_response.status_code == 200:
                rank_data = rank_response.json()
                # Örnek olarak ilk rank bilgisi
                rank = rank_data[0]['tier']
                division = rank_data[0]['rank']
                lp = rank_data[0]['leaguePoints']
                return jsonify({
                    'name': summoner_name,
                    'level': summoner_level,
                    'rank': f"{rank} {division} {lp}LP"
                })
            else:
                return jsonify({"error": "ELO bilgisi alınamadı."})
        else:
            return jsonify({"error": "Sihirdar bulunamadı."})
    
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
