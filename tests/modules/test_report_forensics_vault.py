"""
Unit Tests for report.forensics_vault (Digital Evidence Integrity & Custody Trail)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.report.forensics_vault import ForensicsEvidenceVault, get_default_engine

class TestForensicsEvidenceVault:
    def test_initialization(self):
        engine = ForensicsEvidenceVault(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_register_evidence_item_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-REP-FOR-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "register_evidence_item")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "report.forensics_vault"
        assert result["class"] == "ForensicsEvidenceVault"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = ForensicsEvidenceVault()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
