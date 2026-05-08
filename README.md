# Sepsis Atlas

AI-powered clinical evidence extraction and retrieval system.
Transforms published sepsis research into a structured, searchable evidence base.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Extraction Pipeline                     │
│  app.py ──► extract_findings.py ──► extract_schema.py   │
│               (LLM: abstract)     (LLM: full sections)  │
└────────────────────────┬────────────────────────────────┘
                         │ list of {finding, evidence}
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  PostgreSQL + pgvector                   │
│  papers ──► findings ──► evidence (+ 1536-dim vector)   │
└────────────────────────┬────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
       FastAPI REST API       Semantic search
       /ingest /search         (cosine ANN)
       /filter /papers
              │
              ▼
       frontend/index.html
       (chat UI + evidence table)
```

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | ≥ 3.11 |
| PostgreSQL | ≥ 15 |
| pgvector extension | ≥ 0.5 |

### Install pgvector

```bash
# Ubuntu / Debian
sudo apt install postgresql-16-pgvector   # adjust version number

# macOS (Homebrew)
brew install pgvector
```

---

## Quick Start

### 1. Clone / copy the project

```bash
cd sepsis_atlas
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env — at minimum set OPENROUTER_API_KEY
```

### 4. Set up the database

```bash
# Option A — automated (runs as postgres superuser)
python setup_db.py

# Option B — manual SQL
psql -U postgres <<'SQL'
CREATE USER sepsis_user WITH PASSWORD 'sepsis_pass';
CREATE DATABASE sepsis_atlas OWNER sepsis_user;
GRANT ALL PRIVILEGES ON DATABASE sepsis_atlas TO sepsis_user;
SQL

psql -U sepsis_user -d sepsis_atlas -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql -U sepsis_user -d sepsis_atlas -f db/schema.sql
```

### 5. Run the extraction pipeline (standalone test)

```bash
cd extraction_pipeline
python app.py                         # prints JSON to stdout (no DB)
python app.py --ingest                # extract + store sample paper in DB
```

### 6. Start the API server

```bash
# From the project root
uvicorn api.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 7. Open the frontend

```bash
# Any static file server works
cd frontend
python -m http.server 3000
```

Then open http://localhost:3000 in your browser.

---

## Ingesting papers

### Single paper (CLI)

```bash
# Your paper must be a JSON file with at least an "abstract" key.
# Add a "paper_id" key for a stable identifier; otherwise the filename is used.
python batch_ingest.py --file my_paper.json
```

### Batch ingestion

```bash
python batch_ingest.py --dir papers/
```

### Via API

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "paper_id": "smith2023",
    "title": "Lactate and 28-day mortality",
    "paper_json": { "abstract": { "Results": "…" }, "Methods": "…" }
  }'
```

---

## Querying

### Semantic search (chat UI or API)

```bash
curl "http://localhost:8000/search?q=lactate+28-day+mortality+septic+shock&top_k=10"
```

### Structured filter

```bash
curl "http://localhost:8000/filter?predictor=SOFA&outcome=mortality&affected_only=true"
```

---

## File structure

```
sepsis_atlas/
├── extraction_pipeline/
│   ├── app.py                  # entry point (also used by API)
│   ├── extract_findings.py     # Step 1 – abstract → findings
│   ├── fetch_relevant_sections.py  # Step 2 – select sections
│   ├── extract_schema.py       # Step 3 – findings → evidence JSON
│   └── llm_invoker.py          # OpenRouter HTTP wrapper
├── db/
│   ├── schema.sql              # PostgreSQL + pgvector DDL
│   ├── connection.py           # psycopg2 pool
│   ├── embeddings.py           # text → vector via OpenRouter
│   ├── ingest.py               # write extraction results to DB
│   └── query.py                # semantic search + structured filters
├── api/
│   └── main.py                 # FastAPI app
├── frontend/
│   └── index.html              # single-file chat UI
├── setup_db.py                 # one-shot DB initialiser
├── batch_ingest.py             # bulk paper ingestion
├── requirements.txt
└── .env.example
```

---

## Changes made to the original extraction pipeline

| File | Change | Reason |
|---|---|---|
| `llm_invoker.py` | Replaced `openrouter` SDK with direct `requests` call | SDK was an undocumented dependency; HTTP call is identical. Added retry logic with exponential back-off. |
| `extract_findings.py` | Widened input type to accept `dict` or `str` | `app.py` passes the full paper dict; extracting the abstract string internally avoids coupling. |
| `fetch_relevant_sections.py` | Replaced duplicate of `CORE_FINDINGS_PROMPT` with actual section-identification logic | The original file contained a paste error — it was a copy of `extract_findings.py`. The real job of this module is to walk the paper JSON and return the relevant sections. |
| `extract_schema.py` | Fixed scope bug: moved `extracted_evidence = []` inside the loop | In the original, the list was declared outside the loop, so every iteration appended to a growing list — evidence from finding N would re-appear in findings N+1, N+2, … |
| `app.py` | Added CLI argument parsing and `--ingest` flag | Makes it easy to run standalone or with DB storage. |
