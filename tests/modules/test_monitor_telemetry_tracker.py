"""
Unit Tests for monitor.telemetry_tracker (Real-Time User Safety Telemetry Tracker)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.monitor.telemetry_tracker import TelemetryTracker, get_default_engine

class TestTelemetryTracker:
    def test_initialization(self):
        engine = TelemetryTracker(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_process_heartbeat_packet_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-MON-TEL-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "process_heartbeat_packet")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "monitor.telemetry_tracker"
        assert result["class"] == "TelemetryTracker"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = TelemetryTracker()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
