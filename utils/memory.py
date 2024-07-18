import os
import yaml
from collections import deque
from models.evaluation import UserEvaluation
from datetime import datetime
import sqlite3
import json
from cohere import Client
from loguru import logger
from config import COHERE_RERANK_MODEL, COHERE_EMBED_MODEL, COHERE_API_KEY

class Memory:
    def __init__(self, max_size=100, db_path='memory.db'):
        self.iterations = deque(maxlen=max_size)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f'memory_{self.session_id}.yaml'
        self.highest_scoring_iteration = None
        self.iteration_count = 0
        self.db_path = db_path
        self.cohere_client = Client(COHERE_API_KEY)
        self._init_db()

    def _init_db(self):
        logger.info("Initializing database.")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iterations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TEXT,
                prompt TEXT,
                content TEXT,
                ai_evaluation TEXT,
                user_evaluation_content TEXT,
                user_feedback_evaluator TEXT,
                feedback_agent_analysis TEXT,
                total_score REAL,
                embedding TEXT
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")

    def add_iteration(self, prompt, content, ai_evaluation, user_evaluation_content, user_feedback_evaluator, feedback_agent_analysis):
        timestamp = datetime.now().isoformat()
        
        iteration = {
            'timestamp': timestamp,
            'prompt': prompt,
            'content': content,
            'ai_evaluation': ai_evaluation,
            'user_evaluation_content': {
                'score': user_evaluation_content.score,
                'feedback': user_evaluation_content.feedback
            },
            'user_feedback_evaluator': user_feedback_evaluator,
            'feedback_agent_analysis': feedback_agent_analysis,
            'metadata': {
                'total_score': sum(user_evaluation_content.score.values()) / len(user_evaluation_content.score)
            }
        }
        self.iterations.append(iteration)
        self._update_highest_scoring_iteration(iteration)
        self.iteration_count += 1
        self._save_to_db(iteration)

    def _save_to_db(self, iteration):
        logger.info(f"Saving iteration to database: {iteration['timestamp']}")
        embedding = self._get_embedding(iteration['content'])
        logger.info(f"Generated embedding of length: {len(embedding)}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO iterations (
                session_id, timestamp, prompt, content, ai_evaluation,
                user_evaluation_content, user_feedback_evaluator,
                feedback_agent_analysis, total_score, embedding
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.session_id,
            iteration['timestamp'],
            iteration['prompt'],
            iteration['content'],
            json.dumps(iteration['ai_evaluation']),
            json.dumps(iteration['user_evaluation_content'].__dict__ if isinstance(iteration['user_evaluation_content'], UserEvaluation) else iteration['user_evaluation_content']),
            iteration['user_feedback_evaluator'],
            json.dumps(iteration['feedback_agent_analysis']),
            iteration['metadata']['total_score'],
            json.dumps(embedding)
        ))
        conn.commit()
        conn.close()
        logger.info(f"Iteration saved to database successfully. Row ID: {cursor.lastrowid}")

    def _get_embedding(self, text):
        logger.info(f"Generating embedding for text: {text[:50]}...")
        response = self.cohere_client.embed(
            texts=[text],
            model=COHERE_EMBED_MODEL,
            input_type="search_document"
        )
        logger.info("Embedding generated successfully.")
        return response.embeddings[0]

    def get_relevant_iterations(self, query, top_n=5):
        logger.info(f"Fetching relevant iterations for query: {query}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, content FROM iterations')
        all_iterations = cursor.fetchall()
        conn.close()

        if not all_iterations:
            logger.info("No iterations found in the database.")
            return []

        ids, texts = zip(*all_iterations)
        logger.info(f"Reranking {len(texts)} iterations")
        rerank_results = self.cohere_client.rerank(
            query=query,
            documents=texts,
            top_n=top_n,
            model=COHERE_RERANK_MODEL
        )
        logger.info(f"Reranking complete. Top relevance score: {rerank_results.results[0].relevance_score if rerank_results.results else 'N/A'}")

        relevant_iterations = []
        for result in rerank_results.results:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM iterations WHERE id = ?', (ids[result.index],))
            iteration = cursor.fetchone()
            conn.close()
            if iteration:
                relevant_iterations.append({
                    'id': iteration[0],
                    'session_id': iteration[1],
                    'timestamp': iteration[2],
                    'prompt': iteration[3],
                    'content': iteration[4],
                    'ai_evaluation': json.loads(iteration[5]),
                    'user_evaluation_content': json.loads(iteration[6]),
                    'user_feedback_evaluator': iteration[7],
                    'feedback_agent_analysis': json.loads(iteration[8]),
                    'total_score': iteration[9],
                    'relevance_score': result.relevance_score
                })

        logger.info(f"Found {len(relevant_iterations)} relevant iterations.")
        return relevant_iterations

    def _update_highest_scoring_iteration(self, iteration):
        if not self.highest_scoring_iteration or iteration['metadata']['total_score'] > self.highest_scoring_iteration['metadata']['total_score']:
            self.highest_scoring_iteration = iteration
            logger.info(f"Updated highest scoring iteration: {iteration['timestamp']} with score {iteration['metadata']['total_score']}")

    def get_content_creator_context(self, evaluation_criteria):
        context = {
            'prompt': self.iterations[-1]['prompt'] if self.iterations else None,
            'last_content': self.iterations[-1]['content'] if self.iterations else None,
            'highest_scoring_content': self.highest_scoring_iteration['content'] if self.highest_scoring_iteration else None,
            'evaluation_criteria': evaluation_criteria,
            'last_feedback': self.iterations[-1]['feedback_agent_analysis'] if self.iterations else None,
            'highest_scoring_feedback': self.highest_scoring_iteration['feedback_agent_analysis'] if self.highest_scoring_iteration else None
        }
        return context

    def get_evaluator_context(self, evaluation_criteria):
        context = {
            'prompt': self.iterations[-1]['prompt'] if self.iterations else None,
            'evaluation_criteria': evaluation_criteria,
            'last_evaluation': self.iterations[-1]['ai_evaluation'] if self.iterations else None,
            'last_content': self.iterations[-1]['content'] if self.iterations else None,
            'highest_scoring_content': self.highest_scoring_iteration['content'] if self.highest_scoring_iteration else None,
            'last_feedback': self.iterations[-1]['feedback_agent_analysis'] if self.iterations else None
        }
        return context

    def get_feedback_agent_context(self):
        return list(self.iterations)[-5:]

    def get_recent_iterations(self, n=5):
        return list(self.iterations)[-n:]

    def get_iteration_count(self):
        return self.iteration_count

    def save_to_file(self):
        logger.info(f"Saving memory to file: {self.filename}")
        with open(self.filename, 'w') as f:
            yaml.dump(list(self.iterations), f)
        logger.info("Memory saved to file successfully.")

    def load_from_file(self, session_id=None):
        if session_id:
            filename = f'memory_{session_id}.yaml'
        else:
            files = [f for f in os.listdir() if f.startswith('memory_') and f.endswith('.yaml')]
            if not files:
                logger.info("No existing memory files found. Starting with empty memory.")
                return
            filename = max(files)

        try:
            logger.info(f"Loading memory from file: {filename}")
            with open(filename, 'r') as f:
                loaded_data = yaml.safe_load(f)
                if loaded_data:
                    self.iterations = deque(
                        [{**iteration, 
                        'user_evaluation_content': UserEvaluation(
                            score=iteration['user_evaluation_content']['score'],
                            feedback=iteration['user_evaluation_content']['feedback']
                        ) if isinstance(iteration['user_evaluation_content'], dict) else iteration['user_evaluation_content']}
                        for iteration in loaded_data],
                        maxlen=self.iterations.maxlen
                    )
                    self.session_id = filename.split('_')[1].split('.')[0]
                    self.filename = filename
                    
                    # Save loaded data to SQLite
                    for iteration in self.iterations:
                        self._save_to_db(iteration)
            logger.info("Memory loaded from file successfully.")
        except yaml.YAMLError as e:
            logger.error(f"Error loading memory file: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading memory file: {e}")
            logger.exception(e)  # This will log the full traceback

    def start_new_session(self):
        logger.info("Starting a new session.")
        self.iterations.clear()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f'memory_{self.session_id}.yaml'
        self.iteration_count = 0
        self.highest_scoring_iteration = None
        logger.info("New session started successfully.")

memory = Memory()