-- 006_token_verification.sql
-- Execution token session functions and cleanup

BEGIN;

-- ── Issue Execution Token ─────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION issue_execution_token(
    p_tenant_id   UUID,
    p_user_id     UUID,
    p_resource_type TEXT,
    p_resource_id   UUID,
    p_purpose       TEXT,
    p_policy_id     UUID,
    p_token_hash    TEXT,
    p_ttl_seconds   INT DEFAULT 60
) RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_token_id UUID;
BEGIN
    INSERT INTO execution_tokens (
        tenant_id, user_id, resource_type, resource_id,
        purpose, policy_id, token_hash, state, expires_at
    ) VALUES (
        p_tenant_id, p_user_id, p_resource_type, p_resource_id,
        p_purpose, p_policy_id, p_token_hash, 'ISSUED',
        NOW() + (p_ttl_seconds || ' seconds')::INTERVAL
    )
    RETURNING id INTO v_token_id;

    RETURN v_token_id;
END;
$$;

-- ── Consume (validate + mark used) Execution Token ───────────────────────────

CREATE OR REPLACE FUNCTION consume_execution_token(
    p_token_hash  TEXT,
    p_tenant_id   UUID,
    p_user_id     UUID
) RETURNS TABLE (
    valid         BOOLEAN,
    token_id      UUID,
    resource_type TEXT,
    resource_id   UUID,
    purpose       TEXT,
    reason        TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_token RECORD;
BEGIN
    SELECT * INTO v_token
    FROM execution_tokens
    WHERE token_hash = p_token_hash
      AND tenant_id  = p_tenant_id
      AND user_id    = p_user_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RETURN QUERY SELECT false, NULL::UUID, NULL::TEXT, NULL::UUID, NULL::TEXT, 'token_not_found';
        RETURN;
    END IF;

    IF v_token.state = 'CONSUMED' THEN
        RETURN QUERY SELECT false, v_token.id, v_token.resource_type, v_token.resource_id,
                            v_token.purpose, 'token_already_consumed';
        RETURN;
    END IF;

    IF v_token.state = 'EXPIRED' OR v_token.expires_at < NOW() THEN
        -- Mark expired
        UPDATE execution_tokens SET state = 'EXPIRED'
        WHERE id = v_token.id;
        RETURN QUERY SELECT false, v_token.id, v_token.resource_type, v_token.resource_id,
                            v_token.purpose, 'token_expired';
        RETURN;
    END IF;

    -- Mark consumed
    UPDATE execution_tokens
    SET state = 'CONSUMED', consumed_at = NOW()
    WHERE id = v_token.id;

    RETURN QUERY SELECT true, v_token.id, v_token.resource_type, v_token.resource_id,
                        v_token.purpose, 'ok';
END;
$$;

-- ── Expire stale tokens ───────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION expire_stale_tokens()
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    v_count INT;
BEGIN
    UPDATE execution_tokens
    SET state = 'EXPIRED'
    WHERE state IN ('DESIGNED', 'ISSUED')
      AND expires_at < NOW();

    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$;

-- ── Scheduled cleanup (pg_cron compatible comment) ───────────────────────────
-- SELECT cron.schedule('expire-tokens', '* * * * *', 'SELECT expire_stale_tokens()');

GRANT EXECUTE ON FUNCTION issue_execution_token(UUID, UUID, TEXT, UUID, TEXT, UUID, TEXT, INT) TO ioslens_app;
GRANT EXECUTE ON FUNCTION consume_execution_token(TEXT, UUID, UUID) TO ioslens_app;
GRANT EXECUTE ON FUNCTION expire_stale_tokens() TO ioslens_app;

COMMIT;
