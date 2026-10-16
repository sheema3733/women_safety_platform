"""
Unit Tests for prepare.travel_safety (Safe Transit Corridor Routing)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.prepare.travel_safety import TransitCorridorMonitor, get_default_engine

class TestTransitCorridorMonitor:
    def test_initialization(self):
        engine = TransitCorridorMonitor(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_evaluate_route_safety_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-PRE-TRA-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "evaluate_route_safety")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "prepare.travel_safety"
        assert result["class"] == "TransitCorridorMonitor"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = TransitCorridorMonitor()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
