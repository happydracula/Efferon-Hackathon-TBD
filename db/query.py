"""
db/query.py
-----------
Query layer for the Sepsis Atlas.

Two query modes
---------------
1. **Semantic search** (`semantic_search`)
   Embeds the natural-language query and returns the *k* most similar
   evidence rows using cosine distance on the pgvector index.

2. **Structured filter** (`structured_query`)
   Keyword / predicate filters on population_type, predictors, outcome, etc.
   Useful for exact look-ups when you know what you want.

Both return a list of plain dicts ready to be serialised as JSON or
rendered in the UI.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from connection import get_conn, put_conn
from embeddings import embed_text


# ---------------------------------------------------------------------------
# Semantic search
# ---------------------------------------------------------------------------

def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Embed *query* and return the *top_k* most relevant evidence rows.

    Returns
    -------
    list of dicts with all columns from the evidence_full view.
    """
    embedding = embed_text(query)
    embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"

    sql = """
    SELECT
        e.id,
        e.paper_id,
        p.title                   AS paper_title,
        f.population_type         AS finding_population,
        e.population_type,
        e.predictors,
        e.affected_or_not,
        e.sample_size,
        e.outcome,
        e.timing,
        e.method,
        e.effect_size,
        e.performance,
        e.notes,
        e.raw_json,
        1 - (e.embedding <=> %s::vector)  AS similarity
    FROM evidence e
    JOIN findings f ON f.id = e.finding_id
    JOIN papers   p ON p.paper_id = e.paper_id
    ORDER BY e.embedding <=> %s::vector
    LIMIT %s
    """

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (embedding_str, embedding_str, top_k))
            cols = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
        return [dict(zip(cols, row)) for row in rows]
    finally:
        put_conn(conn)


# ---------------------------------------------------------------------------
# Structured / keyword query
# ---------------------------------------------------------------------------

def structured_query(
    population: str | None = None,
    predictor: str | None = None,
    outcome: str | None = None,
    affected_only: bool | None = None,
    limit: int = 50,
) -> list[dict]:
    """
    Filter evidence rows by structured fields.

    All parameters are optional and combined with AND.
    Text matches are case-insensitive ILIKE.
    """
    conditions = []
    params: list = []

    if population:
        conditions.append("e.population_type ILIKE %s")
        params.append(f"%{population}%")
    if predictor:
        # Check if the predictor appears in the predictors array (any element)
        conditions.append("EXISTS (SELECT 1 FROM unnest(e.predictors) p WHERE p ILIKE %s)")
        params.append(f"%{predictor}%")
    if outcome:
        conditions.append("e.outcome ILIKE %s")
        params.append(f"%{outcome}%")
    if affected_only is not None:
        conditions.append("e.affected_or_not = %s")
        params.append(affected_only)

    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    sql = f"""
    SELECT
        e.id,
        e.paper_id,
        p.title          AS paper_title,
        e.population_type,
        e.predictors,
        e.affected_or_not,
        e.sample_size,
        e.outcome,
        e.timing,
        e.method,
        e.effect_size,
        e.performance,
        e.notes,
        e.raw_json
    FROM evidence e
    JOIN findings f ON f.id = e.finding_id
    JOIN papers   p ON p.paper_id = e.paper_id
    {where_clause}
    ORDER BY e.created_at DESC
    LIMIT %s
    """
    params.append(limit)

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            cols = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
        return [dict(zip(cols, row)) for row in rows]
    finally:
        put_conn(conn)


# ---------------------------------------------------------------------------
# Helper: list all papers
# ---------------------------------------------------------------------------

def list_papers() -> list[dict]:
    sql = "SELECT paper_id, title, ingested_at FROM papers ORDER BY ingested_at DESC"
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            cols = [desc[0] for desc in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
    finally:
        put_conn(conn)
