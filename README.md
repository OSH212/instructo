
Instructo: Perplexity LLM Teacher Project

Overview

The Perplexity LLM Teacher Project is an advanced AI-powered content creation and evaluation system. It leverages Perplexity's API to generate high-quality content, perform in-depth evaluations, and provide comprehensive feedback for continuous improvement. This project demonstrates the potential of AI in content creation, evaluation, and self-improvement processes.
Features

1. AI-Powered Content Creation

Utilizes Perplexity's online language models
Generates based on user prompts
Incorporates feedback for continuous improvement in content quality

2. Automated Content Evaluation

multi-criteria evaluation system
detailed scores and feedback for each criterion

3. User Feedback Integration

users to rate and provide feedback on generated content and AI evaluations

4. Adaptive Learning System

feedback loop for iterative improvement of agents
user feedback used to generate specific improvement suggestions for content creation and evaluation

5. Comprehensive Feedback Analysis

dedicated FeedbackAgent to analyze iterations
overall analysis, specific feedback for content creator and evaluator
Determines if improvements are needed and explains  decision

6. Memory System

Retains past interactions, including prompts, generated content, AI evaluations, and user feedback

7. Modular and Extensible Design

Separates content creation, evaluation, and feedback analysis into distinct modules
Facilitates easy expansion and modification of system components

How It Works

1. Content Generation: The system prompts the user for a content topic. The AI-powered ContentCreator generates comprehensive content based on this prompt.
2. AI Evaluation: The Evaluator agent assesses the generated content based on predefined criteria, providing scores and detailed feedback.
3. User Feedback: The user reviews the generated content and AI evaluation, providing scores and feedback for each evaluation criterion.
4. Feedback Analysis: The FeedbackAgent analyzes the AI evaluation and user feedback, providing comprehensive analysis and improvement suggestions.
5. Continuous Improvement: Based on the feedback and suggestions, the system updates its content creation and evaluation processes for future outputs.


More Details
API Integration: Utilizes Perplexity's API
Model Selection: Uses different models for content creation, evaluation, and feedback analysis (configurable in config.py)
Data Persistence: Stores interaction history in YAML format for easy reading and parsing

Installation
Clone the repository
Install required packages: pip install -r requirements.txt
Set up your environment variables: Create a .env file in the project root and add your Perplexity API key
Usage
Run the main script to start the interactive session

Follow the prompts to:
Enter content prompts
Review generated content
Examine AI evaluation
Provide feedback on the AI's performance
Choose to continue, disagree, start a new interaction, or quit


Acknowledgments
Perplexity AI for inspiring  this project