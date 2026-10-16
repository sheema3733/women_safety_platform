"""
Unit Tests for report.pattern_detector (Spatial-Temporal Incident Pattern Detector)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.report.pattern_detector import IncidentPatternDetector, get_default_engine

class TestIncidentPatternDetector:
    def test_initialization(self):
        engine = IncidentPatternDetector(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_detect_incident_clusters_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-REP-PAT-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "detect_incident_clusters")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "report.pattern_detector"
        assert result["class"] == "IncidentPatternDetector"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = IncidentPatternDetector()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
