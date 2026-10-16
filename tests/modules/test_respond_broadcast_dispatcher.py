"""
Unit Tests for respond.broadcast_dispatcher (Emergency Broadcast Alert Dispatcher)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.respond.broadcast_dispatcher import BroadcastDispatcher, get_default_engine

class TestBroadcastDispatcher:
    def test_initialization(self):
        engine = BroadcastDispatcher(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_format_emergency_broadcast_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-RES-BRO-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "format_emergency_broadcast")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "respond.broadcast_dispatcher"
        assert result["class"] == "BroadcastDispatcher"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = BroadcastDispatcher()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
