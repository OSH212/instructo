

# ========================
# File: config.py
# ========================

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('PERPLEXITY_API_KEY')
API_URL = os.getenv('PERPLEXITY_API_URL', 'https://api.perplexity.ai/chat/completions')

CONTENT_CREATOR_MODEL = "llama-3-sonar-large-32k-online"
EVALUATOR_MODEL = "llama-3-sonar-large-32k-online"
FEEDBACK_MODEL = "llama-3-sonar-large-32k-chat"

MEMORY_FILE = 'memory.yaml'
MAX_MEMORY_SIZE = 100

# Evaluation threshold
LOW_SCORE_THRESHOLD = 7

# ========================
# File: main.py
# ========================

from agents.content_creator import ContentCreator
from agents.evaluator import Evaluator
from models.evaluation import UserEvaluation
from utils.memory import memory
from utils.api_handler import api
from config import FEEDBACK_MODEL
import traceback
from colorama import Fore, Style, init
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from utils.guidelines import EVALUATION_CRITERIA
from agents.feedback_agent import FeedbackAgent

def apply_feedback(creator, evaluator, creator_feedback, evaluator_feedback):
    if creator_feedback:
        creator.learn(creator_feedback)
    if evaluator_feedback:
        evaluator.learn(evaluator_feedback)


def handle_command(command, prompt, creator, evaluator, feedback_agent):
    if command == 'quit':
        return False
    elif command == 'new':
        return True
    elif command == 'restart':
        print("\nRestarting interaction with the same prompt.")
        run_interaction(prompt, creator, evaluator, feedback_agent)
    else:
        print("Invalid command. Please try again.")
    return True

def parse_evaluation(evaluation):
    if isinstance(evaluation, str):
        return {'full_evaluation': evaluation}
    return evaluation


def run_interaction(prompt, creator, evaluator, feedback_agent):
    console = Console()
    
    while True:
        # Content creation
        content = creator.create_content(prompt)
        console.print(Panel(content, title="Generated Content", expand=False), style="cyan")

        # AI Evaluation
        evaluation = evaluator.evaluate_content(content, prompt)
        display_evaluation(evaluation, console)

        # User Evaluation
        user_eval = get_user_evaluation(console)

        # Store interaction in memory
        memory.add_interaction(prompt, content, evaluation, user_eval)

        # Feedback Agent Analysis
        feedback = feedback_agent.analyze_interaction({'prompt': prompt, 'content': content}, evaluation, user_eval)
        display_feedback(feedback, console)

        while True:
            decision = Prompt.ask(
                "What would you like to do?",
                choices=["continue", "disagree", "new", "quit"],
                default="continue"
            )

            if decision == "continue":
                if feedback['improvements_needed']:
                    creator.learn(feedback['content_feedback'])
                    evaluator.learn(feedback['evaluator_feedback'])
                    break
                else:
                    console.print("No further improvements needed. Starting a new interaction.")
                    return True
            elif decision == "disagree":
                additional_feedback = get_additional_feedback(console)
                feedback = feedback_agent.incorporate_user_feedback(feedback, additional_feedback)
                display_feedback(feedback, console)
            elif decision == "new":
                return True
            elif decision == "quit":
                return False
        
        if decision == "quit":
            break

    return True


def display_feedback(feedback, console):
    console.print("\n[bold magenta]Feedback Agent Analysis:[/bold magenta]")
    
    if 'overall_analysis' in feedback:
        console.print(Panel(feedback['overall_analysis'], title="Overall Analysis", expand=False))

    console.print("\n[bold cyan]Feedback for Content Creator:[/bold cyan]")
    if 'content_feedback' in feedback:
        for criterion, suggestions in feedback['content_feedback'].items():
            console.print(f"\n[underline]{criterion}:[/underline]")
            for suggestion in suggestions:
                console.print(f"- {suggestion}")
    
    console.print("\n[bold yellow]Feedback for Evaluator:[/bold yellow]")
    if 'evaluator_feedback' in feedback:
        for criterion, suggestions in feedback['evaluator_feedback'].items():
            console.print(f"\n[underline]{criterion}:[/underline]")
            for suggestion in suggestions:
                console.print(f"- {suggestion}")

    if 'conclusion' in feedback:
        console.print("\n[bold green]Conclusion:[/bold green]")
        console.print(Panel(feedback['conclusion'], expand=False))

    console.print(f"\n[bold]Improvements needed:[/bold] {'Yes' if feedback.get('improvements_needed', False) else 'No'}")

def get_additional_feedback(console):
    console.print("\n[bold]Please provide additional feedback for improvement:[/bold]")
    return Prompt.ask("Your feedback")

def display_evaluation(evaluation, console):
    console.print("\n[bold yellow]AI Evaluation:[/bold yellow]")
    if isinstance(evaluation, str):
        console.print(evaluation)
    elif isinstance(evaluation, dict):
        for criterion, details in evaluation.items():
            console.print(f"\n[cyan]{criterion}:[/cyan]")
            if isinstance(details, dict):
                if 'score' in details:
                    console.print(f"Score: {details['score']}")
                if 'explanation' in details:
                    console.print(f"Explanation: {details['explanation']}")
                if 'suggestions' in details and details['suggestions']:
                    console.print("Suggestions:")
                    for suggestion in details['suggestions']:
                        console.print(f"- {suggestion}")
            else:
                console.print(details)
    else:
        console.print("Error: Unexpected evaluation format")

def get_user_evaluation(console):
    user_scores = {}
    user_feedbacks = {}
    
    console.print("\n[bold]Please rate and provide feedback for each criterion:[/bold]")
    
    table = Table(title="Evaluation Criteria", box=box.ROUNDED)
    table.add_column("Criterion", style="cyan")
    table.add_column("Score (0-10)", style="magenta")
    table.add_column("Feedback", style="green")

    for criterion in EVALUATION_CRITERIA.keys():
        while True:
            score = Prompt.ask(f"Rate the [cyan]{criterion}[/cyan] (0-10)", default="5")
            try:
                score = float(score)
                if 0 <= score <= 10:
                    break
                else:
                    console.print("[red]Please enter a number between 0 and 10.[/red]")
            except ValueError:
                console.print("[red]Invalid input. Please enter a number.[/red]")
        
        feedback = Prompt.ask(f"Provide feedback for [cyan]{criterion}[/cyan]")
        
        user_scores[criterion] = score
        user_feedbacks[criterion] = feedback
        
        table.add_row(criterion, str(score), feedback)

    console.print(table)

    return UserEvaluation(user_scores, user_feedbacks)

def main():
    creator = ContentCreator()
    evaluator = Evaluator()
    feedback_agent = FeedbackAgent()
    
    memory.load_from_file()  # Load previous interactions if available
    
    try:
        while True:
            prompt = input("Enter a content prompt (or 'quit' to exit): ")
            if prompt.lower() == 'quit':
                break

            continue_main_loop = run_interaction(prompt, creator, evaluator, feedback_agent)
            if not continue_main_loop:
                break

    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())
    finally:
        memory.save_to_file()  # Save the latest interaction before exiting

if __name__ == "__main__":
    main()

# ========================
# File: combined_python_files.py
# ========================



# ========================
# File: config.py
# ========================

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('PERPLEXITY_API_KEY')
API_URL = os.getenv('PERPLEXITY_API_URL', 'https://api.perplexity.ai/chat/completions')

CONTENT_CREATOR_MODEL = "llama-3-sonar-large-32k-online"
EVALUATOR_MODEL = "llama-3-sonar-large-32k-online"
FEEDBACK_MODEL = "llama-3-sonar-large-32k-chat"

MEMORY_FILE = 'memory.yaml'
MAX_MEMORY_SIZE = 100

# Evaluation threshold
LOW_SCORE_THRESHOLD = 7

# ========================
# File: main.py
# ========================

from agents.content_creator import ContentCreator
from agents.evaluator import Evaluator
from models.evaluation import UserEvaluation
from utils.memory import memory
from utils.api_handler import api
from config import FEEDBACK_MODEL
import traceback
from colorama import Fore, Style, init
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from utils.guidelines import EVALUATION_CRITERIA
from agents.feedback_agent import FeedbackAgent

def apply_feedback(creator, evaluator, creator_feedback, evaluator_feedback):
    if creator_feedback:
        creator.learn(creator_feedback)
    if evaluator_feedback:
        evaluator.learn(evaluator_feedback)


def handle_command(command, prompt, creator, evaluator, feedback_agent):
    if command == 'quit':
        return False
    elif command == 'new':
        return True
    elif command == 'restart':
        print("\nRestarting interaction with the same prompt.")
        run_interaction(prompt, creator, evaluator, feedback_agent)
    else:
        print("Invalid command. Please try again.")
    return True

def parse_evaluation(evaluation):
    if isinstance(evaluation, str):
        return {'full_evaluation': evaluation}
    return evaluation


def run_interaction(prompt, creator, evaluator, feedback_agent):
    console = Console()
    
    while True:
        # Content creation
        content = creator.create_content(prompt)
        console.print(Panel(content, title="Generated Content", expand=False), style="cyan")

        # AI Evaluation
        evaluation = evaluator.evaluate_content(content, prompt)
        display_evaluation(evaluation, console)

        # User Evaluation
        user_eval = get_user_evaluation(console)

        # Store interaction in memory
        memory.add_interaction(prompt, content, evaluation, user_eval)

        # Feedback Agent Analysis
        feedback = feedback_agent.analyze_interaction({'prompt': prompt, 'content': content}, evaluation, user_eval)
        display_feedback(feedback, console)

        while True:
            decision = Prompt.ask(
                "What would you like to do?",
                choices=["continue", "disagree", "new", "quit"],
                default="continue"
            )

            if decision == "continue":
                if feedback['improvements_needed']:
                    creator.learn(feedback['content_feedback'])
                    evaluator.learn(feedback['evaluator_feedback'])
                    break
                else:
                    console.print("No further improvements needed. Starting a new interaction.")
                    return True
            elif decision == "disagree":
                additional_feedback = get_additional_feedback(console)
                feedback = feedback_agent.incorporate_user_feedback(feedback, additional_feedback)
                display_feedback(feedback, console)
            elif decision == "new":
                return True
            elif decision == "quit":
                return False
        
        if decision == "quit":
            break

    return True


def display_feedback(feedback, console):
    console.print("\n[bold magenta]Feedback Agent Analysis:[/bold magenta]")
    
    if 'overall_analysis' in feedback:
        console.print(Panel(feedback['overall_analysis'], title="Overall Analysis", expand=False))

    console.print("\n[bold cyan]Feedback for Content Creator:[/bold cyan]")
    if 'content_feedback' in feedback:
        for criterion, suggestions in feedback['content_feedback'].items():
            console.print(f"\n[underline]{criterion}:[/underline]")
            for suggestion in suggestions:
                console.print(f"- {suggestion}")
    
    console.print("\n[bold yellow]Feedback for Evaluator:[/bold yellow]")
    if 'evaluator_feedback' in feedback:
        for criterion, suggestions in feedback['evaluator_feedback'].items():
            console.print(f"\n[underline]{criterion}:[/underline]")
            for suggestion in suggestions:
                console.print(f"- {suggestion}")

    if 'conclusion' in feedback:
        console.print("\n[bold green]Conclusion:[/bold green]")
        console.print(Panel(feedback['conclusion'], expand=False))

    console.print(f"\n[bold]Improvements needed:[/bold] {'Yes' if feedback.get('improvements_needed', False) else 'No'}")

def get_additional_feedback(console):
    console.print("\n[bold]Please provide additional feedback for improvement:[/bold]")
    return Prompt.ask("Your feedback")

def display_evaluation(evaluation, console):
    console.print("\n[bold yellow]AI Evaluation:[/bold yellow]")
    if isinstance(evaluation, str):
        console.print(evaluation)
    elif isinstance(evaluation, dict):
        for criterion, details in evaluation.items():
            console.print(f"\n[cyan]{criterion}:[/cyan]")
            if isinstance(details, dict):
                if 'score' in details:
                    console.print(f"Score: {details['score']}")
                if 'explanation' in details:
                    console.print(f"Explanation: {details['explanation']}")
                if 'suggestions' in details and details['suggestions']:
                    console.print("Suggestions:")
                    for suggestion in details['suggestions']:
                        console.print(f"- {suggestion}")
            else:
                console.print(details)
    else:
        console.print("Error: Unexpected evaluation format")

def get_user_evaluation(console):
    user_scores = {}
    user_feedbacks = {}
    
    console.print("\n[bold]Please rate and provide feedback for each criterion:[/bold]")
    
    table = Table(title="Evaluation Criteria", box=box.ROUNDED)
    table.add_column("Criterion", style="cyan")
    table.add_column("Score (0-10)", style="magenta")
    table.add_column("Feedback", style="green")

    for criterion in EVALUATION_CRITERIA.keys():
        while True:
            score = Prompt.ask(f"Rate the [cyan]{criterion}[/cyan] (0-10)", default="5")
            try:
                score = float(score)
                if 0 <= score <= 10:
                    break
                else:
                    console.print("[red]Please enter a number between 0 and 10.[/red]")
            except ValueError:
                console.print("[red]Invalid input. Please enter a number.[/red]")
        
        feedback = Prompt.ask(f"Provide feedback for [cyan]{criterion}[/cyan]")
        
        user_scores[criterion] = score
        user_feedbacks[criterion] = feedback
        
        table.add_row(criterion, str(score), feedback)

    console.print(table)

    return UserEvaluation(user_scores, user_feedbacks)

def main():
    creator = ContentCreator()
    evaluator = Evaluator()
    feedback_agent = FeedbackAgent()
    
    memory.load_from_file()  # Load previous interactions if available
    
    try:
        while True:
            prompt = input("Enter a content prompt (or 'quit' to exit): ")
            if prompt.lower() == 'quit':
                break

            continue_main_loop = run_interaction(prompt, creator, evaluator, feedback_agent)
            if not continue_main_loop:
                break

    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())
    finally:
        memory.save_to_file()  # Save the latest interaction before exiting

if __name__ == "__main__":
    main()

# ========================
# File: agents/feedback_agent.py
# ========================

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

    def analyze_interaction(self, content, evaluation, user_eval):
        feedback_prompt = self._generate_feedback_prompt(content, evaluation, user_eval)
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": feedback_prompt}
        ]

        response = api.get_completion(self.model, messages)
        if response and 'choices' in response:
            feedback = response['choices'][0]['message']['content'].strip()
            return self._parse_feedback(feedback)
        return None

    def _generate_feedback_prompt(self, content, evaluation, user_eval):
        return f"""
        Analyze the following interaction:

        Original Prompt: {content['prompt']}
        Generated Content: {content['content']}
        AI Evaluation: {evaluation}
        User Evaluation: {user_eval}

        Provide a comprehensive analysis and actionable feedback in the following structure:

        [Overall Analysis]
        (Provide a brief overall analysis of the interaction, including major discrepancies between AI and user evaluations)

        [Feedback for Content Creator]
        (For each criterion, provide specific, actionable feedback for the content creator. If no improvement is needed, explicitly state why.)

        [Feedback for Evaluator]
        (For each criterion, provide specific, actionable feedback for the evaluator. If no improvement is needed, explicitly state why.)

        [Conclusion]
        (Conclude with whether improvements are needed overall and a brief summary)

        Ensure you address all of the following criteria in both the Content Creator and Evaluator sections:
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

# ========================
# File: agents/content_creator.py
# ========================

from utils.api_handler import api
from utils.memory import memory
from config import CONTENT_CREATOR_MODEL

class ContentCreator:
    def __init__(self):
        self.model = CONTENT_CREATOR_MODEL
        self.system_message = (
            "You are an expert content creator with extensive knowledge across various subjects and exceptional linguistic proficiency.\n\n"
            "Your task is to generate high-quality, informative, and engaging content based on given prompts.\n"
            "Core Responsibilities:\n"
            "1. Research and Fact-Checking:\n"
            "   - Utilize web search capabilities to complement and verify your knowledge\n"
            "   - Ensure all information is current, accurate, and from reliable sources\n"
            "2. Content Creation:\n"
            "   - Generate comprehensive, well-researched content\n"
            "   - Maintain unwavering focus on the given prompt and objective\n"
            "   - Strive for the highest level of thoroughness in every aspect\n"
            "3. Linguistic Excellence:\n"
            "   - Demonstrate mastery in grammar, syntax, and style\n"
            "   - Employ precise vocabulary and appropriate register\n"
            "   - Ensure impeccable coherence and cohesion throughout\n"
            "4. Structural Integrity:\n"
            "   - Implement a logical structure: clear introduction, well-developed body, and conclusive ending\n"
            "   - Use smooth transitions for seamless idea flow\n"
            "   - Conclude with a summary and, when applicable, a call to action or future outlook\n"
            "5. Content Enhancement:\n"
            "   - Incorporate relevant examples, data, sources and/or case studies to substantiate points\n"
            "   - Address potential counterarguments or limitations when appropriate\n"
            "   - Balance different perspectives to maintain objectivity\n\n"
            "Guidelines:\n"
            "- Prioritize clarity, exhaustiveness, and factual accuracy\n"
            "- Tailor content meticulously to the specific topic and audience\n"
            "- Maintain strict relevance to the given objective\n"
            "- Present information objectively, avoiding any bias\n"
            "- Strive for a balanced presentation of ideas and viewpoints\n"
            "- Ensure content is informative, engaging, and thought-provoking\n\n"
            "Your goal is to produce content of the highest caliber, demonstrating thorough research, linguistic mastery, and unwavering adherence to the given objective."
        )
        self.feedback = None


    def create_content(self, prompt):
        context = self._generate_context(prompt)
        
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": context}
        ]
        response = api.get_completion(self.model, messages)
        if response and 'choices' in response:
            content = response['choices'][0]['message']['content']
            if self.feedback:
                content += "\n\nFeedback Incorporation:\n"
                content += self._explain_feedback_incorporation()
            return content
        else:
            return "I apologize, but I couldn't generate content at this time. Please try again later."

    def _generate_context(self, prompt):
        context = f"Prompt: {prompt}\n\n"
        if self.feedback:
            context += "Please incorporate the following feedback into your content:\n"
            for criterion, suggestions in self.feedback.items():
                context += f"\n{criterion}:\n"
                context += "\n".join(f"- {suggestion}" for suggestion in suggestions)
                context += "\n\nGenerate the content based on the prompt and incorporate the feedback. After the main content, explain how you incorporated it in your new iteration.\n\n"
        else:
             context += "Please generate content based on the given prompt."
        return context

    def _explain_feedback_incorporation(self):
        explanation = "Here's how I incorporated the feedback:\n"
        for criterion, suggestions in self.feedback.items():
            explanation += f"\n{criterion}:\n"
            for suggestion in suggestions:
                explanation += f"- {suggestion}: [Explain how this suggestion was incorporated]\n"
        return explanation

    def learn(self, feedback):
        self.feedback = feedback

# ========================
# File: agents/__init__.py
# ========================

from .content_creator import ContentCreator
from .evaluator import Evaluator

# ========================
# File: agents/evaluator.py
# ========================

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
            for criterion, suggestions in self.feedback.items():
                evaluation_prompt += f"\n{criterion}:\n"
                evaluation_prompt += "\n".join(f"- {suggestion}" for suggestion in suggestions)
                evaluation_prompt += "\n\nAfter your evaluation, explain how you incorporated each piece of feedback."
        
        messages = [            {"role": "system", "content": self.system_message},
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

    def _explain_feedback_incorporation(self):
        explanation = "Here's how I incorporated the feedback into my evaluation:\n"
        for criterion, suggestions in self.feedback.items():
            explanation += f"\n{criterion}:\n"
            for suggestion in suggestions:
                explanation += f"- {suggestion}: [Explain how this suggestion was incorporated into the evaluation]\n"
        return explanation

# ========================
# File: utils/api_handler.py
# ========================

import requests
from config import API_KEY, API_URL

class PerplexityAPI:
    def __init__(self):
        self.url = API_URL
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {API_KEY}"
        }

    def get_completion(self, model, messages, temperature=0.1):
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        try:
            response = requests.post(self.url, json=payload, headers=self.headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
            return None

api = PerplexityAPI()

# ========================
# File: utils/memory.py
# ========================

import os 
import yaml
from collections import deque
from models.evaluation import UserEvaluation
from datetime import datetime

class Memory:
    def __init__(self, max_size=100):
        self.interactions = deque(maxlen=max_size)
        self.filename = f'memory_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml'

    def add_interaction(self, prompt, content, ai_evaluation, user_evaluation):
        timestamp = datetime.now().isoformat()
        self.interactions.append({
            'timestamp': timestamp,
            'prompt': prompt,
            'content': content,
            'ai_evaluation': ai_evaluation,
            'user_evaluation': {
                'score': user_evaluation.score,
                'feedback': user_evaluation.feedback
            }
        })

    def get_recent_interactions(self, n=5):
        return list(self.interactions)[-n:]

    def save_to_file(self):
        with open(self.filename, 'a') as f:
            yaml.dump([self.interactions[-1]], f)

    def load_from_file(self):
        try:
            files = [f for f in os.listdir() if f.startswith('memory_') and f.endswith('.yaml')]
            if not files:
                print("No existing memory files found. Starting with empty memory.")
                return

            latest_file = max(files)
            with open(latest_file, 'r') as f:
                loaded_data = yaml.safe_load(f)
                if loaded_data:
                    self.interactions = deque(
                        [{**interaction, 
                        'user_evaluation': UserEvaluation(
                            score=interaction['user_evaluation']['score'],
                            feedback=interaction['user_evaluation']['feedback']
                        )}
                        for interaction in loaded_data],
                        maxlen=self.interactions.maxlen
                    )
        except yaml.YAMLError as e:
            print(f"Error loading memory file: {e}")
        except Exception as e:
            print(f"Unexpected error loading memory file: {e}")

memory = Memory()

# ========================
# File: utils/__init__.py
# ========================

from .api_handler import PerplexityAPI
from .guidelines import EVALUATION_CRITERIA
from .memory import Memory

# ========================
# File: utils/guidelines.py
# ========================

EVALUATION_CRITERIA = {
    "Content Quality": {
        "description": "Assess the accuracy, depth, and relevance of the information presented.",
        "rubric": [
            "1-2: Significant errors, shallow treatment, or off-topic",
            "3-4: Some inaccuracies or lacks depth in key areas",
            "5-6: Generally accurate and relevant but could be more comprehensive",
            "7-8: Accurate, relevant, and fairly in-depth treatment",
            "9: Highly accurate, comprehensive, and insightful with minor room for improvement",
            "10: Perfect content quality, nothing more needed"
        ],
        "prompt": "Evaluate the accuracy, depth, and relevance of the content. Consider complexity of ideas, use of expert knowledge, and alignment with the given prompt/objective. Suggest areas for improvement or expansion."
    },
    "Critical Analysis and Argumentation": {
        "description": "Assess the level of critical thinking, insights, and quality of argumentation.",
        "rubric": [
            "1-2: Superficial analysis with poor argumentation",
            "3-4: Basic analysis with limited original thought or weak arguments",
            "5-6: Some critical analysis and adequate argumentation, but could go deeper",
            "7-8: Good critical analysis with well-constructed arguments",
            "9: Exceptional critical thinking with compelling argumentation, minor improvements possible",
            "10: Perfect critical analysis and argumentation, nothing more needed"
        ],
        "prompt": "Evaluate the depth of analysis, presence of original insights, and strength of arguments. Assess the use of evidence/sources. Identify areas where the analysis could be deepened or argumentation improved."
    },
    "Structure and Clarity": {
        "description": "Evaluate how well ideas are organized and communicated.",
        "rubric": [
            "1-2: Confusing and poorly structured",
            "3-4: Some clear points but overall difficult to follow",
            "5-6: Generally clear but with some organizational issues",
            "7-8: Clear and well-structured with minor issues",
            "9: Exceptionally clear, coherent, and well-organized with minimal room for improvement",
            "10: Perfect structure and clarity, nothing more needed"
        ],
        "prompt": "Assess the clarity of expression and logical flow of ideas. Identify any unclear passages or structural issues. Suggest improvements for clarity and coherence."
    },
    "Language and Style": {
        "description": "Evaluate the quality of writing, including grammar, vocabulary, and stylistic choices.",
        "rubric": [
            "1-2: Poor grammar and inappropriate style",
            "3-4: Frequent language errors or inconsistent style",
            "5-6: Generally correct language with an appropriate style",
            "7-8: Well-written with good command of language and style",
            "9: Exceptional writing with near-perfect use of language and style",
            "10: Perfect language and style, nothing more needed"
        ],
        "prompt": "Assess the quality of writing, including grammar, vocabulary, and style. Consider the appropriateness for the intended audience and purpose. Suggest improvements in language use and style."
    },
    "Perspective and Objectivity": {
        "description": "Evaluate the appropriateness of the perspective taken and the level of objectivity (when required).",
        "rubric": [
            "1-2: Heavily biased or inappropriate perspective",
            "3-4: Noticeable bias or misaligned perspective",
            "5-6: Generally appropriate perspective with some bias",
            "7-8: Well-balanced perspective, mostly objective when required",
            "9: Near-perfect alignment of perspective, objective when required with minimal room for improvement",
            "10: Perfect perspective and objectivity, nothing more needed"
        ],
        "prompt": "Assess whether the perspective taken is appropriate for the given prompt/objective. If objectivity is required, evaluate its presence. If a specific viewpoint is needed, assess how well it's presented. Suggest ways to improve the balance or perspective as needed."
    },
    "Relevance to Initial Objective and Accuracy": {
        "description": "Assess how well the content addresses the initial user-given objective and the accuracy of facts presented.",
        "rubric": [
            "1-2: Content largely ignores or misses the initial objective; contains significant factual errors",
            "3-4: Content partially addresses the initial objective with significant gaps; contains some inaccuracies",
            "5-6: Content addresses the initial objective but lacks depth or comprehensiveness; mostly accurate with some minor errors",
            "7-8: Content fully addresses the initial objective with good relevance; facts are generally accurate",
            "9: Content exceptionally addresses and expands upon the initial objective with high accuracy; minimal room for improvement",
            "10: Perfect relevance to initial objective and factual accuracy, nothing more needed"
        ],
        "prompt": "Compare the content to the initial user-given objective. Evaluate how well it addresses and fulfills this objective. Also assess the accuracy of the facts presented in the content."
    },
    "Creativity and Originality": {
        "description": "Assess the level of creativity and originality in the content.",
        "rubric": [
            "1-2: Entirely derivative or lacking creativity",
            "3-4: Mostly conventional with little originality",
            "5-6: Some creative elements but largely conventional",
            "7-8: Good level of creativity and originality",
            "9: Exceptionally creative and original with minimal room for improvement",
            "10: Perfect creativity and originality, nothing more needed"
        ],
        "prompt": "Evaluate the creativity and originality of the content. Consider unique approaches, novel ideas, or innovative presentations. Suggest areas where more creative approaches could be applied."
    }
}


def get_evaluation_prompt(content, objective):
    prompt = "Evaluate the following content based on these criteria:\n\n"
    for criterion, details in EVALUATION_CRITERIA.items():
        prompt += f"{criterion}:\n"
        prompt += f"Description: {details['description']}\n"
        prompt += "Rubric:\n" + "\n".join(details['rubric']) + "\n"
        prompt += f"Evaluation task: {details['prompt'].format(objective=objective)}\n\n"
    
    prompt += f"Content to evaluate:\n\n{content}\n\n"
    prompt += "For each criterion, provide:\n"
    prompt += "1. A score (1-10) based on the rubric\n"
    prompt += "2. A brief explanation for the score\n"
    prompt += "3. Specific suggestions for improvement\n"
    prompt += "\nFinally, provide an overall assessment and key recommendations for improvement."
    
    return prompt

# ========================
# File: models/evaluation.py
# ========================

from dataclasses import dataclass

@dataclass
class UserEvaluation:
    score: float
    feedback: str

# ========================
# File: models/__init__.py
# ========================

from .evaluation import UserEvaluation