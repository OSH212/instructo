from utils.api_handler import api
from config import FEEDBACK_MODEL
from utils.guidelines import EVALUATION_CRITERIA
from utils.memory import memory

import logging

logger = logging.getLogger(__name__)

class FeedbackAgent:
    def __init__(self):
        self.model = FEEDBACK_MODEL
        self.system_message = (
            "You are an AI improvement specialist with expertise in content creation, evaluation, and system optimization. "
            "Your goal is to provide insightful analysis and actionable feedback to enhance AI performance."
        )

    def analyze_interaction(self, recent_iterations, prompt, content, evaluation, user_eval_content, user_feedback_evaluator):
        relevant_iterations = memory.get_relevant_iterations(prompt)

        feedback_prompt = self._generate_feedback_prompt(recent_iterations, relevant_iterations, prompt, content, evaluation, user_eval_content, user_feedback_evaluator)

        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": feedback_prompt}
        ]

        response = api.get_completion(self.model, messages)
        if response and 'choices' in response:
            feedback = response['choices'][0]['message']['content'].strip()
            return self._parse_feedback(feedback)
        return None

    def _generate_feedback_prompt(self, recent_iterations, relevant_iterations, prompt, content, evaluation, user_eval_content, user_feedback_evaluator):
        context = "\n".join([f"Iteration {i}: {iter['content'][:100]}..." for i, iter in enumerate(recent_iterations)])

        relevant_context = "\n".join([
            f"Relevant Iteration (Score: {iter['relevance_score']:.2f}):\n"
            f"Content: {iter['content'][:100]}...\n"
            f"AI Evaluation: {str(iter['ai_evaluation'])[:100]}...\n"
            f"User Evaluation: {str(iter['user_evaluation_content'])[:100]}..."
            for iter in relevant_iterations
        ])

        return f"""
        Analyze the following interaction:

        Context of recent iterations:
        {context}

        Relevant previous iterations:
        {relevant_context}

        Current Iteration:
        Original Prompt: {prompt}
        Generated Content: {content}
        AI Evaluation: {evaluation}
        User Evaluation for Content: {user_eval_content}
        User Feedback for Evaluator: {user_feedback_evaluator}

        Provide a comprehensive analysis and actionable feedback in the following structure in markdown: 
        
        ### [###Overall Analysis###]
        (Provide a brief overall analysis of the interaction, including major discrepancies between AI and user evaluations, and how it compares to relevant previous iterations)
        
        ### [###Feedback for Content Creator###]
        (Under the 'Feedback for Content Creator section': For each criterion - and based on the AI and user evaluations, provide /10 rating as well as specific, actionable feedback for the content creator. If no improvement is needed, explicitly state why. Consider the performance in relevant previous iterations when providing feedback.)
        
        ### [###Feedback for Evaluator###]
        (Provide specific, actionable feedback for the evaluator based on the user's feedback and your analysis. If no improvement is needed, explicitly state why. Consider the evaluator's performance in relevant previous iterations.)
        
        ### [###Improvements Needed###]
        (Explicitly state 'YES' if improvements are needed, or 'NO' if no improvements are necessary. Provide a brief explanation for your decision.)
        Note: Consider improvements necessary until the content rating is 10/10 across all criteria and both the user and evaluator are in full agreement. However, use your judgment to assess the overall quality and progress.
        
        Ensure you address all of the following criteria in the Content Creator section:
        {', '.join(EVALUATION_CRITERIA.keys())} and include details on how you used the context of recent iterations and relevant previous iterations in your assessment and feedback.

        For each criterion, provide at least one specific suggestion for improvement or explicitly state why no improvement is needed.
        """

    def _parse_feedback(self, feedback):
        sections = feedback.split('###')
        parsed_feedback = {
            'improvements_needed': '',
            'everything': '',
        }

        for section in sections:
            section = section.strip()
            if section:
                lines = section.split('\n', 1)
                if len(lines) > 1:
                    header, content = lines
                    header = header.lower().strip()
                    content = content.strip()

                    if 'improvements needed' in header:
                        parsed_feedback['improvements_needed'] = content
                    else:
                        parsed_feedback['everything'] += f"### {header.capitalize()}\n{content}\n\n"

        # Removing "Improvements Needed" section from 'everything'
        parsed_feedback['everything'] = parsed_feedback['everything'].replace(f"### Improvements Needed\n{parsed_feedback['improvements_needed']}\n\n", "")

        return parsed_feedback

    def incorporate_user_feedback(self, previous_feedback, additional_feedback):
        incorporation_prompt = f"""
        Previous analysis:
        {previous_feedback.get('overall_analysis', '')}

        Additional user feedback:
        {additional_feedback}

        Please incorporate the additional user feedback into your previous analysis and feedback. Update your recommendations for both the content creator and evaluator based on this new information.

        Provide your updated feedback in the following structure:
        
        ### [###Overall Analysis###]
        (Updated overall analysis incorporating the new feedback)
        
        ### [###Feedback for Content Creator###]
        (Under the 'Feedback for Content Creator section': For each criterion, provide updated specific, actionable feedback for the content creator, explicitly mentioning how the additional user feedback has been incorporated)
        
        ### [###Feedback for Evaluator###]
        (Provide updated specific, actionable feedback for the evaluator, explicitly mentioning how the additional user feedback has been incorporated)
        
        ### [###Improvements Needed###]
        (State 'YES' or 'NO', and provide a brief explanation for your decision, considering the additional feedback)
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