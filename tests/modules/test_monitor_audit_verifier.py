"""
Unit Tests for monitor.audit_verifier (Merkle Tree Audit Ledger Verifier)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.monitor.audit_verifier import AuditLedgerVerifier, get_default_engine

class TestAuditLedgerVerifier:
    def test_initialization(self):
        engine = AuditLedgerVerifier(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_verify_merkle_root_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-MON-AUD-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "verify_merkle_root")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "monitor.audit_verifier"
        assert result["class"] == "AuditLedgerVerifier"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = AuditLedgerVerifier()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
