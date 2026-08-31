import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3639_segment_pair_sparse_grid_rt_index_diagnostic_2026-06-06.md"
SUMMARY = ROOT / "docs" / "reports" / "goal3639_segment_pair_sparse_grid_a5000" / "summary.json"
LARGE_SUMMARY = ROOT / "docs" / "reports" / "goal3639_segment_pair_sparse_grid_a5000" / "large_summary.json"
RUNNER = ROOT / "scripts" / "goal3631_segment_pair_backend_conformance_runner.py"


class Goal3639SegmentPairSparseGridRtIndexDiagnosticTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.large_summary = json.loads(LARGE_SUMMARY.read_text(encoding="utf-8"))
        cls.runner = RUNNER.read_text(encoding="utf-8")

    def _sparse_cases(self):
        return [
            case
            for payload in (self.summary, self.large_summary)
            for case in payload["cases"]
            if case["name"].startswith("sparse_diagonal_grid_")
        ]

    def test_artifacts_record_clean_source_and_matching_sparse_cases(self):
        for payload in (self.summary, self.large_summary):
            self.assertEqual(payload["git_commit"][:8], "89bae35b")
            self.assertEqual(payload["git_tracked_status_short"], "")
            self.assertTrue(payload["pod_validation_succeeded"])
            self.assertTrue(payload["all_same_contract_counts_match"])

        cases = {case["name"]: case for case in self._sparse_cases()}
        self.assertEqual(
            set(cases),
            {
                "sparse_diagonal_grid_1024",
                "sparse_diagonal_grid_2048",
                "sparse_diagonal_grid_4096",
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

    def test_large_sparse_cases_show_rt_index_crossover_without_public_claim(self):
        cases = {case["name"]: case for case in self._sparse_cases()}
        for name in ("sparse_diagonal_grid_8192", "sparse_diagonal_grid_16384", "sparse_diagonal_grid_32768"):
            case = cases[name]
            cupy_kernel = case["cupy_dense_same_contract"]["seconds"]["dense_kernel"]
            optix_wall = case["optix"]["dense_device_count_route"]["seconds"]
            self.assertGreater(cupy_kernel / optix_wall, 1.0, name)

        fastest = cases["sparse_diagonal_grid_32768"]
        cupy_kernel = fastest["cupy_dense_same_contract"]["seconds"]["dense_kernel"]
        optix_wall = fastest["optix"]["dense_device_count_route"]["seconds"]
        self.assertGreater(cupy_kernel / optix_wall, 5.0)

        for flag, value in self.summary["claim_boundary"].items():
            self.assertFalse(value, flag)
        for flag, value in self.large_summary["claim_boundary"].items():
            self.assertFalse(value, flag)

    def test_report_and_runner_keep_boundary_and_sparse_case_visible(self):
        self.assertIn("not a RayJoin reproduction", self.report)
        self.assertIn("not a public broad speedup claim", self.report)
        self.assertIn("credible sparse-index win", self.report)
        self.assertIn("--sparse-grid-sizes", self.runner)
        self.assertIn("_make_sparse_diagonal_grid_case", self.runner)


if __name__ == "__main__":
    unittest.main()
