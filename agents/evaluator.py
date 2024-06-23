from utils.api_handler import api
from utils.guidelines import EVALUATION_CRITERIA, get_evaluation_prompt
from config import EVALUATOR_MODEL

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
    

    def evaluate_content(self, content, objective):
        evaluation_prompt = get_evaluation_prompt(content, objective)
        if self.feedback:
            evaluation_prompt += "\n\nPlease incorporate the following feedback into your evaluation:\n"
            evaluation_prompt += self.feedback
            evaluation_prompt += "\n\nAfter your evaluation, explain how you incorporated the feedback."
        
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": evaluation_prompt}
        ]
        response = api.get_completion(self.model, messages)
        if response and 'choices' in response:
            evaluation = response['choices'][0]['message']['content']
            if self.feedback:
                evaluation += "\n\nFeedback Incorporation:\n"
                evaluation += self._explain_feedback_incorporation()
            parsed_evaluation = self._parse_evaluation(evaluation)
            if not parsed_evaluation:  # If parsing fails, return the raw evaluation
                return {"Raw Evaluation": evaluation}
            return parsed_evaluation
        else:
            return {"Error": "I apologize, but I couldn't evaluate the content at this time. Please try again later."}
        
    def _explain_feedback_incorporation(self):
        return f"I have received and incorporated the following feedback into my evaluation:\n{self.feedback}\n\nHere's how I incorporated this feedback: [Specific explanation of how the feedback was incorporated into the evaluation]"

    def learn(self, feedback):
        self.feedback = feedback
        
    def _explain_feedback_incorporation(self):
        explanation = "I have received and incorporated the following feedback into my evaluation:\n"
        for criterion, suggestions in self.feedback.items():
            explanation += f"\n{criterion}:\n"
            for suggestion in suggestions:
                explanation += f"- {suggestion}: [Specific explanation of how this suggestion was incorporated into the evaluation]\n"
        return explanation


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

    def learn(self, feedback):
        self.feedback = feedback