from utils.api_handler import api
from utils.guidelines import EVALUATION_CRITERIA, get_evaluation_prompt
from utils.memory import memory
from config import EVALUATOR_MODEL

class Evaluator:
    def __init__(self):
        self.model = EVALUATOR_MODEL
        self.system_message = (
            "You are an expert content evaluator with a keen eye for detail and quality. "
            "Your task is to critically assess the given content based on the provided criteria. "
            "Provide a thorough evaluation, highlighting strengths and areas for improvement. "
            "Be objective, constructive, and specific in your feedback. "
            "Use the rubrics and prompts provided for each criterion to guide your evaluation."
        )

    def evaluate_content(self, content):
        recent_interactions = memory.get_recent_interactions()
        context = self._generate_context(recent_interactions)
        
        evaluation_prompt = get_evaluation_prompt(content)
        
        messages = [
            {"role": "system", "content": self.system_message + context},
            {"role": "user", "content": evaluation_prompt}
        ]
        response = api.get_completion(self.model, messages)
        if response and 'choices' in response:
            return response['choices'][0]['message']['content']
        else:
            return "I apologize, but I couldn't evaluate the content at this time. Please try again later."

    def _generate_context(self, recent_interactions):
        if not recent_interactions:
            return ""
        
        context = "\n\nRecent evaluation performance notes:"
        for interaction in recent_interactions:
            user_evaluation = interaction['user_evaluation']
            if isinstance(user_evaluation, dict) and 'score' in user_evaluation:
                if user_evaluation['score'] < 7:  # Focus on areas needing improvement
                    context += f"\n- User feedback on your evaluation: {user_evaluation['feedback']}"
        
        return context

    def learn(self, feedback):
        self.system_message += f"\n\nImprovement note: {feedback}"