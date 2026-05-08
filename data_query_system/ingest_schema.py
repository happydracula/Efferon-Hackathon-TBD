from data_query_system.db import get_conn
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_invoker import get_embedding

def ingest_data(item):
    conn = get_conn()
    cur = conn.cursor()
    try:
            
        pop_vector = get_embedding(item["Population"], "sentence-transformers/all-minilm-l6-v2")
        pred_vector = get_embedding(item["Predictor"], "sentence-transformers/all-minilm-l6-v2")

        # 3. Insert into Postgres
        query = """
            INSERT INTO study_metadata (
                study_name, population, sample_size, predictor, outcome, 
                timing, method, performance, notes, source, 
                population_embedding, predictor_embedding
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            item["Study"], item["Population"], item["Sample Size"], item["Predictor"], 
            item["Outcome"], item["Timing"], item["Method"], item["Performance"], 
            item["Notes"], item["Source"], pop_vector, pred_vector
        )
        
        cur.execute(query, values)
        conn.commit()
        print(f"Successfully ingested: {item['Study']}")
    finally:
        cur.close()
        conn.close()
