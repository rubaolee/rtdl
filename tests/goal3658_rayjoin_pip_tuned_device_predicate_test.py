from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3658_rayjoin_pip_tuned_device_predicate_2026-06-06.md"
SUMMARY = ROOT / "docs" / "reports" / "goal3658_rayjoin_pip_tuned_device_predicate_a5000" / "summary.json"
RUNNER = ROOT / "scripts" / "goal3244_rayjoin_same_slice_repeated_count_runner.py"
NATIVE = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal3658RayJoinPipTunedDevicePredicateTest(unittest.TestCase):
    def test_report_records_improved_bounded_pip_position_without_release_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "RTDL/OptiX now has the best current same-contract PIP scalar count",
            "still slower than RayJoin query timing",
            "not a paper-reproduction or RTDL-beats-RayJoin claim",
            "app-agnostic",
            "RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS",
            "eps=1e-9",
            "`1.53x` faster than the prior CuPy",
            "does not authorize",
        ):
            self.assertIn(phrase, text)

    def test_summary_is_clean_exact_and_faster_than_prior_cupy_baseline(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        rtdl = payload["rtdl"]
        rayjoin = payload["rayjoin"]
        prior = payload["prior_baselines"]

        self.assertTrue(payload["clean_checkout"])
        self.assertEqual(payload["source_dirty_recorded"], [])
        self.assertEqual(payload["rtdl_commit_recorded"][:8], "9c85c2a0")
        self.assertEqual(rtdl["count"], 1417)
        self.assertTrue(rtdl["counts_consistent"])
        self.assertEqual(rtdl["count_mode"], "device_filtered_prepared_points_validated")
        self.assertEqual(rtdl["internal_query_repeat"], 30000)
        self.assertEqual(rtdl["internal_warmup"], 100)
        self.assertEqual(rtdl["pip_device_predicate_eps"], 1e-9)
        self.assertTrue(rtdl["pip_scalar_count_pipeline"])
        self.assertLess(rtdl["prepared_query_ms"]["median"], prior["goal3595_cupy_dense_ms"])
        self.assertLess(rtdl["prepared_query_ms"]["median"], prior["goal3596_rtdl_exact_prepared_ms"])
        self.assertGreater(rtdl["prepared_query_total_ms"]["median"], 8000.0)
        self.assertGreater(rayjoin["process_wall_ms"]["median"], 6000.0)
        self.assertFalse(rayjoin["positive_assignment_count_available"])
        self.assertGreater(payload["comparison"]["rtdl_over_rayjoin_query_ratio"], 1.0)
        self.assertTrue(all(value is False for value in payload["claim_boundary"].values()))

    def test_native_and_runner_expose_generic_epsilon_without_rayjoin_native_wording(self) -> None:
        runner = RUNNER.read_text(encoding="utf-8")
        native = NATIVE.read_text(encoding="utf-8")

        self.assertIn("--rtdl-pip-device-predicate-eps", runner)
        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS", runner)
        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS", native)
        self.assertIn("finite non-negative number", native)
        self.assertIn("failed to specialize closed-shape membership device predicate epsilon", native)
        self.assertNotIn("RayJoin", native)
        self.assertNotIn("CDB", native)


if __name__ == "__main__":
    unittest.main()
