"""
api/main.py
-----------
FastAPI REST API for the Sepsis Atlas.

Endpoints
---------
POST /ingest
    Accept a paper JSON body, run the extraction pipeline, store in DB.

GET  /search?q=<natural language query>&top_k=10
    Semantic search over the evidence base.

GET  /filter
    Structured filter: ?population=…&predictor=…&outcome=…&affected_only=true

GET  /papers
    List all ingested papers.

GET  /health
    Liveness probe.
"""

import sys
import os

# Make extraction_pipeline importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "extraction_pipeline"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any

from db.connection import apply_schema
from db.ingest import ingest_extraction_result
from db.query import semantic_search, structured_query, list_papers
from extraction_pipeline.app import run_extraction

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Sepsis Atlas API",
    description="AI-powered clinical evidence extraction and retrieval",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    """Apply DB schema on first start (idempotent CREATE IF NOT EXISTS)."""
    try:
        apply_schema()
    except Exception as exc:
        print(f"[startup] Schema application failed: {exc}")


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class IngestRequest(BaseModel):
    paper_id: str
    title: str | None = None
    paper_json: dict[str, Any]


class IngestResponse(BaseModel):
    paper_id: str
    findings_count: int
    evidence_count: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
def ingest(req: IngestRequest):
    """
    Run the extraction pipeline on *paper_json* and store results in PostgreSQL.
    """
    try:
        result = run_extraction(req.paper_json)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {exc}")

    try:
        ingest_extraction_result(
            paper_id=req.paper_id,
            paper_json=req.paper_json,
            extraction_result=result,
            title=req.title,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"DB ingest failed: {exc}")

    evidence_count = sum(len(item.get("evidence", [])) for item in result)
    return IngestResponse(
        paper_id=req.paper_id,
        findings_count=len(result),
        evidence_count=evidence_count,
    )


@app.get("/search")
def search(
    q: str = Query(..., description="Natural language clinical query"),
    top_k: int = Query(10, ge=1, le=100),
):
    """
    Semantic search: embed the query and return the most relevant evidence rows.
    """
    try:
        results = semantic_search(q, top_k=top_k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"query": q, "results": results, "count": len(results)}


@app.get("/filter")
def filter_evidence(
    population: str | None = Query(None),
    predictor: str | None = Query(None),
    outcome: str | None = Query(None),
    affected_only: bool | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
):
    """
    Structured keyword filter over the evidence table.
    """
    try:
        results = structured_query(
            population=population,
            predictor=predictor,
            outcome=outcome,
            affected_only=affected_only,
            limit=limit,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"results": results, "count": len(results)}


@app.get("/papers")
def papers():
    """List all ingested papers."""
    try:
        return {"papers": list_papers()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
