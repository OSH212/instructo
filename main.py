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


def handle_command(command, prompt, creator, evaluator):
    if command == 'quit':
        return False
    elif command == 'new':
        return True
    elif command == 'restart':
        print("\nRestarting interaction with the same prompt.")
        run_interaction(prompt, creator, evaluator)
    else:
        print("Invalid command. Please try again.")
    return True

def parse_evaluation(evaluation):
    if isinstance(evaluation, str):
        return {'full_evaluation': evaluation}
    return evaluation

def display_evaluation(evaluation, console):
    console.print("\n[bold yellow]AI Evaluation:[/bold yellow]")
    console.print(f"Overall Assessment: {evaluation['overall_assessment']}")
    console.print("\nRecommendations:")
    for recommendation in evaluation['recommendations']:
        console.print(f"- {recommendation}")
    
    if evaluation.get('no_improvements_needed', False):
        console.print("\n[green]No improvements needed. The content is exceptional.[/green]")
    else:
        console.print("\n[yellow]Improvements may be needed based on the recommendations above.[/yellow]")
    
    if 'feedback_acknowledgment' in evaluation:
        console.print("\n[bold cyan]Feedback Acknowledgment:[/bold cyan]")
        console.print(evaluation['feedback_acknowledgment'])
    
    console.print("\nFull Evaluation:", style="dim")
    console.print(evaluation['full_evaluation'])

def run_interaction(prompt, creator, evaluator, feedback_agent):
    console = Console()
    
    while True:
        # Reset feedback variables at the start of each iteration
        creator_feedback = None
        evaluator_feedback = None

        # Content creation
        content = creator.create_content(prompt, previous_content=None, feedback=creator_feedback)
        console.print(Panel(content, title="Generated Content", expand=False), style="cyan")

        # AI Evaluation
        evaluation = evaluator.evaluate_content(content, prompt, evaluator_feedback)
        parsed_eval = parse_evaluation(evaluation)
        display_evaluation(parsed_eval, console)

        # User Evaluation
        user_eval = get_user_evaluation(console)

        # Store interaction in memory
        memory.add_interaction(prompt, content, evaluation, user_eval)

        # Apply feedback to improve agents
        interpretation, improvements_needed = feedback_agent.analyze_interaction({'prompt': prompt, 'content': content}, evaluation, user_eval)
        console.print("\n[bold magenta]AI Interpretation:[/bold magenta]")
        console.print(Panel(interpretation, expand=False), style="magenta")

        # Ask user if they agree with the AI's assessment
        user_agrees = Prompt.ask("Do you agree with the AI's assessment?", choices=["yes", "no"], default="yes")

        if improvements_needed and user_agrees.lower() == "yes":
            creator_feedback, evaluator_feedback = feedback_agent.generate_improvement_suggestions(interpretation)
            console.print("\n[yellow]Improvements are needed. The content creator and evaluator will now improve their outputs.[/yellow]")
            if creator_feedback:
                console.print("\n[bold cyan]Feedback for Content Creator:[/bold cyan]")
                for criterion, suggestions in creator_feedback.items():
                    console.print(f"\n{criterion}:")
                    for suggestion in suggestions:
                        console.print(f"- {suggestion}")
            if evaluator_feedback:
                console.print("\n[bold yellow]Feedback for Evaluator:[/bold yellow]")
                for criterion, suggestions in evaluator_feedback.items():
                    console.print(f"\n{criterion}:")
                    for suggestion in suggestions:
                        console.print(f"- {suggestion}")
            
            # Apply feedback
            creator.learn(creator_feedback)
            evaluator.learn(evaluator_feedback)
            
            user_choice = Prompt.ask("Do you want to continue with the improved version, start a new prompt, or quit?", choices=["continue", "new", "quit"], default="continue")
            if user_choice == 'continue':
                continue
            elif user_choice == 'new':
                return True
            elif user_choice == 'quit':
                return False
        else:
            if improvements_needed:
                console.print("\n[yellow]The AI suggested improvements, but you disagreed. No changes will be made.[/yellow]")
            else:
                console.print("\n[green]No improvements are needed. The content and evaluation are exceptional.[/green]")
            user_choice = Prompt.ask("Do you want to start a new prompt or quit?", choices=["new", "quit"], default="new")
            return user_choice == "new"

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

    overall_score = sum(user_scores.values()) / len(user_scores)
    overall_feedback = "\n".join([f"{k}: {v}" for k, v in user_feedbacks.items()])
    
    return UserEvaluation(overall_score, overall_feedback)
    


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