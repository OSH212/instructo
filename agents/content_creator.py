from utils.api_handler import api
from utils.memory import memory
from config import CONTENT_CREATOR_MODEL
from utils.guidelines import EVALUATION_CRITERIA

import logging

logger = logging.getLogger(__name__)

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
            return response['choices'][0]['message']['content']
        else:
            return "I apologize, but I couldn't generate content at this time. Please try again later."


    def _generate_context(self, prompt):
        memory_context = memory.get_content_creator_context(EVALUATION_CRITERIA)
        logger.debug(f"Memory context: {memory_context}")

        context = f"Prompt: {prompt}\n\n"
        context += f"Evaluation Criteria: {', '.join(EVALUATION_CRITERIA.keys())}\n\n"
        
        last_content = memory_context.get('last_content', '')
        logger.debug(f"last content: {last_content}, memory content: {memory_context}, memory:{memory}")
        if last_content:
            context += f"Last Generated Content: {last_content[:200]}...\n\n"
        
        highest_scoring_content = memory_context.get('highest_scoring_content', '')
        if highest_scoring_content and highest_scoring_content != last_content:
            context += f"Highest Scoring Content: {highest_scoring_content[:200]}...\n\n"
        
        last_feedback = memory_context.get('last_feedback', {})
        if last_feedback:
            context += "Last Feedback:\n"
            context += f"Overall Analysis: {last_feedback.get('overall_analysis', '')[:200]}...\n"
            context += "Specific Feedback for Content Creator:\n"
            for criterion, feedback in last_feedback.get('content_creator_feedback', {}).items():
                context += f"- {criterion}: {feedback[:100]}...\n"
            context += "\n"
        
        if last_feedback:
            context += ("Generate the content based on the prompt. Explicitly acknowledge the previous feedback "
                        "and explain how you've incorporated it into your response. Your response should follow this structure:\n"
                        "1. Acknowledgment of previous feedback\n"
                        "2. Explanation of how you've incorporated the feedback\n"
                        "3. New content incorporating the feedback\n"
                        "Focus on improving based on the evaluation criteria and previous feedback.")
        else:
            context += ("Generate the content based on the prompt. Your response should follow this structure:\n"
                        "1. New content addressing the prompt\n"
                        "Focus on addressing the evaluation criteria.")
        if user_evaluation_content := memory_context.get("user_evaluation_content", None):
            context += "User feedback for the content creator (IMPORTANT):\n"
            context += str(user_evaluation_content)

        logger.debug(f"Generated context: {context}")
        return context