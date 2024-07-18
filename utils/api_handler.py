# import requests
# from config import API_KEY, API_URL
import litellm
from litellm import completion
import os
from config import API_KEY

litellm.set_verbose=False

class PerplexityAPI:
    def __init__(self):
        os.environ['PERPLEXITYAI_API_KEY'] = API_KEY

    def get_completion(self, model, messages):
        try:
            response = completion(
                model=model,
                messages=messages
            )
            return response
        except Exception as e:
            print(f"API request failed: {e}")
            return None

api = PerplexityAPI()

# class PerplexityAPI:
#     def __init__(self):
#         self.url = API_URL
#         self.headers = {
#             "accept": "application/json",
#             "content-type": "application/json",
#             "authorization": f"Bearer {API_KEY}"
#         }

#     def get_completion(self, model, messages, temperature=0.1):
#         payload = {
#             "model": model,
#             "messages": messages,
#             "temperature": temperature
#         }
#         try:
#             response = requests.post(self.url, json=payload, headers=self.headers)
#             response.raise_for_status()  # Raise an exception for bad status codes
#             return response.json()
#         except requests.exceptions.RequestException as e:
#             print(f"API request failed: {e}")
#             if hasattr(e, 'response') and e.response is not None:
#                 print(f"Response content: {e.response.text}")
#             return None

# api = PerplexityAPI()