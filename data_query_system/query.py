import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_query_system.db import get_conn
from llm_invoker import get_embedding

def query_studies(query_text, limit=3):
    """
    Queries the database using cosine similarity. 
    It checks the query against both population and predictor embeddings.
    """
    conn = get_conn()
    cur = conn.cursor()
    query_embedding = get_embedding(query_text, "sentence-transformers/all-minilm-l6-v2")


    search_query = """
        SELECT 
            study_name, 
            population, 
            predictor, 
            performance,
            LEAST(
                population_embedding <=> %s::vector, 
                predictor_embedding <=> %s::vector
            ) AS min_distance
        FROM study_metadata
        ORDER BY min_distance ASC
        LIMIT %s;
    """

    cur.execute(search_query, (query_embedding, query_embedding, limit))
    results = cur.fetchall()

    # 3. Print the results nicely
    print(f"\n--- Top Results for: '{query_text}' ---")
    for row in results:
        name, pop, pred, perf, dist = row
        similarity = 1 - dist
        print(f"Study: {name}")
        print(f"Match Similarity: {similarity:.4f}")
        print(f"Population: {pop[:100]}...")
        print(f"Predictor: {pred[:100]}...")
        print(f"Performance: {perf}")
        print("-" * 30)

