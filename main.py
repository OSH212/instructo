from agents.content_creator import ContentCreator
from agents.evaluator import Evaluator
from models.evaluation import UserEvaluation
from utils.memory import memory
from utils.api_handler import api

def apply_feedback(creator, evaluator, user_eval, content, ai_evaluation):
    feedback_prompt = f"""
    Analyze the following interaction and provide specific, actionable feedback for both the content creator and the evaluator:

    Original Prompt: {content['prompt']}
    Generated Content: {content['content']}
    AI Evaluation: {ai_evaluation}
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
    
    response = api.get_completion("llama-3-chat-small", messages)
    suggestions = response['choices'][0]['message']['content']
    
    print("\nImprovement Suggestions:")
    print(suggestions)
    
    creator_feedback = suggestions.split('1.')[1].split('2.')[0].strip()
    evaluator_feedback = suggestions.split('2.')[1].strip()
    
    creator.learn(creator_feedback)
    evaluator.learn(evaluator_feedback)

def main():
    creator = ContentCreator()
    evaluator = Evaluator()
    
    memory.load_from_file()  # Load previous interactions if available
    
    try:
        while True:
            prompt = input("Enter a content prompt (or 'quit' to exit): ")
            if prompt.lower() == 'quit':
                break

            # Content creation
            content = creator.create_content(prompt)
            print("\nGenerated Content:\n", content)

            # AI Evaluation
            ai_evaluation = evaluator.evaluate_content(content)
            print("\nAI Evaluation:\n", ai_evaluation)

            # User Evaluation
            user_score = float(input("\nRate the AI's evaluation (0-10): "))
            user_feedback = input("Provide feedback on the AI's evaluation: ")
            user_eval = UserEvaluation(user_score, user_feedback)

            # Store interaction in memory
            memory.add_interaction(prompt, content, ai_evaluation, user_eval)

            # Apply feedback to improve agents
            apply_feedback(creator, evaluator, user_eval, {'prompt': prompt, 'content': content}, ai_evaluation)

    finally:
        memory.save_to_file()  # Save interactions before exiting

if __name__ == "__main__":
    main()