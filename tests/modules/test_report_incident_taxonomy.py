"""
Unit Tests for report.incident_taxonomy (Statutory Incident Classification Models)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.report.incident_taxonomy import IncidentTaxonomyModel, get_default_engine

class TestIncidentTaxonomyModel:
    def test_initialization(self):
        engine = IncidentTaxonomyModel(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_classify_incident_statutes_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-REP-INC-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "classify_incident_statutes")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "report.incident_taxonomy"
        assert result["class"] == "IncidentTaxonomyModel"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = IncidentTaxonomyModel()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
