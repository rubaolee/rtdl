import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3376_owner_face_cupy_optix_candidate_route_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3376_owner_face_cupy_optix_candidate_route_probe_2026-06-04.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3376_owner_face_cupy_optix_candidate_route_probe_2026-06-04.json"


class Goal3376OwnerFaceCupyOptixCandidateRouteProbeTest(unittest.TestCase):
    def test_artifact_records_live_optix_candidate_stream_and_exact_recovery(self):
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["schema"], "rtdl.goal3376.owner_face_cupy_optix_candidate_route_probe.v1")
        self.assertEqual(data["goal"], 3376)
        self.assertEqual(data["rtdl_commit"], "ddc6962c4c23d4bd9091f487d35f029b7b042ef7")
        self.assertEqual(data["gpu"], "NVIDIA RTX A5000, 580.126.09")
        self.assertEqual(data["cupy_version"], "14.1.1")
        self.assertTrue(data["candidate_rows_from_optix_device_columns"])
        self.assertFalse(data["stored_candidate_artifact_used_as_input"])
        self.assertFalse(data["stored_topology_artifact_used_as_input"])
        self.assertFalse(data["stored_incident_artifact_used_as_input"])
        self.assertTrue(data["stored_exact_oracle_artifact_used_as_input"])
        self.assertTrue(data["topology_rows_derived_from_cdb"])
        self.assertTrue(data["incident_rows_derived_from_cdb"])
        self.assertEqual(data["point_count"], 7)
        self.assertEqual(data["cdb_chain_count"], 512)
        self.assertEqual(data["cdb_topology_row_count"], 512)
        self.assertEqual(data["optix_candidate_row_count"], 1429)
        self.assertEqual(data["selected_candidate_row_count"], 26)
        self.assertEqual(data["pipeline_topology_row_count"], 11)
        self.assertEqual(data["incident_row_count"], 21)
        self.assertFalse(data["optix_candidate_overflow"])
        self.assertTrue(data["optix_candidate_device_resident"])
        self.assertGreater(data["optix_candidate_traversal_seconds"], 0.0)
        self.assertTrue(data["owner_face_present_for_all_points"])
        self.assertTrue(data["selected_owner_faces_match_expected"])
        self.assertTrue(data["recovered_shapes_match_exact"])
        self.assertEqual(data["selected_owner_face_by_point"], data["expected_owner_face_by_point"])
        self.assertEqual(data["recovered_shape_ids_by_point"], data["exact_shape_ids_by_point"])
        self.assertEqual(data["live_candidate_shape_ids_by_point"]["522"], [521, 522, 523])
        self.assertEqual(data["live_candidate_shape_ids_by_point"]["538"], [418, 535, 539, 540])
        self.assertFalse(any(data["claim_boundary"].values()))

    def test_report_and_script_keep_live_candidate_boundary_visible(self):
        report = REPORT.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("Live OptiX Candidate Route Probe", report)
        self.assertIn("stored artifact is now only an expected-answer oracle", report)
        self.assertIn("candidate rows, topology rows, and incident rows are not read from stored artifacts", report)
        self.assertIn("not a default route", report)
        self.assertIn("not release evidence", report)
        self.assertIn("RayJoin paper reproduction", report)
        self.assertIn("true-zero-copy", report)
        self.assertIn("candidate_device_columns", script)
        self.assertIn("as_cupy_columns", script)
        self.assertIn("stored_candidate_artifact_used_as_input", script)
        self.assertIn('"stored_candidate_artifact_used_as_input": False', script)


if __name__ == "__main__":
    unittest.main()
