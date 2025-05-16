import requests
from django.conf import settings

def analyze_toxicity(text):
    api_key = settings.PERSPECTIVE_API_KEY
    url = f"https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={api_key}"

    data = {
        "comment": {"text": text},
        "languages": ["en"],
        "requestedAttributes": {"TOXICITY": {}}
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()

        # Get the toxicity score (0.0 to 1.0)
        score = result['attributeScores']['TOXICITY']['summaryScore']['value']
        return score
    except Exception as e:
        print("Toxicity analysis error:", e)
        return 0.0  # default to non-toxic if there's an error