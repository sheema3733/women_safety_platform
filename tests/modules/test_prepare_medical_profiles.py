"""
Unit Tests for prepare.medical_profiles (Special Assistance & Medication Registry)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.prepare.medical_profiles import MedicalSafetyRegistry, get_default_engine

class TestMedicalSafetyRegistry:
    def test_initialization(self):
        engine = MedicalSafetyRegistry(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_retrieve_medical_profile_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-PRE-MED-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "retrieve_medical_profile")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "prepare.medical_profiles"
        assert result["class"] == "MedicalSafetyRegistry"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = MedicalSafetyRegistry()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
