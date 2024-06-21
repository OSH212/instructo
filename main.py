from agents.content_creator import ContentCreator
from agents.evaluator import Evaluator
from models.evaluation import UserEvaluation
from utils.memory import memory
from utils.api_handler import api
from config import FEEDBACK_MODEL
import traceback

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

def run_interaction(prompt, creator, evaluator):
    previous_content = None
    creator_feedback = None
    
    while True:
        # Content creation
        content = creator.create_content(prompt, previous_content, creator_feedback)
        print("\nGenerated Content:\n", content)

        # AI Evaluation
        evaluation = evaluator.evaluate_content(content, prompt)
        print("\nAI Evaluation:")
        print(evaluation)

        # User Evaluation
        while True:
            try:
                user_score = float(input("\nRate the AI's evaluation (0-10): "))
                if 0 <= user_score <= 10:
                    break
                else:
                    print("Please enter a number between 0 and 10.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        user_feedback = input("Provide feedback on the AI's evaluation: ")
        user_eval = UserEvaluation(user_score, user_feedback)

        # Store interaction in memory
        memory.add_interaction(prompt, content, evaluation, user_eval)

        # Apply feedback to improve agents
        creator_feedback, evaluator_feedback = apply_feedback(creator, evaluator, user_eval, {'prompt': prompt, 'content': content}, evaluation)

        if creator_feedback is None and evaluator_feedback is None:
            print("\nNo improvements are needed. The content and evaluation are exceptional.")
            while True:
                user_choice = input("Do you want to start a new prompt or quit? Enter 'new' or 'quit': ").lower()
                if user_choice in ['new', 'quit']:
                    return user_choice == 'new'
                else:
                    print("Invalid choice. Please enter 'new' or 'quit'.")
        elif creator_feedback and evaluator_feedback:
            print("\nBased on the feedback, the content creator and evaluator will now improve their outputs.")
            print("\nDo you want to continue with the improved version, start a new prompt, or quit?")
            print("Enter 'continue' to see the improved version, 'new' for a new prompt, or 'quit' to exit.")
            
            user_choice = input().lower()
            if user_choice == 'continue':
                previous_content = content
                continue
            elif user_choice == 'new':
                return True
            elif user_choice == 'quit':
                return False
            else:
                print("Invalid choice. Continuing with the improved version.")
                previous_content = content
        else:
            print("\nUnable to apply feedback. Do you want to try again with the same prompt, start a new one, or quit?")
            print("Enter 'restart' to try again, 'new' for a new prompt, or 'quit' to exit.")
            
            user_choice = input().lower()
            if user_choice == 'restart':
                continue
            elif user_choice == 'new':
                return True
            elif user_choice == 'quit':
                return False
            else:
                print("Invalid choice. Restarting with the same prompt.")
        

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