"""
Unit Tests for report.zero_fir_generator (Automated Statutory Zero FIR Generator)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.report.zero_fir_generator import ZeroFIRGenerator, get_default_engine

class TestZeroFIRGenerator:
    def test_initialization(self):
        engine = ZeroFIRGenerator(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_compile_statutory_fir_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-REP-ZER-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "compile_statutory_fir")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "report.zero_fir_generator"
        assert result["class"] == "ZeroFIRGenerator"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = ZeroFIRGenerator()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
