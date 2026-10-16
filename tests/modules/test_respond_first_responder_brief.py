"""
Unit Tests for respond.first_responder_brief (Situational Briefing Generator for Police)
Women Safety & Emergency Assistance Platform
"""

import pytest
from app.modules.respond.first_responder_brief import FirstResponseBriefGenerator, get_default_engine

class TestFirstResponseBriefGenerator:
    def test_initialization(self):
        engine = FirstResponseBriefGenerator(tenant_id="TEST_TENANT")
        assert engine.tenant_id == "TEST_TENANT"
        assert engine.is_active is True
        assert len(engine.subsystems) == 25

    def test_generate_incident_brief_execution(self):
        engine = get_default_engine()
        payload = {
            "id": "REQ-TEST-001",
            "node_id": "CAT-RES-FIR-0001",
            "context": {"raw_metric": 60.0}
        }
        result = getattr(engine, "generate_incident_brief")(payload)
        assert "composite_score" in result
        assert result["composite_score"] >= 0.0
        assert result["module"] == "respond.first_responder_brief"
        assert result["class"] == "FirstResponseBriefGenerator"
        assert result["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_audit_summary(self):
        engine = FirstResponseBriefGenerator()
        summary = engine.audit_summary()
        assert summary["active"] is True
        assert summary["subsystems_loaded"] == 25
