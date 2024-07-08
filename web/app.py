import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify
from main import run_interaction, ContentCreator, Evaluator, FeedbackAgent, memory
from utils.guidelines import EVALUATION_CRITERIA
from models.evaluation import UserEvaluation

app = Flask(__name__)

creator = ContentCreator()
evaluator = Evaluator()
feedback_agent = FeedbackAgent()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.json['prompt']
    content = creator.create_content(prompt)
    evaluation = evaluator.evaluate_content(content, prompt)
    return jsonify({
        'content': content,
        'evaluation': evaluation,
        'criteria': list(EVALUATION_CRITERIA.keys())
    })

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    recent_iterations = memory.get_recent_iterations(5)
    user_eval_content = UserEvaluation(data['user_eval_content']['scores'], data['user_eval_content']['feedbacks'])
    
    feedback = feedback_agent.analyze_interaction(
        recent_iterations,
        data['prompt'],
        data['content'],
        data['evaluation'],
        user_eval_content,
        data['user_feedback_evaluator']
    )
    
    memory.add_iteration(
        data['prompt'],
        data['content'],
        data['evaluation'],
        user_eval_content,
        data['user_feedback_evaluator'],
        feedback
    )
    
    return jsonify({'feedback': feedback})

@app.route('/incorporate_feedback', methods=['POST'])
def incorporate_feedback():
    data = request.json
    updated_feedback = feedback_agent.incorporate_user_feedback(data['feedback'], data['additional_feedback'])
    return jsonify({'feedback': updated_feedback})

if __name__ == '__main__':
    app.run(debug=True)