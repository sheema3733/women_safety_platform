"""
Unit Tests for prepare.risk_assessment (Dynamic Multi-Variable Danger Index)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.prepare.risk_assessment import RiskProfile, get_default_engine

class TestRiskProfile:
    def test_initialization(self):
        engine = RiskProfile(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_assess_composite_risk_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-PRE-RIS-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "assess_composite_risk")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "prepare.risk_assessment"
        assert result["class"] == "RiskProfile"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = RiskProfile()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
