import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3374_owner_face_cupy_runtime_cdb_route_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3374_owner_face_cupy_runtime_cdb_route_probe_2026-06-04.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3374_owner_face_cupy_runtime_cdb_route_probe_2026-06-04.json"


class Goal3374OwnerFaceCupyRuntimeCdbRouteProbeTest(unittest.TestCase):
    def test_artifact_records_runtime_cdb_derivation_and_exact_recovery(self):
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["schema"], "rtdl.goal3374.owner_face_cupy_runtime_cdb_route_probe.v1")
        self.assertEqual(data["goal"], 3374)
        self.assertEqual(data["rtdl_commit"], "4cc57bc49fab9e06532e7cbd08b38fb81e1ae570")
        self.assertEqual(data["gpu"], "NVIDIA RTX A5000, 580.126.09")
        self.assertEqual(data["cupy_version"], "14.1.1")
        self.assertTrue(data["topology_rows_derived_from_cdb"])
        self.assertTrue(data["incident_rows_derived_from_cdb"])
        self.assertFalse(data["stored_topology_artifact_used_as_input"])
        self.assertFalse(data["stored_incident_artifact_used_as_input"])
        self.assertTrue(data["candidate_oracle_artifact_used_as_input"])
        self.assertEqual(data["point_count"], 7)
        self.assertEqual(data["cdb_chain_count"], 512)
        self.assertEqual(data["cdb_topology_row_count"], 512)
        self.assertEqual(data["pipeline_topology_row_count"], 11)
        self.assertEqual(data["incident_row_count"], 21)
        self.assertEqual(data["candidate_row_count"], 26)
        self.assertTrue(data["owner_face_present_for_all_points"])
        self.assertTrue(data["selected_owner_faces_match_expected"])
        self.assertTrue(data["recovered_shapes_match_exact"])
        self.assertEqual(data["selected_owner_face_by_point"], data["expected_owner_face_by_point"])
        self.assertEqual(data["recovered_shape_ids_by_point"], data["exact_shape_ids_by_point"])
        self.assertFalse(any(data["claim_boundary"].values()))

    def test_report_and_script_keep_runtime_scope_and_boundary_visible(self):
        report = REPORT.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("Runtime-CDB route probe", report)
        self.assertIn("candidate/exact mismatch set still comes from the stored Goal3328 oracle", report)
        self.assertIn("does not authorize release", report)
        self.assertIn("not native RT traversal", report)
        self.assertIn("true zero-copy", report)
        self.assertIn("RayJoin paper reproduction", report)
        self.assertIn("chains_to_topology_rows", script)
        self.assertIn("chains_to_incident_face_candidate_rows", script)
        self.assertIn('"stored_incident_artifact_used_as_input": False', script)
        self.assertIn('"stored_topology_artifact_used_as_input": False', script)


if __name__ == "__main__":
    unittest.main()
