from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3381_owner_face_selective_live_route_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3381_owner_face_selective_live_route_probe_2026-06-04.md"
SCRIPT = ROOT / "scripts" / "goal3381_owner_face_selective_live_route_probe.py"


class Goal3381OwnerFaceSelectiveLiveRouteProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.script = SCRIPT.read_text(encoding="utf-8")

    def test_full_slice_matches_live_exact_oracle(self):
        payload = self.payload
        self.assertEqual(payload["schema"], "rtdl.goal3381.owner_face_selective_live_route_probe.v1")
        self.assertEqual(payload["goal"], 3381)
        self.assertTrue(payload["candidate_rows_from_optix_device_columns"])
        self.assertTrue(payload["exact_oracle_generated_by_live_optix_run"])
        self.assertTrue(payload["topology_rows_derived_from_cdb"])
        self.assertTrue(payload["incident_rows_derived_from_cdb"])
        self.assertEqual(payload["point_count"], 512)
        self.assertEqual(payload["shape_count"], 478)
        self.assertEqual(payload["optix_candidate_row_count"], 1429)
        self.assertEqual(payload["exact_row_count"], 1417)
        self.assertEqual(payload["filtered_row_count"], 1417)
        self.assertTrue(payload["matches_exact"])
        self.assertEqual(payload["missing_exact_row_count"], 0)
        self.assertEqual(payload["extra_row_count"], 0)

    def test_selective_pipeline_repairs_only_caller_supplied_ambiguity_set(self):
        payload = self.payload
        self.assertEqual(
            payload["selected_point_source"],
            "caller_supplied_goal3328_known_mismatch_points",
        )
        self.assertEqual(
            payload["selected_owner_face_source"],
            "caller_supplied_fixture_policy_for_known_mismatch_points",
        )
        self.assertEqual(payload["selected_point_ids"], [522, 523, 538, 539, 540, 564, 565])
        self.assertEqual(payload["selected_candidate_row_count"], 26)
        self.assertEqual(payload["selected_exact_row_count"], 14)
        self.assertEqual(payload["selected_filtered_row_count"], 14)
        self.assertEqual(payload["passthrough_candidate_row_count"], 1403)
        self.assertEqual(payload["candidate_extra_row_count_before_filter"], 12)
        self.assertEqual(payload["removed_candidate_extra_row_count"], 12)
        self.assertTrue(payload["selected_output_matches_exact"])
        self.assertTrue(payload["owner_face_present_for_all_selected_points"])
        self.assertTrue(payload["selected_owner_faces_match_expected"])
        self.assertEqual(
            payload["removed_candidate_extra_sample"],
            [
                [522, 521],
                [523, 521],
                [538, 418],
                [538, 540],
                [539, 418],
                [539, 540],
                [540, 535],
                [540, 539],
                [564, 437],
                [564, 559],
                [565, 437],
                [565, 559],
            ],
        )

    def test_stored_artifacts_are_not_used_as_route_inputs(self):
        payload = self.payload
        self.assertFalse(payload["stored_candidate_artifact_used_as_input"])
        self.assertFalse(payload["stored_topology_artifact_used_as_input"])
        self.assertFalse(payload["stored_incident_artifact_used_as_input"])
        self.assertFalse(payload["stored_exact_oracle_artifact_used_as_input"])

    def test_claim_boundary_blocks_public_and_default_route_claims(self):
        boundary = self.payload["claim_boundary"]
        for key, value in boundary.items():
            self.assertFalse(value, key)
        self.assertIn("does not authorize a default route", self.report)
        self.assertIn("does not infer those points automatically", self.report)
        self.assertIn("claim-boundary flags remain false", self.report)

    def test_probe_uses_live_candidates_and_selective_cupy_continuation(self):
        self.assertIn("candidate_device_columns(points)", self.script)
        self.assertIn("as_cupy_columns()", self.script)
        self.assertIn("run_selective_closed_shape_owner_face_priority_membership_pipeline_cupy", self.script)
        self.assertIn("prepared.run(points)", self.script)
        self.assertIn("caller-supplied ambiguity set", self.report)


if __name__ == "__main__":
    unittest.main()
