import os 
import yaml
from collections import deque
from models.evaluation import UserEvaluation
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Memory:
    def __init__(self, max_size=100):
        self.iterations = deque(maxlen=max_size)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f'memory_{self.session_id}.yaml'
        self.highest_scoring_iteration = None
        self.iteration_count = 0

    def add_iteration(self, prompt, content, ai_evaluation, user_evaluation_content, user_feedback_evaluator, feedback_agent_analysis):
        timestamp = datetime.now().isoformat()
        
        iteration = {
            'timestamp': timestamp,
            'prompt': prompt,
            'content': content,
            'ai_evaluation': ai_evaluation,
            'user_evaluation_content': {
                'score': user_evaluation_content.score,
                'feedback': user_evaluation_content.feedback
            },
            'user_feedback_evaluator': user_feedback_evaluator,
            'feedback_agent_analysis': feedback_agent_analysis,
            'metadata': {
                'total_score': sum(user_evaluation_content.score.values()) / len(user_evaluation_content.score)
            }
        }
        self.iterations.append(iteration)
        self._update_highest_scoring_iteration(iteration)
        self.iteration_count += 1
        self.save_to_file()

    def _update_highest_scoring_iteration(self, iteration):
        if not self.highest_scoring_iteration or iteration['metadata']['total_score'] > self.highest_scoring_iteration['metadata']['total_score']:
            self.highest_scoring_iteration = iteration

    def get_content_creator_context(self, evaluation_criteria):
        context = {
            'prompt': self.iterations[-1]['prompt'] if self.iterations else None,
            'last_content': self.iterations[-1]['content'] if self.iterations else None,
            'highest_scoring_content': self.highest_scoring_iteration['content'] if self.highest_scoring_iteration else None,
            'evaluation_criteria': evaluation_criteria,
            'last_feedback': self.iterations[-1]['feedback_agent_analysis'] if self.iterations else None,
            'highest_scoring_feedback': self.highest_scoring_iteration['feedback_agent_analysis'] if self.highest_scoring_iteration else None
        }
        return context

    def get_evaluator_context(self, evaluation_criteria):
        context = {
            'prompt': self.iterations[-1]['prompt'] if self.iterations else None,
            'evaluation_criteria': evaluation_criteria,
            'last_evaluation': self.iterations[-1]['ai_evaluation'] if self.iterations else None,
            'last_content': self.iterations[-1]['content'] if self.iterations else None,
            'highest_scoring_content': self.highest_scoring_iteration['content'] if self.highest_scoring_iteration else None,
            'last_feedback': self.iterations[-1]['feedback_agent_analysis'] if self.iterations else None
        }
        return context

    def get_feedback_agent_context(self):
        return list(self.iterations)[-5:]

    def get_recent_iterations(self, n=5):
        return list(self.iterations)[-n:]

    def get_iteration_count(self):
        return self.iteration_count

    def save_to_file(self):
        with open(self.filename, 'w') as f:
            yaml.dump(list(self.iterations), f)

    def load_from_file(self, session_id=None):
        if session_id:
            filename = f'memory_{session_id}.yaml'
        else:
            files = [f for f in os.listdir() if f.startswith('memory_') and f.endswith('.yaml')]
            if not files:
                print("No existing memory files found. Starting with empty memory.")
                return
            filename = max(files)

        try:
            with open(filename, 'r') as f:
                loaded_data = yaml.safe_load(f)
                if loaded_data:
                    self.iterations = deque(
                        [{**iteration, 
                        'user_evaluation_content': UserEvaluation(
                            score=iteration['user_evaluation_content']['score'],
                            feedback=iteration['user_evaluation_content']['feedback']
                        )}
                        for iteration in loaded_data],
                        maxlen=self.iterations.maxlen
                    )
                    self.session_id = filename.split('_')[1].split('.')[0]
                    self.filename = filename
        except yaml.YAMLError as e:
            print(f"Error loading memory file: {e}")
        except Exception as e:
            print(f"Unexpected error loading memory file: {e}")

    def start_new_session(self):
        self.iterations.clear()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f'memory_{self.session_id}.yaml'
        self.iteration_count = 0
        self.highest_scoring_iteration = None

memory = Memory()