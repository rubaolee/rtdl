from __future__ import annotations

import json
import statistics
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3248_rayjoin_current_best_after_lsi_lazy_lookup_and_pip_extent_2026-06-03.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3248_rayjoin_current_best_extent025_pod_2026-06-03.json"
BASELINE = ROOT / "docs" / "reports" / "goal3244_rayjoin_same_slice_repeated_count_pod_2026-06-03.json"
STDOUT = ROOT / "docs" / "reports" / "goal3248_rayjoin_current_best_extent025_pod_2026-06-03.stdout"
LOG_DIR = ROOT / "docs" / "reports" / "goal3248_rayjoin_current_best_extent025_pod"


def _row(data: dict, workload: str) -> dict:
    return {row["workload"]: row for row in data["comparisons"]}[workload]


def _phase_median_ms(data: dict, workload: str, field: str) -> float:
    values = [
        float(sample[field]) * 1000.0
        for sample in data["rtdl"][workload]["native_phase_samples"]
        if sample and field in sample
    ]
    return float(statistics.median(values))


class Goal3248RayJoinCurrentBestExtent025ArtifactTest(unittest.TestCase):
    def test_report_records_current_best_table_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "RayJoin Current Best After LSI Lazy Lookup And PIP Extent Tuning",
            "RTDL_OPTIX_POINT_PRIMITIVE_QUERY_HALF_EXTENT=0.25",
            "0.458829 ms",
            "1.97x",
            "0.934755 ms",
            "4.82x",
            "3.16x",
            "1.19x",
            "device-resident grouped",
            "does not authorize release",
            "paper-reproduction claims",
        ):
            self.assertIn(phrase, text)

    def test_artifact_is_clean_and_claim_bounded(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["schema"], "rtdl.goal3244.rayjoin_same_slice_repeated_count.v1")
        self.assertEqual(data["rtdl_commit"], "eb09b9b21a7e6223fd96769326331216fe609035")
        self.assertEqual(data["source_dirty"], [])
        self.assertTrue(all(value is False for value in data["claim_boundary"].values()))

    def test_current_best_improves_over_goal3244_baseline_but_not_rayjoin(self) -> None:
        current = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))

        current_lsi = _row(current, "lsi")
        current_pip = _row(current, "pip")
        baseline_lsi = _row(baseline, "lsi")
        baseline_pip = _row(baseline, "pip")

        self.assertEqual(current_lsi["rtdl_count"], 269)
        self.assertEqual(current_lsi["rayjoin_visible_count"], 269)
        self.assertEqual(current_pip["rtdl_count"], 1430)
        self.assertIsNone(current_pip["rayjoin_visible_count"])

        self.assertLess(
            current_lsi["rtdl_prepared_query_ms_median"],
            baseline_lsi["rtdl_prepared_query_ms_median"] / 3.0,
        )
        self.assertLess(
            current_pip["rtdl_prepared_query_ms_median"],
            baseline_pip["rtdl_prepared_query_ms_median"],
        )
        self.assertGreater(current_lsi["rtdl_over_rayjoin_query_ratio"], 1.0)
        self.assertGreater(current_pip["rtdl_over_rayjoin_query_ratio"], 4.0)

    def test_pip_bottleneck_remains_candidate_write(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertGreater(_phase_median_ms(data, "pip", "candidate_write_pass"), 0.7)
        self.assertLess(_phase_median_ms(data, "pip", "exact_refine"), 0.1)
        self.assertLess(_phase_median_ms(data, "pip", "candidate_download"), 0.02)

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
