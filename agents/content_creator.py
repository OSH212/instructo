from utils.api_handler import api
from utils.memory import memory

class ContentCreator:
    def __init__(self):
        self.model = "llama-3-sonar-small-32k-online"
        self.system_message = ("You are a skilled content creator with expertise in various subjects. "
                               "Your task is to create informative, engaging, and well-structured content "
                               "based on the given prompt. Ensure your writing is clear, factual, and tailored "
                               "to the topic at hand.")

    def create_content(self, prompt):
        recent_interactions = memory.get_recent_interactions()
        context = self._generate_context(recent_interactions)
        
        messages = [
            {"role": "system", "content": self.system_message + context},
            {"role": "user", "content": prompt}
        ]
        response = api.get_completion(self.model, messages)
        return response['choices'][0]['message']['content']

    def _generate_context(self, recent_interactions):
        if not recent_interactions:
            return ""
        
        context = "\n\nRecent performance notes:"
        for interaction in recent_interactions:
            if interaction['user_evaluation'].score < 7:  # Focus on areas needing improvement
                context += f"\n- For prompt '{interaction['prompt']}', user feedback was: {interaction['user_evaluation'].feedback}"
        
        return context

    def learn(self, feedback):
        self.system_message += f"\n\nImprovement note: {feedback}"