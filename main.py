# from colorama import Fore, Style, init
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from agents.content_creator import ContentCreator
from agents.evaluator import Evaluator
from models.evaluation import UserEvaluation
from utils.memory import memory
from utils.guidelines import EVALUATION_CRITERIA
from agents.feedback_agent import FeedbackAgent
# from utils.api_handler import api
# from config import FEEDBACK_MODEL
import traceback




#import logging

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)


def run_interaction(prompt, creator, evaluator, feedback_agent):
    console = Console()
    iteration_count = 0
    
    while True:
        # logger.debug(f"Starting iteration {iteration_count}")
        # logger.debug(f"Using memory with {len(memory.get_recent_iterations(5))} recent iterations")
        # logger.debug(f"Starting iteration {memory.get_iteration_count()}")
        # logger.debug(f"Using memory with {len(memory.get_recent_iterations(5))} recent iterations")
        
        # Content creation
        console.print("Fetching relevant iterations from memory...")
        relevant_iterations = memory.get_relevant_iterations(prompt)
        console.print(f"Found {len(relevant_iterations)} relevant iterations.")
        console.print("Creating content...")
        content = creator.create_content(prompt)
        console.print(Panel(content, title="Generated Content", expand=False), style="cyan")

        # AI Evaluation
        #logger.debug("Evaluating content")
        evaluation = evaluator.evaluate_content(content, prompt)
        display_evaluation(evaluation, console)

        # User Evaluation for Content
        #logger.debug("Getting user evaluation for content")
        user_eval_content = get_user_evaluation_for_content(console)

        # User Feedback for Evaluator
        #logger.debug("Getting user feedback for evaluator")
        user_feedback_evaluator = get_user_feedback_for_evaluator(console)

        # Feedback Agent Analysis
        #logger.debug("Generating and displaying feedback")
        recent_iterations = memory.get_recent_iterations(5)  # Get the recent iterations
        #logger.debug(f"recent iterations: {recent_iterations}")
        feedback = feedback_agent.analyze_interaction(recent_iterations, prompt, content, evaluation, user_eval_content, user_feedback_evaluator)
        display_feedback(feedback, console)
        #logger.debug(f"Feedback before storing in memory: {feedback}")


        # Store iteration in memory
        #logger.debug("Storing iteration in memory")
        memory.add_iteration(prompt, content, evaluation, user_eval_content, user_feedback_evaluator, feedback)

        while True:
            #logger.debug("Asking for user decision")
            decision = Prompt.ask(
                "What would you like to do?",
                choices=["continue", "disagree", "new", "quit"],
                default="continue"
            )

            if decision == "continue":
                improvements_needed = feedback['improvements_needed'].strip().upper().startswith('YES')
                if improvements_needed:
                    #logger.debug("Improvements needed, starting next iteration")
                    iteration_count += 1
                    break  # Break the inner loop to start a new iteration
                else:
                    #logger.debug("No improvements needed")
                    console.print("No further improvements needed. Starting a new interaction.")
                    return True
            elif decision == "disagree":
                #logger.debug("User disagreed, incorporating additional feedback")
                additional_feedback = get_additional_feedback(console)
                feedback = feedback_agent.incorporate_user_feedback(feedback, additional_feedback)
                display_feedback(feedback, console)
            elif decision == "new":
                #logger.debug("Starting new interaction")
                memory.start_new_session()
                return True
            elif decision == "quit":
                #logger.debug("Quitting")
                return False

    return True  # Continue the main loop


def display_feedback(feedback, console):
    #logger.debug("Displaying feedback")
    console.print("\n[bold magenta]Feedback Agent Analysis:[/bold magenta]")
    
    if feedback:
        # if feedback['overall_analysis']:
        #     console.print(Panel(feedback['overall_analysis'], title="Overall Analysis", expand=False))
        
        # if feedback['content_creator_feedback']:
        #     console.print("\n[bold]Feedback for Content Creator:[/bold]")
        #     for criterion, content in feedback['content_creator_feedback'].items():
        #         console.print(f"[cyan]{criterion}:[/cyan] {content}")
        
        # if feedback['evaluator_feedback']:
        #     console.print(Panel(feedback['evaluator_feedback'], title="Feedback for Evaluator", expand=False))
        if feedback['everything']:
            console.print(f"\n[bold]Feedback:[/bold] {feedback['everything']}")
        
        if feedback['improvements_needed']:
            console.print(f"\n[bold]Improvements Needed:[/bold] {feedback['improvements_needed']}")
    else:
        console.print("Error: No feedback available")
    
    #logger.debug("Finished displaying feedback")




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


def get_user_evaluation_for_content(console):
    user_scores = {}
    user_feedbacks = {}
    
    console.print("\n[bold]Please rate and provide feedback for the content:[/bold]")
    
    table = Table(title="Content Evaluation Criteria", box=box.ROUNDED)
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

def get_user_feedback_for_evaluator(console):
    console.print("\n[bold]Please provide feedback for the AI Evaluator:[/bold]")
    return Prompt.ask("Your feedback for the evaluator")

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

            memory.start_new_session()
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