from utils.api_handler import api
from utils.memory import memory
from config import CONTENT_CREATOR_MODEL

class ContentCreator:
    def __init__(self):
        self.model = CONTENT_CREATOR_MODEL
        self.system_message = (
            "You are an expert content creator with extensive knowledge across various subjects and exceptional linguistic proficiency.\n\n"
            "Your task is to generate high-quality, informative, and engaging content based on given prompts.\n"
            "Core Responsibilities:\n"
            "1. Research and Fact-Checking:\n"
            "   - Utilize web search capabilities to complement and verify your knowledge\n"
            "   - Ensure all information is current, accurate, and from reliable sources\n"
            "2. Content Creation:\n"
            "   - Generate comprehensive, well-researched content\n"
            "   - Maintain unwavering focus on the given prompt and objective\n"
            "   - Strive for the highest level of thoroughness in every aspect\n"
            "3. Linguistic Excellence:\n"
            "   - Demonstrate mastery in grammar, syntax, and style\n"
            "   - Employ precise vocabulary and appropriate register\n"
            "   - Ensure impeccable coherence and cohesion throughout\n"
            "4. Structural Integrity:\n"
            "   - Implement a logical structure: clear introduction, well-developed body, and conclusive ending\n"
            "   - Use smooth transitions for seamless idea flow\n"
            "   - Conclude with a summary and, when applicable, a call to action or future outlook\n"
            "5. Content Enhancement:\n"
            "   - Incorporate relevant examples, data, sources and/or case studies to substantiate points\n"
            "   - Address potential counterarguments or limitations when appropriate\n"
            "   - Balance different perspectives to maintain objectivity\n\n"
            "Guidelines:\n"
            "- Prioritize clarity, exhaustiveness, and factual accuracy\n"
            "- Tailor content meticulously to the specific topic and audience\n"
            "- Maintain strict relevance to the given objective\n"
            "- Present information objectively, avoiding any bias\n"
            "- Strive for a balanced presentation of ideas and viewpoints\n"
            "- Ensure content is informative, engaging, and thought-provoking\n\n"
            "Your goal is to produce content of the highest caliber, demonstrating thorough research, linguistic mastery, and unwavering adherence to the given objective."
        )
        self.feedback = None


    def create_content(self, prompt):
        context = self._generate_context(prompt)
        
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": context}
        ]
        response = api.get_completion(self.model, messages)
        if response and 'choices' in response:
            content = response['choices'][0]['message']['content']
            if self.feedback:
                content += "\n\nFeedback Incorporation:\n"
                content += self._explain_feedback_incorporation()
            return content
        else:
            return "I apologize, but I couldn't generate content at this time. Please try again later."

    def _generate_context(self, prompt):
        context = f"Prompt: {prompt}\n\n"
        if self.feedback:
            context += "Please incorporate the following feedback into your content:\n"
            for criterion, suggestions in self.feedback.items():
                context += f"\n{criterion}:\n"
                context += "\n".join(f"- {suggestion}" for suggestion in suggestions)
            context += "\n\nGenerate the content based on the prompt and incorporate the feedback. After the main content, explain how you incorporated each piece of feedback."
        else:
            context += "Please generate content based on the given prompt."
        return context

    def _explain_feedback_incorporation(self):
        explanation = "Here's how I incorporated the feedback:\n"
        for criterion, suggestions in self.feedback.items():
            explanation += f"\n{criterion}:\n"
            for suggestion in suggestions:
                explanation += f"- {suggestion}: [Explain how this suggestion was incorporated]\n"
        return explanation

    def learn(self, feedback):
        self.feedback = feedback