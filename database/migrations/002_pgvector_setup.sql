-- 002_pgvector_setup.sql
-- pgvector extension, halfvec columns, and HNSW indexes

CREATE EXTENSION IF NOT EXISTS vector;

-- Add halfvec embedding column to udm_mappings
ALTER TABLE udm_mappings
    ADD COLUMN IF NOT EXISTS embedding halfvec(1536);

-- HNSW index for cosine similarity search
-- m=16: connections per layer (higher = better recall, more memory)
-- ef_construction=64: search width during index build
CREATE INDEX IF NOT EXISTS idx_udm_embedding_hnsw
    ON udm_mappings
    USING hnsw (embedding halfvec_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Governance policy embeddings for semantic policy matching
ALTER TABLE governance_policies
    ADD COLUMN IF NOT EXISTS description_embedding halfvec(1536);

CREATE INDEX IF NOT EXISTS idx_policy_embedding_hnsw
    ON governance_policies
    USING hnsw (description_embedding halfvec_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Function: semantic UDM search
CREATE OR REPLACE FUNCTION search_udm_semantic(
    query_embedding halfvec(1536),
    match_count INT DEFAULT 10,
    min_similarity FLOAT DEFAULT 0.5
)
RETURNS TABLE (
    id          UUID,
    cip_code    TEXT,
    soc_code    TEXT,
    naics_code  TEXT,
    label       TEXT,
    similarity  FLOAT
)
LANGUAGE SQL
STABLE
AS $$
    SELECT
        id,
        cip_code,
        soc_code,
        naics_code,
        label,
        1 - (embedding <=> query_embedding) AS similarity
    FROM udm_mappings
    WHERE embedding IS NOT NULL
      AND 1 - (embedding <=> query_embedding) >= min_similarity
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;
