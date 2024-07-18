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

# Initialize session state variables
if 'iteration_count' not in st.session_state:
    st.session_state.iteration_count = 0
if 'prompt' not in st.session_state:
    st.session_state.prompt = ""
if 'content' not in st.session_state:
    st.session_state.content = None
if 'evaluation' not in st.session_state:
    st.session_state.evaluation = None
if 'user_eval_content' not in st.session_state:
    st.session_state.user_eval_content = None
if 'user_feedback_evaluator' not in st.session_state:
    st.session_state.user_feedback_evaluator = None
if 'feedback' not in st.session_state:
    st.session_state.feedback = None
if 'stage' not in st.session_state:
    st.session_state.stage = "input"

# Initialize agents
creator = ContentCreator()
evaluator = Evaluator()
feedback_agent = FeedbackAgent()

# Custom CSS for retro-futuristic theme
st.markdown("""
<style>
    .main {
        background-color: #0c0c2a;
        color: #e0e0ff;
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #1a1a4a;
        color: #e0e0ff;
        border: 1px solid #4040ff;
    }
    .stButton > button {
        background-color: #ff4080;
        color: #ffffff;
    }
    .stSlider > div > div > div > div {
        background-color: #ff4080;
    }
    .stHeader {
        background-color: #1a1a4a;
        padding: 1rem;
        border-radius: 10px;
    }
    .section-container {
        background-color: #1a1a4a;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Streamlit app
st.title("Instructo")

# Sidebar
st.sidebar.header(f"Current Iteration: {st.session_state.iteration_count}")

# User Input Section (Prompt)
st.header("User Input")
new_prompt = st.text_area("Enter a content prompt:", value=st.session_state.prompt, height=100)
if new_prompt != st.session_state.prompt:
    st.session_state.prompt = new_prompt
    memory.start_new_session()
    st.session_state.iteration_count = 0
    st.session_state.stage = "generate"

if st.button("Generate Content") or st.session_state.stage == "generate":
    with st.spinner("Generating content..."):
        st.session_state.content = creator.create_content(st.session_state.prompt)
        st.session_state.evaluation = evaluator.evaluate_content(st.session_state.content, st.session_state.prompt)
    st.session_state.stage = "user_eval"
    st.experimental_rerun()

# Main content area with four sections
col1, col2 = st.columns(2)

with col1:
    # Content Display
    with st.container():
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.subheader("Generated Content")
        st.text_area("Content:", value=st.session_state.content, height=200, disabled=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # User Evaluation Section
    with st.container():
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.subheader("User Evaluation")
        if st.session_state.stage == "user_eval":
            user_scores = {}
            user_feedbacks = {}
            for criterion in EVALUATION_CRITERIA:
                user_scores[criterion] = st.slider(f"Rate the {criterion} (0-10):", 0, 10, 5)
                user_feedbacks[criterion] = st.text_area(f"Feedback for {criterion}:", height=50)

            if st.button("Submit User Evaluation"):
                st.session_state.user_eval_content = UserEvaluation(user_scores, user_feedbacks)
                st.session_state.stage = "generate_feedback"
                st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # AI Evaluation Display
    with st.container():
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.subheader("AI Evaluation")
        if st.session_state.evaluation:
            for criterion, details in st.session_state.evaluation.items():
                with st.expander(criterion):
                    if isinstance(details, dict):
                        st.write(f"Score: {details['score']}")
                        st.write(f"Explanation: {details['explanation']}")
                        if details['suggestions']:
                            st.write("Suggestions:")
                            for suggestion in details['suggestions']:
                                st.write(f"- {suggestion}")
                    else:
                        st.write(details)
        else:
            st.write("No evaluation available yet. Generate content to see the AI evaluation.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Feedback and Iteration Control
    with st.container():
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.subheader("Feedback and Next Steps")
        
        # Feedback Agent Section
        if st.session_state.stage == "generate_feedback":
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
            st.session_state.stage = "iteration_control"
            st.experimental_rerun()

        if st.session_state.feedback:
            with st.expander("Overall Analysis"):
                st.markdown(st.session_state.feedback.get('everything', ''))
            with st.expander("Improvements Needed"):
                st.write(st.session_state.feedback.get('improvements_needed', ''))

        # Iteration Control
        if st.session_state.stage == "iteration_control":
            decision = st.radio("What would you like to do?", ["Continue", "Disagree", "New", "Quit"])
            if st.button("Confirm"):
                if decision == "Continue":
                    improvements_needed = st.session_state.feedback.get('improvements_needed', '').strip().upper().startswith('YES')
                    if improvements_needed:
                        st.session_state.iteration_count += 1
                        st.session_state.stage = "generate"
                        st.experimental_rerun()
                    else:
                        st.write("No further improvements needed. You can start a new interaction.")
                        st.session_state.stage = "input"
                elif decision == "Disagree":
                    st.session_state.stage = "disagree"
                elif decision == "New":
                    memory.start_new_session()
                    for key in ['prompt', 'content', 'evaluation', 'user_eval_content', 'user_feedback_evaluator', 'feedback']:
                        st.session_state[key] = None
                    st.session_state.iteration_count = 0
                    st.session_state.stage = "input"
                elif decision == "Quit":
                    st.write("Thank you for using Instructo: AI Content Creation and Evaluation System!")
                    memory.save_to_file()
                    st.stop()
                st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Disagree Section
if st.session_state.stage == "disagree":
    st.header("Provide Additional Feedback")
    additional_feedback = st.text_area("Enter your additional feedback:", height=150)
    if st.button("Submit Additional Feedback"):
        with st.spinner("Incorporating additional feedback..."):
            st.session_state.feedback = feedback_agent.incorporate_user_feedback(st.session_state.feedback, additional_feedback)
        st.success("Feedback updated!")
        st.session_state.stage = "iteration_control"
        st.experimental_rerun()

# Run the Streamlit app
if __name__ == "__main__":
    try:
        memory.load_from_file()
    except Exception as e:
        st.error(f"An error occurred while loading memory: {e}")
        st.error(traceback.format_exc())