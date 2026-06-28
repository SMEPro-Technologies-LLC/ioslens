-- 005_audit_ledger.sql
-- Chained hash audit table functions and triggers

-- Sequence for audit ordering per tenant
CREATE SEQUENCE IF NOT EXISTS audit_sequence_global START 1;

-- Function: compute event hash
CREATE OR REPLACE FUNCTION compute_audit_hash(
    p_prev_hash TEXT,
    p_subject_id UUID,
    p_action TEXT,
    p_resource_type TEXT,
    p_resource_id UUID,
    p_decision TEXT,
    p_created_at TIMESTAMPTZ
)
RETURNS TEXT
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT encode(
        digest(
            p_prev_hash ||
            COALESCE(p_subject_id::text, '') ||
            p_action ||
            p_resource_type ||
            COALESCE(p_resource_id::text, '') ||
            p_decision ||
            p_created_at::text,
            'sha256'
        ),
        'hex'
    );
$$;

-- Function: append audit record with chained hash
CREATE OR REPLACE FUNCTION append_audit_record(
    p_tenant_id     UUID,
    p_subject_id    UUID,
    p_action        TEXT,
    p_resource_type TEXT,
    p_resource_id   UUID,
    p_decision      TEXT,
    p_metadata      JSONB DEFAULT '{}'
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_prev_hash TEXT;
    v_seq       BIGINT;
    v_hash      TEXT;
    v_id        UUID;
    v_now       TIMESTAMPTZ := now();
BEGIN
    -- Get previous hash for this tenant (latest record)
    SELECT event_hash, sequence_no
    INTO v_prev_hash, v_seq
    FROM audit_ledger
    WHERE tenant_id = p_tenant_id
    ORDER BY sequence_no DESC
    LIMIT 1;

    IF NOT FOUND THEN
        v_prev_hash := 'GENESIS';
        v_seq := 0;
    END IF;

    -- Compute new sequence and hash
    v_seq := v_seq + 1;
    v_hash := compute_audit_hash(
        v_prev_hash, p_subject_id, p_action,
        p_resource_type, p_resource_id, p_decision, v_now
    );

    -- Insert record
    INSERT INTO audit_ledger (
        tenant_id, sequence_no, prev_hash, event_hash,
        subject_id, action, resource_type, resource_id,
        decision, metadata, created_at
    ) VALUES (
        p_tenant_id, v_seq, v_prev_hash, v_hash,
        p_subject_id, p_action, p_resource_type, p_resource_id,
        p_decision, p_metadata, v_now
    ) RETURNING id INTO v_id;

    RETURN v_id;
END;
$$;

-- Function: verify audit chain integrity for a tenant
CREATE OR REPLACE FUNCTION verify_audit_chain(
    p_tenant_id UUID,
    p_from_seq  BIGINT DEFAULT 1,
    p_to_seq    BIGINT DEFAULT NULL
)
RETURNS TABLE (
    sequence_no     BIGINT,
    chain_valid     BOOLEAN,
    stored_hash     TEXT,
    computed_hash   TEXT
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    r RECORD;
    v_expected_hash TEXT := 'GENESIS';
BEGIN
    FOR r IN
        SELECT al.sequence_no, al.prev_hash, al.event_hash,
               al.subject_id, al.action, al.resource_type,
               al.resource_id, al.decision, al.created_at
        FROM audit_ledger al
        WHERE al.tenant_id = p_tenant_id
          AND al.sequence_no >= p_from_seq
          AND (p_to_seq IS NULL OR al.sequence_no <= p_to_seq)
        ORDER BY al.sequence_no
    LOOP
        -- Verify prev_hash linkage
        IF r.prev_hash != v_expected_hash THEN
            sequence_no   := r.sequence_no;
            chain_valid   := false;
            stored_hash   := r.event_hash;
            computed_hash := v_expected_hash;
            RETURN NEXT;
        END IF;

        -- Compute expected hash
        v_expected_hash := compute_audit_hash(
            r.prev_hash, r.subject_id, r.action,
            r.resource_type, r.resource_id, r.decision, r.created_at
        );

        sequence_no   := r.sequence_no;
        chain_valid   := (r.event_hash = v_expected_hash);
        stored_hash   := r.event_hash;
        computed_hash := v_expected_hash;
        RETURN NEXT;

        v_expected_hash := r.event_hash;
    END LOOP;
END;
$$;

REVOKE ALL ON FUNCTION append_audit_record FROM PUBLIC;
GRANT EXECUTE ON FUNCTION append_audit_record TO ioslens_app;
GRANT EXECUTE ON FUNCTION verify_audit_chain TO ioslens_app;
