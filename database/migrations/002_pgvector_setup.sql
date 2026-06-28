-- 002_pgvector_setup.sql
-- pgvector extension, UDM entity table, HNSW index

BEGIN;

CREATE EXTENSION IF NOT EXISTS vector;

-- ── UDM Entities ──────────────────────────────────────────────────────────────
-- Stores CIP, SOC, and NAICS classification codes with semantic embeddings

CREATE TABLE IF NOT EXISTS udm_entities (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    system      TEXT NOT NULL CHECK (system IN ('CIP', 'SOC', 'NAICS')),
    code        TEXT NOT NULL,
    title       TEXT NOT NULL,
    description TEXT,
    parent_code TEXT,
    level       INT NOT NULL DEFAULT 1,
    embedding   halfvec(1536),
    metadata    JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (system, code)
);

-- ── UDM Crosswalk ─────────────────────────────────────────────────────────────
-- Maps codes across classification systems

CREATE TABLE IF NOT EXISTS udm_crosswalk (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_system     TEXT NOT NULL CHECK (from_system IN ('CIP', 'SOC', 'NAICS')),
    from_code       TEXT NOT NULL,
    to_system       TEXT NOT NULL CHECK (to_system IN ('CIP', 'SOC', 'NAICS')),
    to_code         TEXT NOT NULL,
    confidence      NUMERIC(5,4) NOT NULL DEFAULT 1.0 CHECK (confidence BETWEEN 0 AND 1),
    source          TEXT NOT NULL DEFAULT 'manual',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (from_system, from_code, to_system, to_code)
);

-- ── Indexes ───────────────────────────────────────────────────────────────────

-- Standard lookup indexes
CREATE INDEX IF NOT EXISTS idx_udm_system_code
    ON udm_entities(system, code);

CREATE INDEX IF NOT EXISTS idx_udm_system
    ON udm_entities(system);

CREATE INDEX IF NOT EXISTS idx_udm_parent
    ON udm_entities(system, parent_code)
    WHERE parent_code IS NOT NULL;

-- Trigram index for fuzzy title search
CREATE INDEX IF NOT EXISTS idx_udm_title_trgm
    ON udm_entities USING gin(title gin_trgm_ops);

-- HNSW vector index for cosine similarity (pgvector >= 0.5)
-- ef_construction=64, m=16 — good balance for < 1M rows
CREATE INDEX IF NOT EXISTS idx_udm_embedding_hnsw
    ON udm_entities
    USING hnsw (embedding halfvec_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Crosswalk indexes
CREATE INDEX IF NOT EXISTS idx_crosswalk_from
    ON udm_crosswalk(from_system, from_code);

CREATE INDEX IF NOT EXISTS idx_crosswalk_to
    ON udm_crosswalk(to_system, to_code);

COMMIT;
