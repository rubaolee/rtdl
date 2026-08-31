from __future__ import annotations

import json
import statistics
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3245_segment_pair_exact_refine_lazy_lookup_pod_2026-06-03.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3245_segment_pair_lazy_lookup_pod_2026-06-03.json"
BASELINE = ROOT / "docs" / "reports" / "goal3244_rayjoin_same_slice_repeated_count_pod_2026-06-03.json"
STDOUT = ROOT / "docs" / "reports" / "goal3245_segment_pair_lazy_lookup_pod_2026-06-03.stdout"
LOG_DIR = ROOT / "docs" / "reports" / "goal3245_segment_pair_lazy_lookup_pod"


def _row(data: dict, workload: str) -> dict:
    return {row["workload"]: row for row in data["comparisons"]}[workload]


def _phase_median_ms(data: dict, workload: str, field: str) -> float:
    values = [
        float(sample[field]) * 1000.0
        for sample in data["rtdl"][workload]["native_phase_samples"]
        if sample and field in sample
    ]
    return float(statistics.median(values))


class Goal3245SegmentPairLazyLookupPodArtifactTest(unittest.TestCase):
    def test_report_records_lsi_win_and_pip_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Segment-Pair Exact-Refine Lazy Lookup Pod Evidence",
            "0.232999 ms",
            "0.401776 ms",
            "1.72x",
            "1.449205 ms",
            "3.61x",
            "0.193596 ms",
            "1.147646 ms",
            "5.93x",
            "about `0.041 ms`",
            "PIP was not a target",
            "count-only closed-shape membership path",
            "does not authorize release",
            "paper-reproduction claims",
        ):
            self.assertIn(phrase, text)

    def test_artifact_is_clean_and_preserves_claim_boundaries(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["schema"], "rtdl.goal3244.rayjoin_same_slice_repeated_count.v1")
        self.assertEqual(data["status"], "pass_with_optimization_gap")
        self.assertEqual(data["rtdl_commit"], "92082014ce40c596669edc47c7338ecb4e4c125f")
        self.assertEqual(data["source_dirty"], [])
        self.assertTrue(all(value is False for value in data["claim_boundary"].values()))

    def test_lsi_gap_and_exact_refine_are_reduced(self) -> None:
        current = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        current_lsi = _row(current, "lsi")
        baseline_lsi = _row(baseline, "lsi")

        self.assertEqual(current_lsi["count_contract_status"], "matching_visible_lsi_count")
        self.assertEqual(current_lsi["rayjoin_visible_count"], 269)
        self.assertEqual(current_lsi["rtdl_count"], 269)
        self.assertGreater(baseline_lsi["rtdl_over_rayjoin_query_ratio"], 6.0)
        self.assertLess(current_lsi["rtdl_over_rayjoin_query_ratio"], 1.8)
        self.assertLess(
            current_lsi["rtdl_prepared_query_ms_median"],
            baseline_lsi["rtdl_prepared_query_ms_median"] / 3.0,
        )

        self.assertGreater(_phase_median_ms(baseline, "lsi", "exact_refine"), 1.0)
        self.assertLess(_phase_median_ms(current, "lsi", "exact_refine"), 0.05)

    def test_pip_remains_the_next_bottleneck(self) -> None:
        current = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        current_pip = _row(current, "pip")
        baseline_pip = _row(baseline, "pip")

        self.assertEqual(current_pip["count_contract_status"], "rayjoin_pip_count_not_visible")
        self.assertIsNone(current_pip["rayjoin_visible_count"])
        self.assertEqual(current_pip["rtdl_count"], 1430)
        self.assertGreater(current_pip["rtdl_over_rayjoin_query_ratio"], 5.0)
        self.assertGreater(
            current_pip["rtdl_prepared_query_ms_median"],
            baseline_pip["rtdl_prepared_query_ms_median"] * 0.95,
        )
        self.assertGreater(_phase_median_ms(current, "pip", "candidate_write_pass"), 0.9)
        self.assertLess(_phase_median_ms(current, "pip", "exact_refine"), 0.1)

    def test_stdout_and_logs_are_present(self) -> None:
        text = STDOUT.read_text(encoding="utf-8")
        self.assertIn("[goal3244] RayJoin lsi process 1/5", text)
        self.assertIn("[goal3244] RTDL pip repeat 7/7", text)

        logs = sorted(path.name for path in LOG_DIR.glob("*.log"))
        self.assertEqual(len(logs), 10)
        self.assertIn("rayjoin_lsi_process_1.log", logs)
        self.assertIn("rayjoin_pip_process_5.log", logs)


if __name__ == "__main__":
    unittest.main()
