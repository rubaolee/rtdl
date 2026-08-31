from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOPOLOGY = ROOT / "src" / "rtdsl" / "closed_shape_topology.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
SCRIPT = ROOT / "scripts" / "goal3427_prepared_cupy_refiner_timing_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3427_prepared_cupy_refiner_timing_2026-06-04.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3427_prepared_cupy_refiner_timing_probe_2026-06-04.json"


class Goal3427PreparedCupyRefinerTimingTest(unittest.TestCase):
    def test_prepared_refiner_is_exported_and_device_resident(self):
        topology = TOPOLOGY.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")

        self.assertIn("class PreparedClosedShapeMembershipCandidateRefinerCupy", topology)
        self.assertIn("prepare_closed_shape_membership_candidate_refiner_exact_cupy", topology)
        self.assertIn("cupy_device_prepared_lookup_columns", topology)
        self.assertIn("prepared CuPy refiner requires point and shape ordinal columns", topology)
        self.assertIn("PreparedClosedShapeMembershipCandidateRefinerCupy", init)
        self.assertIn("prepare_closed_shape_membership_candidate_refiner_exact_cupy", init)

    def test_timing_probe_compares_one_shot_and_prepared_paths(self):
        script = SCRIPT.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("one_shot_cupy_refine_sec", script)
        self.assertIn("prepared_cupy_refine_sec", script)
        self.assertIn("prepared_refine_vs_one_shot_median", script)
        self.assertIn("prepared_total_vs_host_median", script)
        self.assertIn("claim_boundary", script)
        self.assertIn("reusable partner helper", report)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3427 pod artifact pending")
    def test_pod_artifact_records_prepared_refiner_timing(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3427.prepared_cupy_refiner_timing_probe.v1")
        self.assertEqual(payload["goal"], 3427)
        self.assertIn("NVIDIA", payload["gpu"])
        self.assertEqual(payload["point_count"], 16545)
        self.assertEqual(payload["shape_count"], 15700)
        self.assertEqual(payload["host_exact_row_count"], 47262)
        self.assertEqual(payload["candidate_row_count"], 47570)
        self.assertEqual(payload["prepared_refined_row_count"], 47262)
        self.assertTrue(payload["all_prepared_counts_match_host"])
        self.assertLess(payload["prepared_refine_vs_one_shot_median"], 1.0)
        for value in payload["claim_boundary"].values():
            self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
