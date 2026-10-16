"""
Unit Tests for learn.trauma_recovery (Psychological First Aid & Recovery Guide)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.learn.trauma_recovery import TraumaRecoveryGuide, get_default_engine

class TestTraumaRecoveryGuide:
    def test_initialization(self):
        engine = TraumaRecoveryGuide(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_lookup_trauma_protocol_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-LEA-TRA-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "lookup_trauma_protocol")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "learn.trauma_recovery"
        assert result["class"] == "TraumaRecoveryGuide"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = TraumaRecoveryGuide()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
