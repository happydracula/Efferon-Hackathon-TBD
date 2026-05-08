-- schema.sql
-- Complete database schema for the Sepsis Atlas
-- Requires PostgreSQL >= 15 and the pgvector extension.

-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- TABLE: papers
-- One row per ingested paper / document.
-- ============================================================
CREATE TABLE IF NOT EXISTS papers (
    id            SERIAL PRIMARY KEY,
    paper_id      TEXT NOT NULL UNIQUE,   -- caller-supplied identifier (e.g. DOI, filename)
    title         TEXT,
    source_json   JSONB NOT NULL,         -- full raw paper JSON as stored
    ingested_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- TABLE: findings
-- One row per (paper, finding) pair from the extraction pipeline.
-- A "finding" is the high-level triple: population / predictors / affected.
-- ============================================================
CREATE TABLE IF NOT EXISTS findings (
    id              SERIAL PRIMARY KEY,
    paper_id        TEXT NOT NULL REFERENCES papers(paper_id) ON DELETE CASCADE,
    population_type TEXT,
    predictors      TEXT[],               -- array of predictor names
    affected_or_not BOOLEAN,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_findings_paper_id ON findings(paper_id);

-- ============================================================
-- TABLE: evidence
-- One row per detailed evidence record extracted for a finding.
-- This maps directly to the DETAILED_EXTRACTION_PROMPT output schema.
-- ============================================================
CREATE TABLE IF NOT EXISTS evidence (
    id              SERIAL PRIMARY KEY,
    finding_id      INTEGER NOT NULL REFERENCES findings(id) ON DELETE CASCADE,
    paper_id        TEXT    NOT NULL REFERENCES papers(paper_id) ON DELETE CASCADE,

    -- Core evidence fields (mirrors the JSON schema from extract_schema.py)
    population_type TEXT,
    predictors      TEXT[],
    affected_or_not BOOLEAN,
    sample_size     TEXT,
    outcome         TEXT,
    timing          TEXT,
    method          TEXT,
    effect_size     TEXT,
    performance     TEXT,
    notes           TEXT,

    -- pgvector embedding for semantic search
    -- Dimension 1536 = text-embedding-3-small; change to 3072 for large, 768 for ada
    embedding       vector(1536),

    -- Full evidence snapshot for traceability
    raw_json        JSONB NOT NULL,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evidence_finding_id ON evidence(finding_id);
CREATE INDEX IF NOT EXISTS idx_evidence_paper_id   ON evidence(paper_id);

-- IVFFlat index for approximate nearest-neighbour search on embeddings.
-- lists = sqrt(expected row count); rebuild after bulk loads.
CREATE INDEX IF NOT EXISTS idx_evidence_embedding
    ON evidence USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 10);

-- ============================================================
-- VIEW: evidence_full
-- Convenience join for API queries — returns evidence enriched
-- with paper and finding metadata.
-- ============================================================
CREATE OR REPLACE VIEW evidence_full AS
SELECT
    e.id,
    e.paper_id,
    p.title                   AS paper_title,
    f.population_type         AS finding_population,
    f.predictors              AS finding_predictors,
    f.affected_or_not         AS finding_affected,
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
    e.created_at
FROM evidence e
JOIN findings f ON f.id = e.finding_id
JOIN papers   p ON p.paper_id = e.paper_id;
