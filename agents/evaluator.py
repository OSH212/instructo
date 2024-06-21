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
            "Use the rubrics and prompts provided for each criterion to guide your evaluation. "
            "Always provide an overall assessment and recommendations for improvement, even if they are minor. "
            "If the content is truly exceptional, state that clearly in your overall assessment."
        )

    def evaluate_content(self, content):
        evaluation_prompt = get_evaluation_prompt(content)
        
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