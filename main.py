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

def apply_feedback(creator, evaluator, user_eval, content, evaluation):
    interpretation_prompt = f"""
    Analyze the following AI evaluation and user feedback:

    AI Evaluation: {evaluation}
    User Score: {user_eval.score}
    User Feedback: {user_eval.feedback}

    Based on this information, determine if any improvements are needed for the content or the evaluation process.
    Respond with either:
    1. "No improvements needed" if both the AI evaluation and user feedback indicate the content and evaluation are exceptional.
    2. "Improvements needed" if either the AI evaluation or user feedback suggest any areas for improvement.

    Provide a brief explanation for your decision.
    """

    messages = [
        {"role": "system", "content": "You are an AI improvement specialist. Your task is to analyze evaluations and feedback to determine if improvements are needed."},
        {"role": "user", "content": interpretation_prompt}
    ]

    try:
        response = api.get_completion(FEEDBACK_MODEL, messages)
        if response and 'choices' in response:
            interpretation = response['choices'][0]['message']['content']
            print("\nAI Interpretation:")
            print(interpretation)

            if "no improvements needed" in interpretation.lower():
                return None, None

            # If improvements are needed, proceed with generating suggestions
            feedback_prompt = f"""
            Based on the following interaction, provide specific, actionable feedback for both the content creator and the evaluator:

            Original Prompt: {content['prompt']}
            Generated Content: {content['content']}
            AI Evaluation: {evaluation}
            User Score: {user_eval.score}
            User Feedback: {user_eval.feedback}

            Provide separate, detailed suggestions for:
            1. How the content creator can improve its output
            2. How the evaluator can enhance its assessment
            """

            messages = [
                {"role": "system", "content": "You are an AI improvement specialist. Your task is to analyze interactions and suggest concrete, specific improvements for AI systems."},
                {"role": "user", "content": feedback_prompt}
            ]

            response = api.get_completion(FEEDBACK_MODEL, messages)
            if response and 'choices' in response:
                suggestions = response['choices'][0]['message']['content']
                
                print("\nImprovement Suggestions:")
                print(suggestions)
                
                creator_feedback = suggestions.split('1.')[1].split('2.')[0].strip()
                evaluator_feedback = suggestions.split('2.')[1].strip()
                
                creator.learn(creator_feedback)
                evaluator.learn(evaluator_feedback)
                return creator_feedback, evaluator_feedback
            else:
                print("Failed to generate improvement suggestions.")
                return None, None
        else:
            print("Failed to interpret the evaluation and feedback.")
            return None, None
    except Exception as e:
        print(f"Error in applying feedback: {e}")
        print(traceback.format_exc())
        return None, None

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

def run_interaction(prompt, creator, evaluator):
    previous_content = None
    creator_feedback = None
    console = Console()
    
    while True:
        # Content creation
        content = creator.create_content(prompt, previous_content, creator_feedback)
        console.print(Panel(content, title="Generated Content", expand=False), style="cyan")

        # AI Evaluation
        evaluation = evaluator.evaluate_content(content, prompt)
        parsed_eval = parse_evaluation(evaluation)
        display_evaluation(parsed_eval, console)

        # User Evaluation
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
        
        user_eval = UserEvaluation(overall_score, overall_feedback)

        # Store interaction in memory
        memory.add_interaction(prompt, content, evaluation, user_eval)

        # Apply feedback to improve agents
        creator_feedback, evaluator_feedback = apply_feedback(creator, evaluator, user_eval, {'prompt': prompt, 'content': content}, evaluation)

        if creator_feedback is None and evaluator_feedback is None:
            console.print("\n[green]No improvements are needed. The content and evaluation are exceptional.[/green]")
            while True:
                user_choice = Prompt.ask("Do you want to start a new prompt or quit?", choices=["new", "quit"], default="new")
                if user_choice in ['new', 'quit']:
                    return user_choice == 'new'
        elif creator_feedback and evaluator_feedback:
            console.print("\n[yellow]Based on the feedback, the content creator and evaluator will now improve their outputs.[/yellow]")
            user_choice = Prompt.ask("Do you want to continue with the improved version, start a new prompt, or quit?", choices=["continue", "new", "quit"], default="continue")
            if user_choice == 'continue':
                previous_content = content
                continue
            elif user_choice == 'new':
                return True
            elif user_choice == 'quit':
                return False
        else:
            console.print("\n[red]Unable to apply feedback.[/red]")
            user_choice = Prompt.ask("Do you want to try again with the same prompt, start a new one, or quit?", choices=["restart", "new", "quit"], default="restart")
            if user_choice == 'restart':
                continue
            elif user_choice == 'new':
                return True
            elif user_choice == 'quit':
                return False
        

def main():
    creator = ContentCreator()
    evaluator = Evaluator()
    
    memory.load_from_file()  # Load previous interactions if available
    
    try:
        while True:
            prompt = input("Enter a content prompt (or 'quit' to exit): ")
            if prompt.lower() == 'quit':
                break

            continue_main_loop = run_interaction(prompt, creator, evaluator)
            if not continue_main_loop:
                break

    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())
    finally:
        memory.save_to_file()  # Save interactions before exiting

if __name__ == "__main__":
    main()