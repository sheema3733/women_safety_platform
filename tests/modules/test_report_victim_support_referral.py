"""
Unit Tests for report.victim_support_referral (Crisis Center & Legal Aid Referral Router)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.report.victim_support_referral import VictimSupportRouter, get_default_engine

class TestVictimSupportRouter:
    def test_initialization(self):
        engine = VictimSupportRouter(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_recommend_crisis_center_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-REP-VIC-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "recommend_crisis_center")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "report.victim_support_referral"
        assert result["class"] == "VictimSupportRouter"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = VictimSupportRouter()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
