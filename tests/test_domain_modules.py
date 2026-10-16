"""
Tests for Women Safety Platform Enterprise Domain Modules
"""

import pytest
from app.modules.prepare.risk_assessment import RiskProfile, haversine_distance, point_in_polygon
from app.modules.prepare.hazard_matrix import WardHazardMatrix
from app.modules.respond.escalation_engine import SOSEscalationEngine
from app.modules.respond.triangulation import LocationTriangulator
from app.modules.respond.haven_ranking import SafeHavenRanker
from app.modules.report.incident_taxonomy import IncidentTaxonomyModel
from app.modules.monitor.geofence_engine import GeofenceMonitor
from app.modules.monitor.audit_verifier import AuditLedgerVerifier
from app.modules.learn.crisis_curriculum import CrisisCurriculumEngine
from app.modules.dispatch.municipal_adapters import MunicipalDispatchGateway

class TestDomainModules:
    def test_haversine_distance(self):
        # Distance between Bangalore (12.9716, 77.5946) and Mysore (12.2958, 76.6394) is ~128 km
        d = haversine_distance(12.9716, 77.5946, 12.2958, 76.6394)
        assert 120 < d < 140

    def test_point_in_polygon(self):
        poly = [(12.0, 77.0), (13.0, 77.0), (13.0, 78.0), (12.0, 78.0)]
        assert point_in_polygon(12.5, 77.5, poly) is True
        assert point_in_polygon(14.0, 77.5, poly) is False

    def test_risk_assessment_engine(self):
        engine = RiskProfile()
        payload = {
            "id": "REQ-TEST-01",
            "node_id": "CAT-PRE-RIS-0001",
            "context": {"raw_metric": 65.0}
        }
        res = engine.assess_composite_risk(payload)
        assert "composite_score" in res
        assert res["status"] in ["APPROVED", "FLAGGED"]
        assert len(engine.execution_ledger) == 1

    def test_ward_hazard_matrix(self):
        engine = WardHazardMatrix()
        payload = {"id": "HAZ-001", "node_id": "CAT-PRE-HAZ-0005"}
        res = engine.lookup_ward_hazard_level(payload)
        assert res["composite_score"] > 0

    def test_sos_escalation_engine(self):
        engine = SOSEscalationEngine()
        payload = {
            "id": "SOS-EVT-99",
            "node_id": "CAT-RES-ESC-0010",
            "context": {"raw_metric": 80.0}
        }
        res = engine.transition_alert_tier(payload)
        assert res["status"] in ["APPROVED", "FLAGGED"]
        assert res["subsystem_evaluations"] == 25

    def test_location_triangulation(self):
        engine = LocationTriangulator()
        payload = {"id": "TRI-01", "node_id": "CAT-RES-TRI-0002"}
        res = engine.refine_coordinate_fix(payload)
        assert res["module"] == "respond.triangulation"

    def test_safe_haven_ranking(self):
        engine = SafeHavenRanker()
        payload = {"id": "HAV-01", "node_id": "CAT-RES-HAV-0003"}
        res = engine.rank_candidate_havens(payload)
        assert res["composite_score"] >= 0

    def test_incident_taxonomy(self):
        engine = IncidentTaxonomyModel()
        payload = {"id": "INC-TAX-01", "node_id": "CAT-REP-INC-0001"}
        res = engine.classify_incident_statutes(payload)
        assert res["module"] == "report.incident_taxonomy"

    def test_geofence_monitor(self):
        engine = GeofenceMonitor()
        payload = {"id": "GEO-01", "node_id": "CAT-MON-GEO-0001"}
        res = engine.evaluate_polygon_containment(payload)
        assert res["composite_score"] >= 0

    def test_audit_ledger_verifier(self):
        engine = AuditLedgerVerifier()
        payload = {"id": "AUD-01", "node_id": "CAT-MON-AUD-0001"}
        res = engine.verify_merkle_root(payload)
        assert res["subsystem_evaluations"] == 25

    def test_crisis_curriculum(self):
        engine = CrisisCurriculumEngine()
        payload = {"id": "CURR-01", "node_id": "CAT-LEA-CRI-0001"}
        res = engine.traverse_decision_tree(payload)
        assert res["module"] == "learn.crisis_curriculum"

    def test_municipal_dispatch_gateway(self):
        engine = MunicipalDispatchGateway()
        payload = {"id": "DISP-01", "node_id": "CAT-DIS-MUN-0001"}
        res = engine.dispatch_emergency_payload(payload)
        assert res["composite_score"] >= 0
