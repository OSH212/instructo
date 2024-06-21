import requests
from config import API_KEY, API_URL

class PerplexityAPI:
    def __init__(self):
        self.url = API_URL
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {API_KEY}"
        }

    def get_completion(self, model, messages, temperature=0.1):
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        try:
            response = requests.post(self.url, json=payload, headers=self.headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
            return None

api = PerplexityAPI()