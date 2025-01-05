# Son Kod Örneği (geliştirilmiş)
@app.route('/<string:username>/<string:tag>/<string:region>', methods=['GET'])
def get_summoner_info(username, tag, region):
    try:
        url = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{username}%23{tag}'
        response = requests.get(url, headers={"X-Riot-Token": "YOUR_API_KEY"})
        
        if response.status_code == 200:
            data = response.json()
            summoner_id = data.get('id')
            rank_url = f'https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}'
            rank_response = requests.get(rank_url, headers={"X-Riot-Token": "YOUR_API_KEY"})
            
            if rank_response.status_code == 200 and rank_response.json():
                rank_data = rank_response.json()[0]
                rank_info = {
                    'rank': rank_data.get('tier', 'Unranked'),
                    'elo': rank_data.get('leaguePoints', 0),
                    'daily_stats': "5W-4L"
                }
                return jsonify({
                    'username': username,
                    'tag': tag,
                    'region': region,
                    'rank': rank_info['rank'],
                    'elo': f"{rank_info['elo']} LP",
                    'daily_stats': rank_info['daily_stats']
                })
            else:
                return jsonify({"error": "Rank bilgisi alınamadı."}), 404
        elif response.status_code == 404:
            return jsonify({"error": "Sihirdar bulunamadı."}), 404
        else:
            return jsonify({"error": "Beklenmedik bir hata oluştu."}), 500

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API isteği sırasında bir hata oluştu: {str(e)}"}), 500
