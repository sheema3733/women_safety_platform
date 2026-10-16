"""
Unit Tests for learn.legal_handbook (Statutory Rights & Constitutional Safeguards)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.learn.legal_handbook import LegalRightsHandbook, get_default_engine

class TestLegalRightsHandbook:
    def test_initialization(self):
        engine = LegalRightsHandbook(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_query_statutory_rights_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-LEA-LEG-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "query_statutory_rights")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "learn.legal_handbook"
        assert result["class"] == "LegalRightsHandbook"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = LegalRightsHandbook()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
