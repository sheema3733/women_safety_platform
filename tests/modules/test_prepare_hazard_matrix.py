"""
Unit Tests for prepare.hazard_matrix (Metropolitan Ward Geo-Hazard Indices)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.prepare.hazard_matrix import WardHazardMatrix, get_default_engine

class TestWardHazardMatrix:
    def test_initialization(self):
        engine = WardHazardMatrix(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_lookup_ward_hazard_level_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-PRE-HAZ-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "lookup_ward_hazard_level")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "prepare.hazard_matrix"
        assert result["class"] == "WardHazardMatrix"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = WardHazardMatrix()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
