from utils.api_handler import api
from utils.guidelines import EVALUATION_CRITERIA, get_evaluation_prompt
from utils.memory import memory
from config import EVALUATOR_MODEL

class Evaluator:
    def __init__(self):
        self.model = EVALUATOR_MODEL
        self.system_message = (
            "You are an expert content evaluator with a keen eye for detail, quality, and effectiveness. Your task is to critically assess given content based on specific criteria.\n\n"
            "Evaluation Process:\n"
            "1. Carefully read the content and the initial user-given objective\n"
            "2. Assess the content against each provided criterion\n"
            "3. For each criterion:\n"
            "   + Assign a score based on the provided rubric\n"
            "   + Provide a brief, specific explanation for the score\n"
            "   + Offer constructive feedback or suggestions for improvement\n"
            "4. Provide an overall assessment summarizing the content's strengths and weaknesses\n"
            "5. List key recommendations for improvement, even if they are minor\n\n"
            "Guidelines:\n"
            "+ Be objective and fair in your assessment\n"
            "+ Provide specific, actionable feedback\n"
            "+ Balance criticism with recognition of strengths\n"
            "+ Consider the content's relevance to the initial objective\n"
            "+ If the content is exceptional, clearly state this in your overall assessment\n\n"
            "Your evaluation should be thorough, constructive, and aimed at helping the content creator improve their work while acknowledging their achievements."
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