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
        # logger.debug("FeedbackAgent: Analyzing interaction")
        # logger.debug(f"Iteration(s): {recent_iterations}")
        # logger.debug(f"Prompt: {prompt[:100]}...")
        # logger.debug(f"Content: {content[:100]}...")
        # logger.debug(f"Evaluation: {evaluation}")
        # logger.debug(f"User Eval Content: {user_eval_content}")
        # logger.debug(f"User Feedback Evaluator: {user_feedback_evaluator}")
    
        #feedback_prompt = self._generate_feedback_prompt(prompt, content, evaluation, user_eval_content, user_feedback_evaluator)
        feedback_prompt = self._generate_feedback_prompt(recent_iterations, prompt, content, evaluation, user_eval_content, user_feedback_evaluator)
        #logger.debug(f"Generated feedback prompt: {feedback_prompt[:200]}...")

        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": feedback_prompt}
        ]

        #logger.debug("FeedbackAgent: Sending request to API")
        response = api.get_completion(self.model, messages)
        #logger.debug(f"API Response: {response}")
        if response and 'choices' in response:
            feedback = response['choices'][0]['message']['content'].strip()
            #logger.debug("FeedbackAgent: Parsing feedback")
            #logger.debug(f"Raw feedback: {feedback[:200]}...")
            return self._parse_feedback(feedback)
        #logger.warning("FeedbackAgent: No valid response from API")
        return None

    def _generate_feedback_prompt(self, recent_iterations, prompt, content, evaluation, user_eval_content, user_feedback_evaluator):
        context = "\n".join([f"Iteration {i}: {iter['content'][:100]}..." for i, iter in enumerate(recent_iterations)])
        #logger.debug(f"Recent iterations retrieved: {len(recent_iterations)}")
        #context = "\n".join([f"Iteration {i+1}: {iter.get('content', '')[:100]}..." for i, iter in enumerate(recent_iterations)])
        #logger.debug(f"Context: {context}")
        
        return f"""
        Analyze the following interaction:

        Context of recent iterations:
        {context}

        Current Iteration:
        Original Prompt: {prompt}
        Generated Content: {content}
        AI Evaluation: {evaluation}
        User Evaluation for Content: {user_eval_content}
        User Feedback for Evaluator: {user_feedback_evaluator}

        Provide a comprehensive analysis and actionable feedback in the following structure in markdown: 
        \n
        ### [###Overall Analysis###]
        (Provide a brief overall analysis of the interaction, including major discrepancies between AI and user evaluations)
        \n
        ### [###Feedback for Content Creator###]
        (Under the 'Feedback for Content Creator section': For each criterion - and based on the ai and user evaluations, provide /10 rating as well as specific, actionable feedback for the content creator. If no improvement is needed, explicitly state why.)
        \n
        ### [###Feedback for Evaluator###]
        (Provide specific, actionable feedback for the evaluator based on the user's feedback and your analysis. If no improvement is needed, explicitly state why.)
        \n
        ### [###Improvements Needed###]
        (Explicitly state 'YES' if improvements are needed, or 'NO' if no improvements are necessary. Provide a brief explanation for your decision.)
        Note: Consider improvements necessary until the content rating is 10/10 across all criteria and both the user and evaluator are in full agreement. However, use your judgment to assess the overall quality and progress.
        \n
        Ensure you address all of the following criteria in the Content Creator section:
        {', '.join(EVALUATION_CRITERIA.keys())} and include details on how you used the context of recent iterations in your assessment and feedback.

        For each criterion, provide at least one specific suggestion for improvement or explicitly state why no improvement is needed.
        """

    def _parse_feedback(self, feedback):
        #logger.debug(f"Parsing feedback: {feedback[:200]}...")
        sections = feedback.split('###')
        parsed_feedback = {
            #'overall_analysis': '',
            #'content_creator_feedback': {},
            #'evaluator_feedback': '',
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

                    # if 'overall analysis' in header:
                    #     parsed_feedback['overall_analysis'] = content
                    # if 'feedback for content creator' in header:
                    #     parsed_feedback['content_creator_feedback'] = content
                    #     # for line in content.split('\n'):
                    #     #     if ':' in line:
                    #     #         key, value = line.split(':', 1)
                    #     #         parsed_feedback['content_creator_feedback'][key.strip()] = value.strip()
                    # if 'feedback for evaluator' in header:
                    #     parsed_feedback['evaluator_feedback'] = content
                    if 'improvements needed' in header:
                        parsed_feedback['improvements_needed'] = content
                    else:
                        parsed_feedback['everything'] += f"### {header.capitalize()}\n{content}\n\n"
                        
        # Removng "Improvements Needed" section from 'everything'
        parsed_feedback['everything'] = parsed_feedback['everything'].replace(f"### Improvements Needed\n{parsed_feedback['improvements_needed']}\n\n", "")

        #logger.debug(f"Parsed feedback: {parsed_feedback}")
        return parsed_feedback

    def incorporate_user_feedback(self, previous_feedback, additional_feedback):
        incorporation_prompt = f"""
        Previous analysis:
        {previous_feedback.get('overall_analysis', '')}

        Additional user feedback:
        {additional_feedback}

        Please incorporate the additional user feedback into your previous analysis and feedback. Update your recommendations for both the content creator and evaluator based on this new information.

        Provide your updated feedback in the following structure:
        \n
        ### [###Overall Analysis###]
        (Updated overall analysis incorporating the new feedback)
        \n
        ### [###Feedback for Content Creator###]
        (Under the 'Feedback for Content Creator section': For each criterion, provide updated specific, actionable feedback for the content creator, explicitly mentioning how the additional user feedback has been incorporated)
        \n
        ### [###Feedback for Evaluator###]
        (Provide updated specific, actionable feedback for the evaluator, explicitly mentioning how the additional user feedback has been incorporated)
        \n
        ### [###Improvements Needed###]
        (State 'YES' or 'NO', and provide a brief explanation for your decision, considering the additional feedback)\n
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