import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3643_segment_pair_prepacked_left_sparse_diagnostic_2026-06-06.md"
SUMMARY = ROOT / "docs" / "reports" / "goal3643_segment_pair_prepacked_left_sparse_a5000" / "summary.json"
RUNNER = ROOT / "scripts" / "goal3631_segment_pair_backend_conformance_runner.py"


class Goal3643SegmentPairPrepackedLeftSparseDiagnosticTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.runner = RUNNER.read_text(encoding="utf-8")

    def _sparse_cases(self):
        return {
            case["name"]: case
            for case in self.summary["cases"]
            if case["name"].startswith("sparse_diagonal_grid_")
        }

    def test_artifact_records_prepacked_left_hot_route_and_clean_source(self):
        self.assertEqual(self.summary["git_commit"][:8], "c4a1a3e0")
        self.assertEqual(self.summary["git_tracked_status_short"], "")
        self.assertTrue(self.summary["pod_validation_succeeded"])
        self.assertTrue(self.summary["all_same_contract_counts_match"])
        self.assertTrue(self.summary["prepack_left_for_optix"])
        self.assertEqual(self.summary["max_counts_output"], 4096)

        cases = self._sparse_cases()
        self.assertEqual(
            set(cases),
            {
                "sparse_diagonal_grid_8192",
                "sparse_diagonal_grid_16384",
                "sparse_diagonal_grid_32768",
            },
        )
        for name, case in cases.items():
            size = int(name.rsplit("_", 1)[1])
            dense = case["optix"]["dense_device_count_route"]
            self.assertEqual(case["candidate_pair_count"], size * size)
            self.assertEqual(case["reference"]["hit_pair_count"], size)
            self.assertEqual(dense["hit_pair_count"], size)
            self.assertTrue(case["all_same_contract_counts_match"])
            self.assertTrue(case["optix"]["left_prepacked_for_dense_route"])
            self.assertGreater(case["optix"]["left_prepack_seconds"], 0.0)
            self.assertTrue(dense["counts_truncated"])
            self.assertEqual(dense["counts_full_length"], size)

    def test_prepacked_left_sparse_hot_route_is_fast_but_pack_cost_stays_visible(self):
        cases = self._sparse_cases()
        expected_min_ratios = {
            "sparse_diagonal_grid_8192": 30.0,
            "sparse_diagonal_grid_16384": 70.0,
            "sparse_diagonal_grid_32768": 200.0,
        }
        for name, min_ratio in expected_min_ratios.items():
            case = cases[name]
            cupy_kernel = case["cupy_dense_same_contract"]["seconds"]["dense_kernel"]
            optix_count = case["optix"]["dense_device_count_route"]["seconds"]
            self.assertGreater(cupy_kernel / optix_count, min_ratio, name)
            self.assertGreater(case["optix"]["left_prepack_seconds"], optix_count, name)

    def test_report_and_runner_keep_prepack_boundary_explicit(self):
        self.assertIn("--prepack-left-for-optix", self.runner)
        self.assertIn("prepack_left_for_optix", self.runner)
        self.assertIn("does not authorize", self.report)
        self.assertIn("one-shot app-wall timing", self.report)
        self.assertIn("reusable/prepared left inputs", self.report)
        for flag, value in self.summary["claim_boundary"].items():
            self.assertFalse(value, flag)


if __name__ == "__main__":
    unittest.main()
