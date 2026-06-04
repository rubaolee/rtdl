from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3244_rayjoin_same_slice_repeated_count_runner.py"
SPEC = importlib.util.spec_from_file_location("goal3244_runner", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Goal3244RayJoinSameSliceRepeatedCountRunnerTest(unittest.TestCase):
    def test_parse_rayjoin_lsi_log_extracts_count_and_timings(self) -> None:
        parsed = MODULE.parse_rayjoin_query_log(
            """
I20260604 run_query.cu:301] Iter: 4
I20260604 run_query.cu:306] Intersections: 269 Queue Load Factor: 0.0501678
Timing results:
 - Build Index: 0.428915 ms
 - Warmup: 1.20902 ms
 - Query: 0.229406 ms
"""
        )

        self.assertEqual(parsed["intersections"], 269)
        self.assertEqual(parsed["build_index_ms"], 0.428915)
        self.assertEqual(parsed["warmup_ms"], 1.20902)
        self.assertEqual(parsed["query_ms"], 0.229406)
        self.assertFalse(parsed["positive_assignment_count_available"])

    def test_parse_rayjoin_pip_log_tracks_checker_without_count(self) -> None:
        parsed = MODULE.parse_rayjoin_query_log(
            """
I20260604 rt_engine.cu:554] optixLaunch, [w,h,d] = 25392,1,1
I20260604 run_query.cu:97] Map: 0 passed check
Timing results:
 - Warmup: 1.00303 ms
 - Query: 0.185776 ms
"""
        )

        self.assertIsNone(parsed["intersections"])
        self.assertTrue(parsed["checker_passed"])
        self.assertEqual(parsed["optix_launch_widths"], [25392])
        self.assertFalse(parsed["positive_assignment_count_available"])

    def test_comparison_rows_keep_pip_boundary_and_lsi_count_contract(self) -> None:
        rayjoin = {
            "lsi": {
                "query_ms_reported": {"median": 0.229406},
                "intersection_counts": {"last": 269},
            },
            "pip": {
                "query_ms_reported": {"median": 0.185776},
                "intersection_counts": {"last": None},
            },
        }
        rtdl = {
            "lsi": {
                "prepared_query_ms": {"median": 1.537322998046875},
                "counts": {"last": 269},
            },
            "pip": {
                "prepared_query_ms": {"median": 1.268438994884491},
                "counts": {"last": 1430},
            },
        }

        rows = MODULE.build_comparison_rows(rayjoin, rtdl)

        lsi = next(row for row in rows if row["workload"] == "lsi")
        pip = next(row for row in rows if row["workload"] == "pip")
        self.assertEqual(lsi["count_contract_status"], "matching_visible_lsi_count")
        self.assertGreater(lsi["rtdl_over_rayjoin_query_ratio"], 6.7)
        self.assertLess(lsi["rtdl_over_rayjoin_query_ratio"], 6.8)
        self.assertEqual(pip["count_contract_status"], "rayjoin_pip_count_not_visible")
        self.assertIsNone(pip["rayjoin_visible_count"])
        self.assertFalse(pip["rayjoin_positive_assignment_count_available"])

    def test_runner_contains_claim_boundary_and_no_release_authorization(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "public_speedup_claim_authorized",
            "rayjoin_paper_reproduction_claim_authorized",
            "rtdl_beats_rayjoin_claim_authorized",
            "true_zero_copy_claim_authorized",
            "RayJoin query_exec PIP still does not expose positive assignment count",
            "does not divide it by repeat",
        ):
            self.assertIn(phrase, text)
        self.assertTrue(all(value is False for value in MODULE.CLAIM_BOUNDARY.values()))


if __name__ == "__main__":
    unittest.main()
