"""
db/ingest.py
------------
Persists extraction pipeline output into PostgreSQL + pgvector.

Flow
----
1.  Upsert the paper into `papers`.
2.  For each (finding, evidence_list) pair from the extraction result:
    a. Insert a row into `findings`.
    b. For each evidence item, generate an embedding and insert into `evidence`.

All writes in a single transaction per paper → either everything lands or
nothing does (safe to re-run if the process is interrupted).
"""

import json
import sys
import os

# Allow importing db modules when called from extraction_pipeline/
sys.path.insert(0, os.path.dirname(__file__))

from connection import get_conn, put_conn
from embeddings import embed_text, build_evidence_text


def _to_pg(val):
    """Serialize dicts/lists to JSON strings for psycopg2.
    Scalars (str, int, float, bool, None) are passed through unchanged.
    """
    return json.dumps(val) if isinstance(val, (dict, list)) else val


def ingest_extraction_result(
    paper_id: str,
    paper_json: dict,
    extraction_result: list[dict],
    title: str | None = None,
) -> None:
    """
    Parameters
    ----------
    paper_id          : unique string identifier for the paper (e.g. DOI or filename)
    paper_json        : the raw paper JSON that was fed to the extraction pipeline
    extraction_result : list of {"finding": …, "evidence": […]} dicts from extract_schema
    title             : optional human-readable title
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # ------------------------------------------------------------------
            # 1. Upsert paper
            # ------------------------------------------------------------------
            cur.execute(
                """
                INSERT INTO papers (paper_id, title, source_json)
                VALUES (%s, %s, %s)
                ON CONFLICT (paper_id) DO UPDATE
                    SET source_json  = EXCLUDED.source_json,
                        title        = COALESCE(EXCLUDED.title, papers.title),
                        ingested_at  = NOW()
                RETURNING id
                """,
                (paper_id, title, json.dumps(paper_json)),
            )

            # ------------------------------------------------------------------
            # 2. Insert findings + evidence
            # ------------------------------------------------------------------
            for item in extraction_result:
                finding = item["finding"]
                evidence_list = item.get("evidence", [])

                # Insert finding row
                cur.execute(
                    """
                    INSERT INTO findings
                        (paper_id, population_type, predictors, affected_or_not)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        paper_id,
                        finding.get("population_type"),
                        finding.get("predictors", []),
                        finding.get("affected_or_not"),
                    ),
                )
                finding_id = cur.fetchone()[0]

                # Insert each evidence row
                for ev in evidence_list:
                    text_for_embedding = build_evidence_text(ev)
                    embedding = embed_text(text_for_embedding)
                    embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"

                    cur.execute(
                        """
                        INSERT INTO evidence (
                            finding_id, paper_id,
                            population_type, predictors, affected_or_not,
                            sample_size, outcome, timing, method,
                            effect_size, performance, notes,
                            embedding, raw_json
                        ) VALUES (
                            %s, %s,
                            %s, %s, %s,
                            %s, %s, %s, %s,
                            %s, %s, %s,
                            %s::vector, %s
                        )
                        """,
                        (
                            finding_id,
                            paper_id,
                            ev.get("population_type"),
                            ev.get("predictors", []),
                            ev.get("affected_or_not"),
                            ev.get("sample_size"),
                            ev.get("outcome"),
                            ev.get("timing"),
                            ev.get("method"),
                            _to_pg(ev.get("effect_size")),
                            _to_pg(ev.get("performance")),
                            ev.get("notes"),
                            embedding_str,
                            json.dumps(ev),
                        ),
                    )

        conn.commit()
        print(f"[ingest] Paper '{paper_id}' committed: "
              f"{len(extraction_result)} finding(s).")
    except Exception:
        conn.rollback()
        raise
    finally:
        put_conn(conn)
