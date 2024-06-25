from utils.memory import memory
from utils.api_handler import api
from utils.guidelines import EVALUATION_CRITERIA, get_evaluation_prompt
from config import EVALUATOR_MODEL

import logging

logger = logging.getLogger(__name__)

class Evaluator:
    def __init__(self):
        self.model = EVALUATOR_MODEL
        self.system_message = (
            "You are an expert content evaluator with extensive linguistic knowledge and a commitment to objectivity.\n\n"
            "Your task is to critically assess content based on specific criteria, leveraging web search capabilities when necessary.\n"
            "Evaluation Process:\n"
            "1. Content Analysis:\n"
            "   - Thoroughly examine the content and the initial user-given objective\n"
            "   - Utilize web search to verify factual accuracy and relevance\n"
            "2. Criteria-based Assessment:\n"
            "   For each provided criterion:\n"
            "   - Assign a score based on the rubric\n"
            "   - Provide a concise, specific justification\n"
            "   - Offer actionable improvement suggestions\n"
            "3. Linguistic Analysis:\n"
            "   - Evaluate grammar, syntax, and style\n"
            "   - Assess vocabulary usage and register appropriateness\n"
            "   - Consider coherence and cohesion\n"
            "4. Overall Evaluation:\n"
            "   - Summarize content strengths and weaknesses\n"
            "   - Maintain a balance between positive and negative feedback\n"
            "5. Improvement Recommendations:\n"
            "   - List specific, actionable suggestions\n"
            "   - Prioritize recommendations based on impact\n\n"
            "Guidelines:\n"
            "- Maintain unwavering objectivity\n"
            "- Provide evidence-based, verifiable feedback\n"
            "- Ensure all critiques are constructive and actionable\n"
            "- Consider content relevance to the initial objective\n"
            "- Acknowledge exceptional quality when warranted, without emotional bias\n"
            "- Utilize web search to complement your knowledge and verify content accuracy\n\n"
            "Your evaluation must be thorough, impartial, and aimed at content improvement while recognizing genuine achievements.\n"
            "Avoid emotional language, maintaining a neutral, professional tone throughout."
        )
        self.feedback = None
        self.last_prompt = None
        self.last_content = None
    

    def evaluate_content(self, content, prompt):
        evaluation_prompt = self._generate_evaluation_prompt(content, prompt)
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": evaluation_prompt}
        ]
        response = api.get_completion(self.model, messages)
        if response and 'choices' in response:
            evaluation = response['choices'][0]['message']['content']
            parsed_evaluation = self._parse_evaluation(evaluation)
            if not parsed_evaluation:  # If parsing fails, return the raw evaluation
                return {"Raw Evaluation": evaluation}
            return parsed_evaluation
        else:
            return {"Error": "I apologize, but I couldn't evaluate the content at this time. Please try again later."}


    def _generate_evaluation_prompt(self, content, prompt):
        memory_context = memory.get_evaluator_context(EVALUATION_CRITERIA)
        #memory_context = memory.get_evaluator_context(EVALUATION_CRITERIA)

        evaluation_prompt = get_evaluation_prompt(content, prompt)
        evaluation_prompt += f"\n\nEvaluation Criteria: {', '.join(EVALUATION_CRITERIA.keys())}\n\n"
        
        last_evaluation = memory_context.get('last_evaluation', '')
        if last_evaluation:
            evaluation_prompt += f"Last Evaluation: {str(last_evaluation)[:200]}...\n\n"
        
        last_content = memory_context.get('last_content', '')
        if last_content:
            evaluation_prompt += f"Last Generated Content: {last_content[:200]}...\n\n"
        
        highest_scoring_content = memory_context.get('highest_scoring_content', '')
        if highest_scoring_content and highest_scoring_content != last_content:
            evaluation_prompt += f"Highest Scoring Content: {highest_scoring_content[:200]}...\n\n"
        
        last_feedback = memory_context.get('last_feedback', {})
        if last_feedback:
            evaluation_prompt += "Last Feedback for Evaluator:\n"
            evaluation_prompt += f"Overall Analysis: {last_feedback.get('overall_analysis', '')[:200]}...\n"
            evaluation_prompt += "Specific Feedback for Evaluator:\n"
            evaluation_prompt +=  str(last_feedback.get('evaluator_feedback', ""))
        if user_feedback_evaluator := memory_context.get("user_feedback_evaluator", None):
            evaluation_prompt += "User feedback for the evaluator (IMPORTANT):\n"
            evaluation_prompt += str(user_feedback_evaluator)

            #for criterion, feedback in last_feedback.get('evaluator_feedback', {}).items():
                #evaluation_prompt += f"- {criterion}: {feedback[:100]}...\n"
            evaluation_prompt += "\n"
        
        evaluation_prompt += ("Please evaluate the content based on the given criteria. Your evaluation should follow this structure:\n"
                            "1. Acknowledgment of previous feedback\n"
                            "2. Explanation of how you've incorporated the feedback into your evaluation process\n"
                            "3. Detailed evaluation of the content, addressing each criterion\n"
                            "Focus on providing constructive and actionable feedback, and explain any changes in your evaluation approach based on previous feedback.")
        
        logger.debug(f"evaluation_prompt: {evaluation_prompt}")
        return evaluation_prompt
    
    def _parse_evaluation(self, evaluation):
        parsed = {}
        current_criterion = None
        for line in evaluation.split('\n'):
            line = line.strip()
            if line in EVALUATION_CRITERIA:
                current_criterion = line
                parsed[current_criterion] = {'score': None, 'explanation': '', 'suggestions': []}
            elif line.startswith("Score:") and current_criterion:
                try:
                    parsed[current_criterion]['score'] = float(line.split(":")[1].strip())
                except ValueError:
                    parsed[current_criterion]['score'] = "N/A"
            elif line.startswith("Explanation:") and current_criterion:
                parsed[current_criterion]['explanation'] = line.split(":", 1)[1].strip()
            elif line.startswith("-") and current_criterion:
                parsed[current_criterion]['suggestions'].append(line[1:].strip())
        
        if not parsed:  # If no criteria were parsed, return the raw evaluation
            return {"Raw Evaluation": evaluation}
        return parsed