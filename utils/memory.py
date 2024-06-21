import yaml
from collections import deque
from models.evaluation import UserEvaluation

class Memory:
    def __init__(self, max_size=100):
        self.interactions = deque(maxlen=max_size)

    def add_interaction(self, prompt, content, ai_evaluation, user_evaluation):
        self.interactions.append({
            'prompt': prompt,
            'content': content,
            'ai_evaluation': ai_evaluation,
            'user_evaluation': {
                'score': user_evaluation.score,
                'feedback': user_evaluation.feedback
            }
        })

    def get_recent_interactions(self, n=5):
        return list(self.interactions)[-n:]

    def save_to_file(self, filename='memory.yaml'):
        with open(filename, 'w') as f:
            yaml.dump(list(self.interactions), f)

    def load_from_file(self, filename='memory.yaml'):
        try:
            with open(filename, 'r') as f:
                loaded_data = yaml.safe_load(f)
                if loaded_data:
                    self.interactions = deque(
                        [{**interaction, 
                          'user_evaluation': UserEvaluation(**interaction['user_evaluation'])}
                         for interaction in loaded_data],
                        maxlen=self.interactions.maxlen
                    )
        except FileNotFoundError:
            print("No existing memory file found. Starting with empty memory.")
        except yaml.YAMLError as e:
            print(f"Error loading memory file: {e}")

memory = Memory()