Instructo: LLM Teacher Project

Overview

Instructo is an AI-powered content creation and evaluation system that leverages Perplexity's API for generating high-quality content and providing comprehensive feedback. It demonstrates the potential of AI in content creation, evaluation, and self-improvement processes. Perplexity models were preferered for their access to up-to-date information.  

An ode to the 'LLM teacher' positions. 

## Key Features

1. AI Content Creation and Evaluation
2. User Feedback Integration
3. Adaptive Learning System
4. Comprehensive Feedback Analysis
5. Persistent Memory with Semantic Search
6. User-Friendly Interface


## How to Use:

1. Install dependencies:
   ```
   pip install -r requirements.txt

### CLI Version

2. Run the main script:
   ```
   python main.py
   ```

3. Follow the prompts to input your content topic and interact with the system.

### If you'd rather use the Streamlit App instead:

- Run the Streamlit app:
   ```
   streamlit run app.py
   ```

3. Open the provided URL in your browser and use the intuitive interface to interact with the system.


### How It Works

1. Content Generation: The system prompts the user for a content topic. The ContentCreator generates comprehensive content based on this prompt.
2. AI Evaluation: The Evaluator agent assesses the generated content based on predefined criteria, providing scores and detailed feedback.
3. User Feedback: The user reviews the generated content and AI evaluation, providing scores and feedback for each evaluation criterion.
4. Feedback Analysis: The FeedbackAgent analyzes the evaluator and user feedback, providing comprehensive analysis and improvement suggestions.
5. Continuous Improvement: Based on the feedback and suggestions, the system updates its content creation and evaluation processes for future outputs.
6. Database Storage: Each iteration, including prompts, content, evaluations, and feedback, is stored in an SQLite database for persistent memory.
7. Semantic Search: When retrieving relevant past iterations, the system uses Cohere's embedding model to convert text to vector representations and the reranking model to find the most relevant entries based on semantic similarity.
8. User Interface: The Streamlit-based UI provides an intuitive interface for users to input prompts, view generated content, provide evaluations, and control the iteration process.


## Configuration

API keys and model specifications are stored in `config.py`. Make sure to set up your environment variables or modify this file with your API keys before running the system.
