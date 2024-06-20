from config import API_KEY, API_URL
import requests

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
        response = requests.post(self.url, json=payload, headers=self.headers)
        return response.json()

api = PerplexityAPI()