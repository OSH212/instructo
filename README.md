# Perplexity LLM Teacher Project

## Overview

This project demonstrates an AI-powered content creation and evaluation system, designed to showcase skills relevant to the LLM Teacher position at Perplexity AI. It utilizes Perplexity's API to generate content and evaluate it, incorporating a feedback loop for continuous improvement.

## Features

- Content generation using Perplexity's online models
- Automated content evaluation based on predefined criteria
- User feedback integration for system improvement
- Memory system to retain and learn from past interactions
- Modular design for easy expansion and modification

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

## Contributing

Contributions to improve the project are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Make your changes and commit (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Perplexity AI for providing the API and inspiration for this project
