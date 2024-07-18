import streamlit as st
from rich.console import Console
from rich.panel import Panel
from agents.content_creator import ContentCreator
from agents.evaluator import Evaluator
from models.evaluation import UserEvaluation
from utils.memory import memory
from utils.guidelines import EVALUATION_CRITERIA
from agents.feedback_agent import FeedbackAgent
import traceback

# Initialize agents
creator = ContentCreator()
evaluator = Evaluator()
feedback_agent = FeedbackAgent()

# Initialize session state
if 'prompt' not in st.session_state:
    st.session_state.prompt = ""
if 'content' not in st.session_state:
    st.session_state.content = ""
if 'evaluation' not in st.session_state:
    st.session_state.evaluation = {}
if 'user_eval_content' not in st.session_state:
    st.session_state.user_eval_content = None
if 'user_feedback_evaluator' not in st.session_state:
    st.session_state.user_feedback_evaluator = ""
if 'feedback' not in st.session_state:
    st.session_state.feedback = {}
if 'iteration_count' not in st.session_state:
    st.session_state.iteration_count = 0

# Streamlit app
st.title("AI Content Creation and Evaluation System")

# User Input Section
st.header("User Input")
new_prompt = st.text_area("Enter a content prompt:", value=st.session_state.prompt)
if new_prompt != st.session_state.prompt:
    st.session_state.prompt = new_prompt
    memory.start_new_session()
    st.session_state.iteration_count = 0

# Content Creation Section
st.header("Content Creation")
if st.button("Generate Content"):
    with st.spinner("Generating content..."):
        st.session_state.content = creator.create_content(st.session_state.prompt)
    st.success("Content generated!")
st.text_area("Generated Content:", value=st.session_state.content, height=200, disabled=True)

# AI Evaluation Section
st.header("AI Evaluation")
if st.button("Evaluate Content"):
    with st.spinner("Evaluating content..."):
        st.session_state.evaluation = evaluator.evaluate_content(st.session_state.content, st.session_state.prompt)
    st.success("Evaluation complete!")
for criterion, details in st.session_state.evaluation.items():
    st.subheader(criterion)
    if isinstance(details, dict):
        st.write(f"Score: {details['score']}")
        st.write(f"Explanation: {details['explanation']}")
        if details['suggestions']:
            st.write("Suggestions:")
            for suggestion in details['suggestions']:
                st.write(f"- {suggestion}")
    else:
        st.write(details)

# User Evaluation Section
st.header("User Evaluation")
user_scores = {}
user_feedbacks = {}
for criterion in EVALUATION_CRITERIA:
    user_scores[criterion] = st.slider(f"Rate the {criterion} (0-10):", 0, 10, 5)
    user_feedbacks[criterion] = st.text_area(f"Provide feedback for {criterion}:")

if st.button("Submit User Evaluation"):
    st.session_state.user_eval_content = UserEvaluation(score=user_scores, feedback=user_feedbacks)
    st.success("User evaluation submitted!")

# User Feedback for Evaluator
st.header("User Feedback for Evaluator")
user_feedback_evaluator = st.text_area("Provide feedback for the AI Evaluator:")
if st.button("Submit Feedback for Evaluator"):
    st.session_state.user_feedback_evaluator = user_feedback_evaluator
    st.success("Feedback for evaluator submitted!")

# Feedback Agent Section
st.header("Feedback Agent Analysis")
if st.button("Generate Feedback"):
    with st.spinner("Generating feedback..."):
        recent_iterations = memory.get_recent_iterations(5)
        st.session_state.feedback = feedback_agent.analyze_interaction(
            recent_iterations,
            st.session_state.prompt,
            st.session_state.content,
            st.session_state.evaluation,
            st.session_state.user_eval_content,
            st.session_state.user_feedback_evaluator
        )
    st.success("Feedback generated!")

if st.session_state.feedback:
    st.subheader("Overall Analysis")
    st.write(st.session_state.feedback.get('everything', ''))
    st.subheader("Improvements Needed")
    st.write(st.session_state.feedback.get('improvements_needed', ''))

# Iteration Control
st.header("Iteration Control")
decision = st.radio("What would you like to do?", ["Continue", "Disagree", "New", "Quit"])

if decision == "Continue":
    improvements_needed = st.session_state.feedback.get('improvements_needed', '').strip().upper().startswith('YES')
    if improvements_needed:
        st.session_state.iteration_count += 1
        st.experimental_rerun()
    else:
        st.write("No further improvements needed. You can start a new interaction.")
elif decision == "Disagree":
    additional_feedback = st.text_area("Provide additional feedback:")
    if st.button("Submit Additional Feedback"):
        with st.spinner("Incorporating additional feedback..."):
            st.session_state.feedback = feedback_agent.incorporate_user_feedback(st.session_state.feedback, additional_feedback)
        st.success("Feedback updated!")
        st.experimental_rerun()
elif decision == "New":
    if st.button("Start New Interaction"):
        memory.start_new_session()
        for key in ['prompt', 'content', 'evaluation', 'user_eval_content', 'user_feedback_evaluator', 'feedback']:
            st.session_state[key] = None
        st.session_state.iteration_count = 0
        st.experimental_rerun()
elif decision == "Quit":
    st.write("Thank you for using the AI Content Creation and Evaluation System!")
    memory.save_to_file()

# Display current iteration count
st.sidebar.write(f"Current Iteration: {st.session_state.iteration_count}")

# Run the Streamlit app
if __name__ == "__main__":
    try:
        memory.load_from_file()
    except Exception as e:
        st.error(f"An error occurred while loading memory: {e}")
        st.error(traceback.format_exc())