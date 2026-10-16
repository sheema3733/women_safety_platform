"""
Unit Tests for prepare.privacy_audit (Digital Footprint Hardening Scanner)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.prepare.privacy_audit import PrivacyAuditScanner, get_default_engine

class TestPrivacyAuditScanner:
    def test_initialization(self):
        engine = PrivacyAuditScanner(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_audit_device_privacy_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-PRE-PRI-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "audit_device_privacy")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "prepare.privacy_audit"
        assert result["class"] == "PrivacyAuditScanner"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = PrivacyAuditScanner()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
