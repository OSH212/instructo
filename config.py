import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('PERPLEXITY_API_KEY')
#API_URL = os.getenv('PERPLEXITY_API_URL', 'https://api.perplexity.ai/chat/completions')

CONTENT_CREATOR_MODEL = "perplexity/llama-3-sonar-large-32k-online"
EVALUATOR_MODEL = "perplexity/llama-3-sonar-large-32k-online"
FEEDBACK_MODEL = "perplexity/llama-3-sonar-large-32k-chat"

MEMORY_FILE = 'memory.yaml'
MAX_MEMORY_SIZE = 100

# Evaluation threshold
LOW_SCORE_THRESHOLD = 7