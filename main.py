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



# def run_interaction(prompt, creator, evaluator, feedback_agent):
#     console = Console()
    
#     while True:
#         # Content creation
#         content = creator.create_content(prompt)
#         console.print(Panel(content, title="Generated Content", expand=False), style="cyan")

#         # AI Evaluation
#         evaluation = evaluator.evaluate_content(content, prompt)
#         display_evaluation(evaluation, console)

#         # User Evaluation for Content
#         user_eval_content = get_user_evaluation_for_content(console)

#         # User Feedback for Evaluator
#         user_feedback_evaluator = get_user_feedback_for_evaluator(console)

#         # Store interaction in memory
#         memory.add_interaction(prompt, content, evaluation, user_eval_content, user_feedback_evaluator)

#         # Feedback Agent Analysis
#         feedback = feedback_agent.analyze_interaction(
#             {'prompt': prompt, 'content': content},
#             evaluation,
#             user_eval_content,
#             user_feedback_evaluator
#         )
#         display_feedback(feedback, console)

#         while True:
#             decision = Prompt.ask(
#                 "What would you like to do?",
#                 choices=["continue", "disagree", "new", "quit"],
#                 default="continue"
#             )

#             if decision == "continue":
#                 if feedback['improvements_needed']:
#                     # Apply feedback to content creator and evaluator
#                     creator.learn(feedback['content_creator_feedback'], prompt, content)
#                     evaluator.learn(feedback['evaluator_feedback'], prompt, content)
                    
#                     # Generate new content with feedback incorporated
#                     new_content = creator.create_content(prompt)
#                     console.print("\n[bold green]Content Creator's response after incorporating feedback:[/bold green]")
#                     console.print(Panel(new_content, title="Updated Generated Content", expand=False), style="cyan")

#                     # Generate new evaluation with feedback incorporated
#                     new_evaluation = evaluator.evaluate_content(new_content, prompt)
#                     console.print("\n[bold green]Evaluator's response after incorporating feedback:[/bold green]")
#                     display_evaluation(new_evaluation, console)

#                     # Update variables for the next iteration
#                     content = new_content
#                     evaluation = new_evaluation
                    
#                     # Get new user evaluations
#                     user_eval_content = get_user_evaluation_for_content(console)
#                     user_feedback_evaluator = get_user_feedback_for_evaluator(console)
                    
#                     # New feedback analysis
#                     feedback = feedback_agent.analyze_interaction(
#                         {'prompt': prompt, 'content': content},
#                         evaluation,
#                         user_eval_content,
#                         user_feedback_evaluator
#                     )
#                     display_feedback(feedback, console)
#                 else:
#                     console.print("No further improvements needed. Starting a new interaction.")
#                     return True
#             elif decision == "disagree":
#                 additional_feedback = get_additional_feedback(console)
#                 feedback = feedback_agent.incorporate_user_feedback(feedback, additional_feedback)
#                 display_feedback(feedback, console)
#             elif decision == "new" or decision == "quit":
#                 return decision == "new"

def run_interaction(prompt, creator, evaluator, feedback_agent):
    console = Console()
    
    while True:
        # Content creation
        content = creator.create_content(prompt)
        console.print(Panel(content, title="Generated Content", expand=False), style="cyan")

        # AI Evaluation
        evaluation = evaluator.evaluate_content(content, prompt)
        display_evaluation(evaluation, console)

        # User Evaluation for Content
        user_eval_content = get_user_evaluation_for_content(console)

        # User Feedback for Evaluator
        user_feedback_evaluator = get_user_feedback_for_evaluator(console)

        # Store interaction in memory
        memory.add_interaction(prompt, content, evaluation, user_eval_content, user_feedback_evaluator)

        # Feedback Agent Analysis
        feedback = feedback_agent.analyze_interaction(
            {'prompt': prompt, 'content': content},
            evaluation,
            user_eval_content,
            user_feedback_evaluator
        )
        display_feedback(feedback, console)

        while True:
            decision = Prompt.ask(
                "What would you like to do?",
                choices=["continue", "disagree", "new", "quit"],
                default="continue"
            )

            if decision == "continue":
                if feedback['improvements_needed']:
                    # Apply feedback to content creator and evaluator
                    creator.learn(feedback['content_creator_feedback'], prompt, content)
                    evaluator.learn(feedback['evaluator_feedback'], prompt, content)
                    break  # Break the inner loop to start a new iteration
                else:
                    console.print("No further improvements needed. Starting a new interaction.")
                    return True
            elif decision == "disagree":
                additional_feedback = get_additional_feedback(console)
                feedback = feedback_agent.incorporate_user_feedback(feedback, additional_feedback)
                display_feedback(feedback, console)
            elif decision == "new" or decision == "quit":
                return decision == "new"

    return True  # Continue the main loop


def display_feedback(feedback, console):
    console.print("\n[bold magenta]Feedback Agent Analysis:[/bold magenta]")
    
    full_feedback = ""
    if 'overall_analysis' in feedback:
        full_feedback += f"[bold]Overall Analysis:[/bold]\n{feedback['overall_analysis']}\n\n"
    
    if 'content_creator_feedback' in feedback:
        full_feedback += f"[bold]Feedback for Content Creator:[/bold]\n{feedback['content_creator_feedback']}\n\n"
    
    if 'evaluator_feedback' in feedback:
        full_feedback += f"[bold]Feedback for Evaluator:[/bold]\n{feedback['evaluator_feedback']}\n\n"
    
    full_feedback += f"[bold]Improvements needed:[/bold] {'Yes' if feedback.get('improvements_needed', False) else 'No'}\n"
    
    if feedback.get('improvements_explanation'):
        full_feedback += f"[bold]Explanation:[/bold]\n{feedback['improvements_explanation']}"
    
    console.print(Panel(full_feedback, title="Feedback Agent Analysis", expand=False))

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