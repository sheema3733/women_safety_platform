"""
Unit Tests for respond.stealth_handlers (Sensor Gesture Triggers & Decoy Handler)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.respond.stealth_handlers import StealthTriggerHandler, get_default_engine

class TestStealthTriggerHandler:
    def test_initialization(self):
        engine = StealthTriggerHandler(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_process_gesture_event_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-RES-STE-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "process_gesture_event")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "respond.stealth_handlers"
        assert result["class"] == "StealthTriggerHandler"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = StealthTriggerHandler()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
