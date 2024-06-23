from utils.api_handler import api
from config import FEEDBACK_MODEL
from utils.guidelines import EVALUATION_CRITERIA



class FeedbackAgent:
    def __init__(self):
        self.model = FEEDBACK_MODEL
        self.system_message = (
            "You are an AI improvement specialist with expertise in content creation, evaluation, and system optimization. "
            "Your goal is to provide insightful analysis and actionable feedback to enhance AI performance."
        )

    # def analyze_interaction(self, content, evaluation, user_eval):
    #     feedback_prompt = self._generate_feedback_prompt(content, evaluation, user_eval)
    #     messages = [
    #         {"role": "system", "content": self.system_message},
    #         {"role": "user", "content": feedback_prompt}
    #     ]

    #     response = api.get_completion(self.model, messages)
    #     if response and 'choices' in response:
    #         feedback = response['choices'][0]['message']['content'].strip()
    #         return self._parse_feedback(feedback)
    #     return None
    

    def analyze_interaction(self, content, evaluation, user_eval_content, user_feedback_evaluator):
        feedback_prompt = self._generate_feedback_prompt(content, evaluation, user_eval_content, user_feedback_evaluator)
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": feedback_prompt}
        ]

        response = api.get_completion(self.model, messages)
        if response and 'choices' in response:
            feedback = response['choices'][0]['message']['content'].strip()
            return self._parse_feedback(feedback)
        return None

    def _generate_feedback_prompt(self, content, evaluation, user_eval_content, user_feedback_evaluator):
        return f"""
        Analyze the following interaction:

        Original Prompt: {content['prompt']}
        Generated Content: {content['content']}
        AI Evaluation: {evaluation}
        User Evaluation for Content: {user_eval_content}
        User Feedback for Evaluator: {user_feedback_evaluator}

        Provide a comprehensive analysis and actionable feedback in the following structure:

        [Overall Analysis]
        (Provide a brief overall analysis of the interaction, including major discrepancies between AI and user evaluations)

        [Feedback for Content Creator]
        (For each criterion, provide specific, actionable feedback for the content creator. If no improvement is needed, explicitly state why.)

        [Feedback for Evaluator]
        (Provide specific, actionable feedback for the evaluator based on the user's feedback and your analysis. If no improvement is needed, explicitly state why.)

        [Conclusion]
        (Conclude with whether improvements are needed overall and a brief summary)

        Ensure you address all of the following criteria in the Content Creator section:
        {', '.join(EVALUATION_CRITERIA.keys())}

        For each criterion, provide at least one specific suggestion for improvement or explicitly state why no improvement is needed.
        """



    def _parse_feedback(self, feedback):
        sections = feedback.split('[Overall Analysis]')
        overall_analysis = sections[-1].split('[Feedback for Content Creator]')[0].strip() if len(sections) > 1 else feedback.strip()
        
        content_section = feedback.split('[Feedback for Content Creator]')[-1].split('[Feedback for Evaluator]')[0] if '[Feedback for Content Creator]' in feedback else ''
        evaluator_section = feedback.split('[Feedback for Evaluator]')[-1].split('[Conclusion]')[0] if '[Feedback for Evaluator]' in feedback else ''
        
        conclusion = feedback.split('[Conclusion]')[-1].strip() if '[Conclusion]' in feedback else ''
        
        content_feedback = self._extract_criterion_feedback(content_section)
        evaluator_feedback = self._extract_criterion_feedback(evaluator_section)
        
        improvements_needed = "improvements are needed" in feedback.lower()

        return {
            'overall_analysis': overall_analysis,
            'content_feedback': content_feedback,
            'evaluator_feedback': evaluator_feedback,
            'improvements_needed': improvements_needed,
            'conclusion': conclusion
        }

    def _extract_criterion_feedback(self, feedback_text):
        feedback = {criterion: [] for criterion in EVALUATION_CRITERIA}
        current_criterion = None

        for line in feedback_text.split('\n'):
            line = line.strip()
            if any(criterion in line for criterion in EVALUATION_CRITERIA):
                current_criterion = next(criterion for criterion in EVALUATION_CRITERIA if criterion in line)
            elif current_criterion and line:  # Check if line is not empty
                if line.startswith('-') or line.startswith('•') or (line[0].isdigit() if line else False):
                    feedback[current_criterion].append(line.lstrip('- •').strip())

        # Remove empty feedback
        feedback = {k: v for k, v in feedback.items() if v}

        return feedback

    def incorporate_user_feedback(self, previous_feedback, additional_feedback):
        incorporation_prompt = f"""
        Previous analysis:
        {previous_feedback['overall_analysis']}

        Additional user feedback:
        {additional_feedback}

        Please incorporate the additional user feedback into your previous analysis and feedback. Update your recommendations for both the content creator and evaluator based on this new information.

        Provide your updated feedback in the same structure as before:
        [Overall Analysis]
        [Feedback for Content Creator]
        [Feedback for Evaluator]
        [Conclusion]
        """

        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": incorporation_prompt}
        ]

        response = api.get_completion(self.model, messages)
        if response and 'choices' in response:
            updated_feedback = response['choices'][0]['message']['content']
            return self._parse_feedback(updated_feedback)
        return previous_feedback