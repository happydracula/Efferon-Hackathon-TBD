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
            id, study_name, population, sample_size, predictor, 
            outcome, timing, method, performance, notes, source,
            1 - (LEAST(
                population_embedding <=> %s::vector, 
                predictor_embedding <=> %s::vector
            )) AS similarity
        FROM study_metadata
        ORDER BY similarity DESC
        LIMIT %s;
    """

    cur.execute(search_query, (query_embedding, query_embedding, limit))
    columns = [desc[0] for desc in cur.description]
    results = [dict(zip(columns, row)) for row in cur.fetchall()]
    return results

