This project is an end-to-end automated pipeline designed to transform unstructured medical PDFs into a structured, queryable knowledge base.

##  The Pipeline Flow

### 1. Data Ingestion & Structuring
*   **PDF-to-HTML Conversion:** Ingests raw research papers and converts them into HTML using docling
*   **Hierarchical JSON Parsing:** Parses the HTML into a structured JSON format where keys represent **Headings** and values are **Paragraph Lists**. This ensures the system understands whether a sentence belongs to the *Methods*, *Results*, or *Discussion* section.

### 2. Entity Discovery
*   **Biomarker Identification:** Scans the text to identify specific biological markers (e.g., Lymphocyte count, Procalcitonin).
*   **Population Profiling:** Extracts critical study demographics, including total sample size ($N$), clinical conditions (e.g., Sepsis-3), and geographic location.

### 3. Context Retrieval 
*   **Keyword & Semantic Hybrid Search:** Identifies exact keyword matches to identify potentially relevant sentences. Since a single sentence may not hold all the necessary information, **cosine similarity** and **sentence subject matching** are used to expand the context window to later and previous sentences.
*   **Heuristic Validation:** Uses **Cosine Similarity** against a specialized **Control Text** to extract only relevant windows. This filters out background discussion and focuses exclusively on text containing raw findings and methodology.

### 4. Synthesis & Intelligence
*   **Structured Summarization:** Relevant context is passed to a Large Language Model (LLM) to transform dense prose into a concise, tabular summary.
*   **Vectorized Knowledge Base:** All structured findings are stored in a **Vector Database**.
*   **Real-time RAG:** A Retrieval-Augmented Generation interface allows users to ask complex natural language questions and receive answers grounded strictly in the validated research data.


## Prerequisites

| Requirement | Version |
|---|---|
| Python | ≥ 3.11 |
| PostgreSQL | ≥ 15 |
| pgvector extension | ≥ 0.5 |

### Install pgvector

```bash
# Ubuntu / Debian
sudo apt install postgresql-16-pgvector 

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
# Create .env — at minimum set OPENROUTER_API_KEY
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
