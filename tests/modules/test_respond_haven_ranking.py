"""
Unit Tests for respond.haven_ranking (Proximity Scoring & Verified Safe Havens)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.respond.haven_ranking import SafeHavenRanker, get_default_engine

class TestSafeHavenRanker:
    def test_initialization(self):
        engine = SafeHavenRanker(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_rank_candidate_havens_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-RES-HAV-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "rank_candidate_havens")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "respond.haven_ranking"
        assert result["class"] == "SafeHavenRanker"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = SafeHavenRanker()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
