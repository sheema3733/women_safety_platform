"""
Unit Tests for monitor.community_index (Metropolitan Safety Readiness Index)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.monitor.community_index import CommunitySafetyIndex, get_default_engine

class TestCommunitySafetyIndex:
    def test_initialization(self):
        engine = CommunitySafetyIndex(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_aggregate_ward_safety_index_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-MON-COM-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "aggregate_ward_safety_index")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "monitor.community_index"
        assert result["class"] == "CommunitySafetyIndex"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = CommunitySafetyIndex()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
