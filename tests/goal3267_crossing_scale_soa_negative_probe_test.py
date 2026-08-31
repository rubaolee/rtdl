from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3267_crossing_scale_soa_negative_probe_2026-06-03.md"
DEFAULT = ROOT / "docs" / "reports" / "goal3267_default_compiletime_same_slice_pod_2026-06-03.json"
SOA = ROOT / "docs" / "reports" / "goal3267_crossing_scale_soa_compiletime_same_slice_pod_2026-06-03.json"
REVERTED = ROOT / "docs" / "reports" / "goal3267_reverted_control_same_slice_pod_2026-06-03.json"
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal3267CrossingScaleSoANegativeProbeTest(unittest.TestCase):
    def _load(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def _pip_row(self, data: dict) -> dict:
        return {row["workload"]: row for row in data["comparisons"]}["pip"]

    def _candidate_median_ms(self, data: dict) -> float:
        samples = [row["candidate_count_pass"] for row in data["rtdl"]["pip"]["native_phase_samples"]]
        return sorted(samples)[len(samples) // 2] * 1000.0

    def test_artifacts_record_soa_improves_same_commit_but_remains_slower_than_best(self) -> None:
        default = self._load(DEFAULT)
        soa = self._load(SOA)
        reverted = self._load(REVERTED)
        default_pip = self._pip_row(default)
        soa_pip = self._pip_row(soa)
        reverted_pip = self._pip_row(reverted)

        self.assertTrue(default["rtdl_commit"].startswith("914b607c"))
        self.assertTrue(soa["rtdl_commit"].startswith("914b607c"))
        self.assertTrue(reverted["rtdl_commit"].startswith("fced1fad"))
        self.assertEqual(default["source_dirty"], [])
        self.assertEqual(soa["source_dirty"], [])
        self.assertEqual(reverted["source_dirty"], [])
        self.assertEqual(default_pip["rtdl_count"], 1430)
        self.assertEqual(soa_pip["rtdl_count"], 1430)
        self.assertEqual(reverted_pip["rtdl_count"], 1430)
        self.assertLess(soa_pip["rtdl_prepared_query_ms_median"], default_pip["rtdl_prepared_query_ms_median"])
        self.assertLess(self._candidate_median_ms(soa), self._candidate_median_ms(default))
        self.assertGreater(soa_pip["rtdl_prepared_query_ms_median"], 0.337990)
        self.assertLess(reverted_pip["rtdl_prepared_query_ms_median"], soa_pip["rtdl_prepared_query_ms_median"])
        self.assertLess(self._candidate_median_ms(reverted), self._candidate_median_ms(soa))
        self.assertTrue(all(value is False for value in soa["claim_boundary"].values()))

    def test_live_source_no_longer_keeps_the_failed_gate(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")

        self.assertNotIn("edge_crossing_scale", core)
        self.assertNotIn("RTDL_OPTIX_POINT_PRIMITIVE_USE_CROSSING_SCALE_LAYOUT", workloads)
        self.assertNotIn("use_prepared_closed_shape_crossing_scale_layout", workloads)

    def test_report_records_revert_and_next_direction(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Crossing-Scale SoA Negative Probe",
            "0.415020",
            "0.372346",
            "Goal3264 count-only payload: `0.322377 ms`",
            "0.339672",
            "live code was reverted",
            "shape-local edge blocking",
            "warp-cooperative evaluation",
            "does not authorize release",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
