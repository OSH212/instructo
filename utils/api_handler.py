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