from utils.api_handler import api
from utils.memory import memory
from config import CONTENT_CREATOR_MODEL

class ContentCreator:
    def __init__(self):
        self.model = CONTENT_CREATOR_MODEL
        self.system_message = ("You are a skilled content creator with expertise in various subjects. "
                               "Your task is to create informative, engaging, and well-structured content "
                               "based on the given prompt. Ensure your writing is clear, factual, and tailored "
                               "to the topic at hand.")

    def create_content(self, prompt, previous_content=None, feedback=None):
        context = self._generate_context(prompt, previous_content, feedback)
        
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": context}
        ]
        response = api.get_completion(self.model, messages)
        if response and 'choices' in response:
            return response['choices'][0]['message']['content']
        else:
            return "I apologize, but I couldn't generate content at this time. Please try again later."

    def _generate_context(self, prompt, previous_content, feedback):
        context = f"Prompt: {prompt}\n\n"
        
        if previous_content:
            context += f"Previous content:\n{previous_content}\n\n"
        
        if feedback:
            context += f"Feedback for improvement:\n{feedback}\n\n"
        
        context += "Please acknowledge the feedback and suggested improvements, then generate new or improved content based on the prompt and feedback."
        
        return context

    def learn(self, feedback):
        self.system_message += f"\n\nImprovement note: {feedback}"