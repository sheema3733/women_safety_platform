"""
Unit Tests for respond.triangulation (GPS Coordinate Clustering & Dead-Reckoning)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.respond.triangulation import LocationTriangulator, get_default_engine

class TestLocationTriangulator:
    def test_initialization(self):
        engine = LocationTriangulator(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_refine_coordinate_fix_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-RES-TRI-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "refine_coordinate_fix")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "respond.triangulation"
        assert result["class"] == "LocationTriangulator"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = LocationTriangulator()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
