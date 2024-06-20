import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('PERPLEXITY_API_KEY')
API_URL = os.getenv('PERPLEXITY_API_URL', 'https://api.perplexity.ai/chat/completions')

CONTENT_CREATOR_MODEL = "llama-3-sonar-large-32k-online"
EVALUATOR_MODEL = "llama-3-sonar-small-32k-chat"
FEEDBACK_MODEL = "llama-3-sonar-large-32k-chat"

MEMORY_FILE = 'memory.json'
MAX_MEMORY_SIZE = 100

# Evaluation threshold
LOW_SCORE_THRESHOLD = 7