import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3645_prepared_segment_left_set_sparse_count_route_2026-06-06.md"
SUMMARY = ROOT / "docs" / "reports" / "goal3645_segment_pair_prepared_left_sparse_a5000" / "summary.json"
RUNNER = ROOT / "scripts" / "goal3631_segment_pair_backend_conformance_runner.py"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
OPTIX_PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
OPTIX_API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"


class Goal3645PreparedSegmentLeftSetSparseCountRouteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.runner = RUNNER.read_text(encoding="utf-8")
        cls.runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        cls.prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")
        cls.api = OPTIX_API.read_text(encoding="utf-8")

    def _sparse_cases(self):
        return {
            case["name"]: case
            for case in self.summary["cases"]
            if case["name"].startswith("sparse_diagonal_grid_")
        }

    def test_artifact_records_clean_prepared_left_route(self):
        self.assertEqual(self.summary["git_commit"][:8], "1276d8d6")
        self.assertEqual(self.summary["git_tracked_status_short"], "")
        self.assertTrue(self.summary["pod_validation_succeeded"])
        self.assertTrue(self.summary["all_same_contract_counts_match"])
        self.assertTrue(self.summary["prepare_left_set_for_optix"])
        self.assertFalse(self.summary["prepack_left_for_optix"])

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
            self.assertTrue(case["optix"]["prepared_left_set_for_dense_route"])
            self.assertGreater(case["optix"]["prepared_left_set_seconds"], 0.0)
            self.assertTrue(dense["counts_truncated"])
            self.assertEqual(dense["counts_full_length"], size)

    def test_prepared_left_hot_route_removes_repeated_upload_bottleneck(self):
        expected_min_ratios = {
            "sparse_diagonal_grid_8192": 40.0,
            "sparse_diagonal_grid_16384": 130.0,
            "sparse_diagonal_grid_32768": 350.0,
        }
        for name, min_ratio in expected_min_ratios.items():
            case = self._sparse_cases()[name]
            cupy_kernel = case["cupy_dense_same_contract"]["seconds"]["dense_kernel"]
            optix_count = case["optix"]["dense_device_count_route"]["seconds"]
            prepared_left_seconds = case["optix"]["prepared_left_set_seconds"]
            self.assertGreater(cupy_kernel / optix_count, min_ratio, name)
            self.assertGreater(prepared_left_seconds, optix_count, name)

    def test_generic_symbols_and_boundary_are_visible(self):
        for symbol in (
            "rtdl_optix_prepare_segment_pair_left_set",
            "rtdl_optix_prepared_segment_pair_left_id_count_prepared_left_device_columns",
            "rtdl_optix_destroy_prepared_segment_pair_left_set",
        ):
            self.assertIn(symbol, self.prelude)
            self.assertIn(symbol, self.api)
            self.assertIn(symbol, self.runtime)
        self.assertIn("prepare_segment_pair_left_set_optix", self.runtime)
        self.assertIn("left_id_count_prepared_left_device_columns", self.runtime)
        self.assertIn("--prepare-left-set-for-optix", self.runner)

        self.assertIn("app-agnostic", self.report)
        self.assertIn("not authorize", self.report)
        self.assertIn("not authorize", self.report)
        self.assertIn("one-shot app-wall timing", self.report)
        for flag, value in self.summary["claim_boundary"].items():
            self.assertFalse(value, flag)


if __name__ == "__main__":
    unittest.main()
