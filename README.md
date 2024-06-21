# Instructo: Perplexity LLM Teacher Project

## Overview

The Perplexity LLM Teacher Project is an advanced AI-powered content creation and evaluation system. It leverages Perplexity's API to generate high-quality content and perform in-depth evaluations, all while incorporating a sophisticated feedback loop for continuous improvement. This project demonstrates the potential of AI in content creation, evaluation, and self-improvement processes.

## Features

1. **AI-Powered Content Creation**
   - Utilizes Perplexity's state-of-the-art language models
   - Generates comprehensive, well-researched content based on user prompts
   - Incorporates feedback for continuous improvement in content quality

2. **Automated Content Evaluation**
   - Employs a multi-criteria evaluation system
   - Assesses content quality, critical analysis, structure, language, relevance, and creativity
   - Provides detailed scores and feedback for each criterion

3. **User Feedback Integration**
   - Allows users to rate and provide feedback on generated content and AI evaluations
   - Incorporates user input to refine both content creation and evaluation processes

4. **Adaptive Learning System**
   - Implements a feedback loop for continuous improvement of AI agents
   - Analyzes user feedback to generate specific improvement suggestions for content creation and evaluation

5. **Memory System**
   - Retains past interactions, including prompts, generated content, AI evaluations, and user feedback

6. **Modular and Extensible Design**
   - Separates content creation, evaluation, and utility functions into distinct modules
   - Facilitates easy expansion and modification of system components

## How It Works

1. **Content Generation**: 
   The system prompts the user for a content topic. The AI-powered ContentCreator then generates comprehensive, well-researched content based on this prompt.

2. **AI Evaluation**: 
   The generated content is automatically evaluated by the Evaluator agent. It assesses the content based on predefined criteria, providing scores and detailed feedback for each aspect.

3. **User Feedback**: 
   The user is prompted to review the generated content and AI evaluation. They can provide scores and feedback for each evaluation criterion.

4. **Feedback Analysis**: 
   The system analyzes the AI evaluation and user feedback to determine if improvements are needed. If so, it generates specific suggestions for both the content creator and evaluator.

5. **Continuous Improvement**: 
   Based on the feedback and suggestions, the system updates its content creation and evaluation processes, aiming to improve future outputs.

6. **Memory Storage**: 
   Each interaction, including the prompt, generated content, AI evaluation, and user feedback, is stored in the system's memory for future reference and learning.

## Technical Details

- **API Integration**: Utilizes Perplexity's API for advanced language model capabilities
- **Model Selection**: Uses different models for content creation, evaluation, and feedback analysis (configurable in `config.py`)
- **Asynchronous Operations**: Implements asynchronous API calls for improved performance
- **Data Persistence**: Stores interaction history in YAML format for easy reading and parsing

## Installation

1. Clone the repository:

2. Install required packages:

3. Set up your environment variables:
Create a `.env` file in the project root and add your Perplexity API key:

## Usage

Run the main script to start the interactive session:

python3.11 main.py  

Follow the prompts to:
1. Enter content prompts
2. Review generated content
3. Examine AI evaluations
4. Provide feedback on the AI's performance

The system will learn and improve based on your feedback over time.

## Project Structure

- `main.py`: Entry point of the application
- `agents/`: Contains the ContentCreator and Evaluator classes
- `models/`: Defines data models used in the project
- `utils/`: Utility functions and classes (API handling, memory, guidelines)
- `config.py`: Configuration settings
- `requirements.txt`: List of required Python packages

## Customization

- Modify `utils/guidelines.py` to adjust evaluation criteria
- Update model selections in `config.py`
- Extend `agents/` classes to add new functionalities

## License

This project is not published for public use. It is a private project to demonstrate my skills and interest in the LLM Teacher position, and for the Perplexity AI team's consideration.

## Acknowledgments

- Perplexity AI for providing the API and inspiration for this project
