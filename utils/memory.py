import json
from collections import deque

class Memory:
    def __init__(self, max_size=100):
        self.interactions = deque(maxlen=max_size)

    def add_interaction(self, prompt, content, ai_evaluation, user_evaluation):
        self.interactions.append({
            'prompt': prompt,
            'content': content,
            'ai_evaluation': ai_evaluation,
            'user_evaluation': user_evaluation
        })

    def get_recent_interactions(self, n=5):
        return list(self.interactions)[-n:]

    def save_to_file(self, filename='memory.json'):
        with open(filename, 'w') as f:
            json.dump(list(self.interactions), f)

    def load_from_file(self, filename='memory.json'):
        try:
            with open(filename, 'r') as f:
                self.interactions = deque(json.load(f), maxlen=self.interactions.maxlen)
        except FileNotFoundError:
            print("No existing memory file found. Starting with empty memory.")

memory = Memory()