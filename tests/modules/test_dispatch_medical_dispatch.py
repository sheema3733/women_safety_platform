"""
Unit Tests for dispatch.medical_dispatch (Trauma Center & Hospital Routing Router)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.dispatch.medical_dispatch import MedicalDispatchRouter, get_default_engine

class TestMedicalDispatchRouter:
    def test_initialization(self):
        engine = MedicalDispatchRouter(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_route_to_trauma_center_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-DIS-MED-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "route_to_trauma_center")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "dispatch.medical_dispatch"
        assert result["class"] == "MedicalDispatchRouter"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = MedicalDispatchRouter()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
