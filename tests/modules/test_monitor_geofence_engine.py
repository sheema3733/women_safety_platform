"""
Unit Tests for monitor.geofence_engine (Polygon Geofence Boundary Containment)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.monitor.geofence_engine import GeofenceMonitor, get_default_engine

class TestGeofenceMonitor:
    def test_initialization(self):
        engine = GeofenceMonitor(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_evaluate_polygon_containment_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-MON-GEO-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "evaluate_polygon_containment")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "monitor.geofence_engine"
        assert result["class"] == "GeofenceMonitor"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = GeofenceMonitor()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
