"""
Unit Tests for prepare.duress_protocols (Covert Panic Triggers & Silent Duress PIN)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.prepare.duress_protocols import DuressProtocolManager, get_default_engine

class TestDuressProtocolManager:
    def test_initialization(self):
        engine = DuressProtocolManager(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_validate_duress_pin_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-PRE-DUR-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "validate_duress_pin")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "prepare.duress_protocols"
        assert result["class"] == "DuressProtocolManager"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = DuressProtocolManager()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
