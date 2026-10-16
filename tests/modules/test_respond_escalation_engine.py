"""
Unit Tests for respond.escalation_engine (Multi-Tier SOS Alert State Machine)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.respond.escalation_engine import SOSEscalationEngine, get_default_engine

class TestSOSEscalationEngine:
    def test_initialization(self):
        engine = SOSEscalationEngine(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_transition_alert_tier_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-RES-ESC-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "transition_alert_tier")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "respond.escalation_engine"
        assert result["class"] == "SOSEscalationEngine"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = SOSEscalationEngine()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
