"""
Unit Tests for learn.cyber_defense (Cyberstalking & Digital Privacy Defense)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.learn.cyber_defense import CyberDefenseHandbook, get_default_engine

class TestCyberDefenseHandbook:
    def test_initialization(self):
        engine = CyberDefenseHandbook(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_evaluate_social_hardening_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-LEA-CYB-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "evaluate_social_hardening")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "learn.cyber_defense"
        assert result["class"] == "CyberDefenseHandbook"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = CyberDefenseHandbook()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
