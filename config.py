import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('PERPLEXITY_API_KEY')
COHERE_API_KEY = os.getenv('COHERE_API_KEY')

CONTENT_CREATOR_MODEL = "perplexity/llama-3-sonar-large-32k-online"
EVALUATOR_MODEL = "perplexity/llama-3-sonar-large-32k-online"
FEEDBACK_MODEL = "perplexity/llama-3-sonar-large-32k-chat"

COHERE_EMBED_MODEL = "embed-english-v3.0"
COHERE_RERANK_MODEL = "rerank-english-v3.0"

MEMORY_FILE = 'memory.yaml'
MAX_MEMORY_SIZE = 100

# Evaluation threshold
LOW_SCORE_THRESHOLD = 7