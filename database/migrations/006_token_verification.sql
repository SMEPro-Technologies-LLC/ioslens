-- 006_token_verification.sql
-- Execution token session functions for DESIGNED-state tokens

-- Clean up expired tokens (called periodically by background job)
CREATE OR REPLACE FUNCTION purge_expired_tokens()
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_count INTEGER;
BEGIN
    DELETE FROM execution_tokens
    WHERE expires_at < now()
       OR revoked = true;

    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$;

-- Verify a token is valid and not replayed
CREATE OR REPLACE FUNCTION verify_execution_token(
    p_jti       TEXT,
    p_tenant_id UUID,
    p_subject_id UUID,
    p_purpose   TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_token execution_tokens%ROWTYPE;
BEGIN
    SELECT * INTO v_token
    FROM execution_tokens
    WHERE jti = p_jti
      AND tenant_id = p_tenant_id
      AND subject_id = p_subject_id
      AND purpose = p_purpose
      AND revoked = false
      AND expires_at > now();

    RETURN FOUND;
END;
$$;

-- Revoke a token immediately
CREATE OR REPLACE FUNCTION revoke_execution_token(p_jti TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_count INTEGER;
BEGIN
    UPDATE execution_tokens
    SET revoked = true, revoked_at = now()
    WHERE jti = p_jti AND revoked = false;

    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count > 0;
END;
$$;

-- Index for fast JTI lookups
CREATE INDEX IF NOT EXISTS idx_tokens_jti_active
    ON execution_tokens (jti)
    WHERE revoked = false AND expires_at > now();

REVOKE ALL ON FUNCTION purge_expired_tokens FROM PUBLIC;
REVOKE ALL ON FUNCTION revoke_execution_token FROM PUBLIC;
GRANT EXECUTE ON FUNCTION verify_execution_token TO ioslens_app;
GRANT EXECUTE ON FUNCTION revoke_execution_token TO ioslens_app;
