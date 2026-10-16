"""
Unit Tests for report.witness_intake (Anonymous Witness Statement Intake)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.report.witness_intake import WitnessIntakeEngine, get_default_engine

class TestWitnessIntakeEngine:
    def test_initialization(self):
        engine = WitnessIntakeEngine(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_corroborate_statement_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-REP-WIT-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "corroborate_statement")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "report.witness_intake"
        assert result["class"] == "WitnessIntakeEngine"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = WitnessIntakeEngine()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
