"""
Unit Tests for report.jurisdiction_router (Police Station Jurisdictional Router)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.report.jurisdiction_router import JurisdictionRouter, get_default_engine

class TestJurisdictionRouter:
    def test_initialization(self):
        engine = JurisdictionRouter(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_resolve_jurisdiction_station_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-REP-JUR-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "resolve_jurisdiction_station")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "report.jurisdiction_router"
        assert result["class"] == "JurisdictionRouter"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = JurisdictionRouter()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
