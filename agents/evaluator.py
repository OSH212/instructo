from utils.api_handler import api
from utils.guidelines import EVALUATION_CRITERIA, get_evaluation_prompt
from utils.memory import memory
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

    def evaluate_content(self, content, objective):
        evaluation_prompt = get_evaluation_prompt(content, objective)
        
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": evaluation_prompt}
        ]
        response = api.get_completion(self.model, messages)
        if response and 'choices' in response:
            full_evaluation = response['choices'][0]['message']['content']
            parsed_evaluation = self._parse_evaluation(full_evaluation)
            if not parsed_evaluation['overall_assessment'] and not parsed_evaluation['recommendations']:
                return full_evaluation  # Return full text if parsing fails
            return parsed_evaluation
        else:
            return "I apologize, but I couldn't evaluate the content at this time. Please try again later."

    def _parse_evaluation(self, evaluation):
        parsed = {
            'overall_assessment': '',
            'recommendations': [],
            'no_improvements_needed': False,
            'full_evaluation': evaluation
        }
        
        lines = evaluation.split('\n')
        current_section = None
        for line in lines:
            line = line.strip()
            if line.lower().startswith("overall assessment:"):
                current_section = 'overall_assessment'
                parsed['overall_assessment'] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("key recommendations for improvement:"):
                current_section = 'recommendations'
            elif current_section == 'recommendations' and line.startswith("-"):
                parsed['recommendations'].append(line[1:].strip())
            elif current_section == 'overall_assessment':
                parsed['overall_assessment'] += " " + line
        
        if "no improvements needed" in parsed['overall_assessment'].lower() or not parsed['recommendations']:
            parsed['no_improvements_needed'] = True

        return parsed

    def learn(self, feedback):
        self.system_message += f"\n\nImprovement note: {feedback}"