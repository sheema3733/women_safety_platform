"""
Unit Tests for monitor.admin_triage_sla (Admin Triage SLA & Response Timers)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.monitor.admin_triage_sla import AdminTriageSLAMonitor, get_default_engine

class TestAdminTriageSLAMonitor:
    def test_initialization(self):
        engine = AdminTriageSLAMonitor(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_evaluate_triage_sla_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-MON-ADM-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "evaluate_triage_sla")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "monitor.admin_triage_sla"
        assert result["class"] == "AdminTriageSLAMonitor"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = AdminTriageSLAMonitor()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
