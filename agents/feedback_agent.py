from utils.api_handler import api
from config import FEEDBACK_MODEL
from utils.guidelines import EVALUATION_CRITERIA

import logging

logger = logging.getLogger(__name__)

class FeedbackAgent:
    def __init__(self):
        self.model = FEEDBACK_MODEL
        self.system_message = (
            "You are an AI improvement specialist with expertise in content creation, evaluation, and system optimization. "
            "Your goal is to provide insightful analysis and actionable feedback to enhance AI performance."
        )

    def analyze_interaction(self, content, evaluation, user_eval_content, user_feedback_evaluator):
        logger.debug("FeedbackAgent: Analyzing interaction")
        feedback_prompt = self._generate_feedback_prompt(content, evaluation, user_eval_content, user_feedback_evaluator)
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": feedback_prompt}
        ]

        logger.debug("FeedbackAgent: Sending request to API")
        response = api.get_completion(self.model, messages)
        if response and 'choices' in response:
            feedback = response['choices'][0]['message']['content'].strip()
            logger.debug("FeedbackAgent: Parsing feedback")
            return self._parse_feedback(feedback)
        logger.warning("FeedbackAgent: No valid response from API")
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

        [Improvements Needed]
        (Explicitly state 'YES' if improvements are needed, or 'NO' if no improvements are necessary. Provide a brief explanation for your decision.)

        Ensure you address all of the following criteria in the Content Creator section:
        {', '.join(EVALUATION_CRITERIA.keys())}

        For each criterion, provide at least one specific suggestion for improvement or explicitly state why no improvement is needed.
        """

    def _parse_feedback(self, feedback):
        sections = feedback.split('[Overall Analysis]')
        overall_analysis = sections[-1].split('[Feedback for Content Creator]')[0].strip() if len(sections) > 1 else feedback.strip()
        
        #content_creator_feedback = feedback.split('[Feedback for Content Creator]')[-1].split('[Feedback for Evaluator]')[0].strip()
        #evaluator_feedback = feedback.split('[Feedback for Evaluator]')[-1].split('[Improvements Needed]')[0].strip()
        
        #improvements_section = feedback.split('[Improvements Needed]')[-1].strip()
        #improvements_needed = 'YES' in improvements_section.upper()
        #improvements_explanation = improvements_section.split('\n', 1)[-1].strip() if '\n' in improvements_section else ''

        return {
            'overall_analysis': overall_analysis,
            #'content_creator_feedback': content_creator_feedback,
            #'evaluator_feedback': evaluator_feedback,
            #'improvements_needed': improvements_needed,
            #'improvements_explanation': improvements_explanation,
        }
    

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
        [Improvements Needed]
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