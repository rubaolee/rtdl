from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3383_owner_face_ambiguity_signal_negative_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3383_owner_face_ambiguity_signal_negative_probe_2026-06-04.md"
SCRIPT = ROOT / "scripts" / "goal3383_owner_face_ambiguity_signal_negative_probe.py"


class Goal3383OwnerFaceAmbiguitySignalNegativeProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.script = SCRIPT.read_text(encoding="utf-8")

    def test_probe_uses_live_optix_candidates_and_exact_only_for_evaluation(self):
        payload = self.payload
        self.assertEqual(payload["schema"], "rtdl.goal3383.owner_face_ambiguity_signal_negative_probe.v1")
        self.assertEqual(payload["goal"], 3383)
        self.assertTrue(payload["candidate_rows_from_optix_device_columns"])
        self.assertTrue(payload["exact_oracle_generated_by_live_optix_run"])
        self.assertTrue(payload["topology_rows_derived_from_cdb"])
        self.assertTrue(payload["incident_rows_derived_from_cdb"])
        self.assertTrue(payload["signal_inputs_exclude_exact_oracle"])
        self.assertTrue(payload["exact_oracle_used_only_for_signal_evaluation"])
        self.assertIn("candidate_device_columns(points)", self.script)
        self.assertIn("prepared.run(points)", self.script)

    def test_true_extra_points_and_best_signal_are_pinned(self):
        payload = self.payload
        self.assertEqual(payload["point_count"], 512)
        self.assertEqual(payload["shape_count"], 478)
        self.assertEqual(payload["optix_candidate_row_count"], 1429)
        self.assertEqual(payload["exact_row_count"], 1417)
        self.assertEqual(payload["candidate_extra_row_count"], 12)
        self.assertEqual(payload["true_extra_point_ids"], [522, 523, 538, 539, 540, 564, 565])
        self.assertEqual(payload["best_simple_signal_name"], "incident_row_eq_3_candidate_face_count_eq_4")
        self.assertEqual(payload["best_simple_signal_false_positive_point_ids"], [651, 652])
        self.assertEqual(payload["best_simple_signal_missed_extra_point_ids"], [])
        self.assertEqual(payload["simple_signal_family_result"], "reject_for_default_route")

    def test_signal_table_rejects_all_tested_default_routes(self):
        signals = {item["name"]: item for item in self.payload["signal_results"]}
        self.assertEqual(signals["candidate_count_ge_3"]["false_positive_count"], 400)
        self.assertEqual(
            signals["candidate_count_gt_incident_max_face_count"]["missed_extra_point_ids"],
            [522, 523],
        )
        self.assertEqual(
            signals["incident_row_eq_3_candidate_face_count_eq_4"]["true_positive_point_ids"],
            [522, 523, 538, 539, 540, 564, 565],
        )
        for signal in signals.values():
            self.assertFalse(signal["default_route_candidate"], signal["name"])

    def test_false_positive_points_are_already_exact_and_must_not_be_filtered_blindly(self):
        rows = {row["point_id"]: row for row in self.payload["interesting_feature_rows"]}
        self.assertEqual(rows[651]["candidate_count"], 4)
        self.assertEqual(rows[651]["exact_count"], 4)
        self.assertEqual(rows[651]["extra_count"], 0)
        self.assertEqual(rows[652]["candidate_count"], 4)
        self.assertEqual(rows[652]["exact_count"], 4)
        self.assertEqual(rows[652]["extra_count"], 0)
        self.assertIn("already match exact", self.report)
        self.assertIn("risk removing valid rows", self.report)

    def test_claim_boundaries_stay_blocked(self):
        for key, value in self.payload["claim_boundary"].items():
            self.assertFalse(value, key)
        self.assertIn("does not authorize a native default route", self.report)
        self.assertIn("claim-boundary flags remain false", self.report)


if __name__ == "__main__":
    unittest.main()
