"""
Unit Tests for prepare.contact_verification (Emergency Contact Verification Protocol)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.prepare.contact_verification import ContactVerifier, get_default_engine

class TestContactVerifier:
    def test_initialization(self):
        engine = ContactVerifier(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_verify_contact_channel_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-PRE-CON-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "verify_contact_channel")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "prepare.contact_verification"
        assert result["class"] == "ContactVerifier"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = ContactVerifier()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
