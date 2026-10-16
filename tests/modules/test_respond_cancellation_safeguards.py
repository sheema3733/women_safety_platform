"""
Unit Tests for respond.cancellation_safeguards (Duress Cancellation & Forced Abort Traps)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.respond.cancellation_safeguards import CancellationSafeguard, get_default_engine

class TestCancellationSafeguard:
    def test_initialization(self):
        engine = CancellationSafeguard(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_validate_cancellation_attempt_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-RES-CAN-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "validate_cancellation_attempt")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "respond.cancellation_safeguards"
        assert result["class"] == "CancellationSafeguard"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = CancellationSafeguard()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
