import os 
import yaml
from collections import deque
from models.evaluation import UserEvaluation
from datetime import datetime

class Memory:
    def __init__(self, max_size=100):
        self.interactions = deque(maxlen=max_size)
        self.filename = f'memory_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml'

    def add_interaction(self, prompt, content, ai_evaluation, user_evaluation_content, user_feedback_evaluator):
        timestamp = datetime.now().isoformat()
        self.interactions.append({
            'timestamp': timestamp,
            'prompt': prompt,
            'content': content,
            'ai_evaluation': ai_evaluation,
            'user_evaluation_content': {
                'score': user_evaluation_content.score,
                'feedback': user_evaluation_content.feedback
            },
            'user_feedback_evaluator': user_feedback_evaluator
        })

    def get_recent_interactions(self, n=5):
        return list(self.interactions)[-n:]

    def save_to_file(self):
        with open(self.filename, 'a') as f:
            yaml.dump([self.interactions[-1]], f)

    def load_from_file(self):
        try:
            files = [f for f in os.listdir() if f.startswith('memory_') and f.endswith('.yaml')]
            if not files:
                print("No existing memory files found. Starting with empty memory.")
                return

            latest_file = max(files)
            with open(latest_file, 'r') as f:
                loaded_data = yaml.safe_load(f)
                if loaded_data:
                    self.interactions = deque(
                        [{**interaction, 
                        'user_evaluation_content': UserEvaluation(
                            score=interaction['user_evaluation_content']['score'],
                            feedback=interaction['user_evaluation_content']['feedback']
                        )}
                        for interaction in loaded_data],
                        maxlen=self.interactions.maxlen
                    )
        except yaml.YAMLError as e:
            print(f"Error loading memory file: {e}")
        except Exception as e:
            print(f"Unexpected error loading memory file: {e}")

memory = Memory()