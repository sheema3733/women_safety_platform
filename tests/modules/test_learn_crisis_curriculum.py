"""
Unit Tests for learn.crisis_curriculum (Crisis Curriculum & Decision Trees)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.learn.crisis_curriculum import CrisisCurriculumEngine, get_default_engine

class TestCrisisCurriculumEngine:
    def test_initialization(self):
        engine = CrisisCurriculumEngine(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_traverse_decision_tree_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-LEA-CRI-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "traverse_decision_tree")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "learn.crisis_curriculum"
        assert result["class"] == "CrisisCurriculumEngine"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = CrisisCurriculumEngine()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
