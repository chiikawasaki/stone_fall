import requests

def fetch_scores_from_api():
    url = "https://stone-fall-game-api.onrender.com/scores"  # APIのURL
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # スコアで降順に並び替えたあと、上位3件だけ返す
        sorted_data = sorted(data, key=lambda x: x['score'], reverse=True)
        return sorted_data[:3]
    except requests.RequestException as e:
        print(f"Error fetching scores: {e}")
        return []


def send_score_to_api(username, score):
    url = "https://stone-fall-game-api.onrender.com/score"
    payload = {'username': username, 'score': score}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error posting score: {e}")
        return {'error': str(e)}
