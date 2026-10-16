"""
Unit Tests for learn.bystander_protocols (5Ds Bystander Intervention Framework)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.learn.bystander_protocols import BystanderInterventionModel, get_default_engine

class TestBystanderInterventionModel:
    def test_initialization(self):
        engine = BystanderInterventionModel(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_select_bystander_intervention_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-LEA-BYS-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "select_bystander_intervention")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "learn.bystander_protocols"
        assert result["class"] == "BystanderInterventionModel"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = BystanderInterventionModel()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
