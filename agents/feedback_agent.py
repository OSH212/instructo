from utils.api_handler import api
from config import FEEDBACK_MODEL
from models.evaluation import UserEvaluation
from utils.guidelines import EVALUATION_CRITERIA


class FeedbackAgent:
    def __init__(self):
        self.model = FEEDBACK_MODEL
        self.system_message = (
            "You are an AI improvement specialist with expertise in content creation, evaluation, and system optimization. "
            "Your goal is to provide insightful analysis and actionable feedback to enhance AI performance."
        )

    def analyze_interaction(self, content, evaluation, user_eval):
        interpretation_prompt = self._generate_interpretation_prompt(content, evaluation, user_eval)
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": interpretation_prompt}
        ]

        response = api.get_completion(self.model, messages)
        if response and 'choices' in response:
            interpretation = response['choices'][0]['message']['content'].strip()
            improvements_needed = "improvements needed" in interpretation.lower()
            return interpretation, improvements_needed
        return None, True  # Default to improvements needed if analysis fails

    def generate_improvement_suggestions(self, interpretation):
        feedback_prompt = self._generate_feedback_prompt(interpretation)
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": interpretation},
            {"role": "assistant", "content": "I understand. I'll provide specific, actionable feedback for both the content creator and the evaluator based on the previous analysis."},
            {"role": "user", "content": feedback_prompt}
        ]

        response = api.get_completion(self.model, messages)
        if response and 'choices' in response:
            suggestions = response['choices'][0]['message']['content']
            return self._parse_suggestions(suggestions)
        return None, None

    def _generate_interpretation_prompt(self, content, evaluation, user_eval):
        return f"""
        Analyze the following interaction:

        Original Prompt: {content['prompt']}
        Generated Content: {content['content']}
        AI Evaluation: {evaluation}
        User Score: {user_eval.score}
        User Feedback: {user_eval.feedback}

        Your tasks:
        1. Compare the AI evaluation with the user feedback, noting any discrepancies.
        2. Assess the quality of the generated content in light of both evaluations.
        3. Determine if improvements are needed for the content, the evaluation process, or both.

        Provide a detailed analysis addressing the following:
        1. Content Quality: Assess the strengths and weaknesses of the generated content.
        2. Evaluation Accuracy: Determine if the AI evaluation was fair and accurate.
        3. User Satisfaction: Analyze the user's feedback and score in relation to the content and AI evaluation.
        4. Improvement Needs: Specify if improvements are needed for the content creator, evaluator, or both.

        Conclude with one of the following decisions, providing a thorough explanation:
        1. "No improvements needed" if the content is exceptional and both AI and user evaluations align positively.
        2. "Improvements needed" if there are discrepancies or clear areas for enhancement in either the content or evaluation process.
        """

    def _generate_feedback_prompt(self, interpretation):
        return """
        Based on your previous analysis, provide specific, actionable feedback for both the content creator and the evaluator:

        1. For the content creator:
           - Identify key areas for improvement in the content.
           - Suggest specific strategies to enhance content quality, relevance, and engagement.
           - Provide examples or techniques that could be applied to address the identified weaknesses.

        2. For the evaluator:
           - Assess the accuracy and fairness of the evaluation.
           - Suggest improvements in the evaluation process or criteria.
           - Provide guidance on how to align the AI evaluation more closely with user expectations and content quality.

        Ensure your suggestions are detailed, practical, and tailored to the specific strengths and weaknesses identified in your analysis.
        """

    def _parse_suggestions(self, suggestions):
        creator_feedback = {}
        evaluator_feedback = {}
        current_section = None
        current_criterion = None

        for line in suggestions.split('\n'):
            line = line.strip()
            if line.startswith("For the content creator:"):
                current_section = "creator"
            elif line.startswith("For the evaluator:"):
                current_section = "evaluator"
            elif line in EVALUATION_CRITERIA:
                current_criterion = line
            elif current_section and current_criterion:
                if current_section == "creator":
                    creator_feedback.setdefault(current_criterion, []).append(line)
                else:
                    evaluator_feedback.setdefault(current_criterion, []).append(line)

        return creator_feedback, evaluator_feedback