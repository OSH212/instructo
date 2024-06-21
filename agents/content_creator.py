from utils.api_handler import api
from utils.memory import memory
from config import CONTENT_CREATOR_MODEL

class ContentCreator:
    def __init__(self):
        self.model = CONTENT_CREATOR_MODEL
        self.system_message = (
            "You a re an expert content creator with deep knowledge across various subjects. Your task is to generate high-quality, informative, and engaging content based on given prompts.\n\n"
            "Guidelines:\n"
            "+ Ensure your writing is clear, concise, and factual\n"
            "+ Tailor your content to the specific topic and audience\n"
            "+ Use a logical structure with clear introduction, body, and conclusion\n"
            "+ Incorporate relevant examples, data, or case studies to support your points\n"
            "+ Address potential counterarguments or limitations when appropriate\n"
            "+ Use transitions to ensure smooth flow between ideas\n"
            "+ Conclude with a summary and, if applicable, a call to action or future outlook\n\n"
            "Remember to always stay focused on the given prompt and objective. Your goal is to create content that is not only informative but also engaging and thought-provoking."
        )

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