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
    if 'full_evaluation' in evaluation:
        console.print(Panel(evaluation['full_evaluation'], title="AI Evaluation", expand=False), style="yellow")
    else:
        overall = Panel(evaluation['overall_assessment'], title="Overall Assessment", expand=False)
        recommendations = Panel("\n".join([f"- {r}" for r in evaluation['recommendations']]), title="Recommendations", expand=False)
        console.print(Columns([overall, recommendations]), style="yellow")

def run_interaction(prompt, creator, evaluator, feedback_agent):
    previous_content = None
    creator_feedback = None
    console = Console()
    
    while True:
        # Content creation
        content = creator.create_content(prompt, previous_content, creator_feedback)
        if creator_feedback:
            console.print("\n[bold cyan]Content Creator's Response to Feedback:[/bold cyan]")
            console.print(f"The content creator has incorporated the following feedback: {creator_feedback}")
        console.print(Panel(content, title="Generated Content", expand=False), style="cyan")

        # AI Evaluation
        evaluation = evaluator.evaluate_content(content, prompt)
        parsed_eval = parse_evaluation(evaluation)
        display_evaluation(parsed_eval, console)

        # User Evaluation
        user_eval = get_user_evaluation(console)

        # Store interaction in memory
        memory.add_interaction(prompt, content, evaluation, user_eval)

        # Apply feedback to improve agents
        interpretation = feedback_agent.analyze_interaction({'prompt': prompt, 'content': content}, evaluation, user_eval)
        console.print("\n[bold magenta]AI Interpretation:[/bold magenta]")
        console.print(Panel(interpretation, expand=False), style="magenta")

        improvements_needed = "improvements needed" in interpretation.lower()

        if improvements_needed:
            creator_feedback, evaluator_feedback = feedback_agent.generate_improvement_suggestions(interpretation)
            console.print("\n[yellow]Improvements are needed. The content creator and evaluator will now improve their outputs.[/yellow]")
            if creator_feedback:
                creator.learn(creator_feedback)
                console.print("\n[bold cyan]Feedback for Content Creator:[/bold cyan]")
                console.print(Panel(creator_feedback, expand=False), style="cyan")
            if evaluator_feedback:
                evaluator.learn(evaluator_feedback)
                console.print("\n[bold yellow]Feedback for Evaluator:[/bold yellow]")
                console.print(Panel(evaluator_feedback, expand=False), style="yellow")
            user_choice = Prompt.ask("Do you want to continue with the improved version, start a new prompt, or quit?", choices=["continue", "new", "quit"], default="continue")
            if user_choice == 'continue':
                previous_content = content
                continue
            elif user_choice == 'new':
                return True
            elif user_choice == 'quit':
                return False
        else:
            console.print("\n[green]No improvements are needed. The content and evaluation are exceptional.[/green]")
            user_choice = Prompt.ask("Do you agree? If not, you can provide additional feedback.", choices=["agree", "disagree"], default="agree")
            if user_choice == "disagree":
                additional_feedback = Prompt.ask("Please provide your additional feedback")
                user_eval.feedback += f"\nAdditional feedback: {additional_feedback}"
                continue
            else:
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