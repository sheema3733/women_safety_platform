"""
Unit Tests for respond.covert_recording (Tamper-Evident Audio Chunking & Vault)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.respond.covert_recording import CovertRecordingVault, get_default_engine

class TestCovertRecordingVault:
    def test_initialization(self):
        engine = CovertRecordingVault(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_sign_recording_chunk_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-RES-COV-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "sign_recording_chunk")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "respond.covert_recording"
        assert result["class"] == "CovertRecordingVault"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = CovertRecordingVault()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
