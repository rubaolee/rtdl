from __future__ import annotations

import json
import statistics
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3263_prepared_edge_layout_negative_probe_and_gate_2026-06-03.md"
NEGATIVE = ROOT / "docs" / "reports" / "goal3262_prepared_edge_layout_negative_probe_pod_2026-06-03.json"
GATED = ROOT / "docs" / "reports" / "goal3263_prepared_edge_layout_gated_default_pod_2026-06-03.json"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal3263PreparedEdgeNegativeProbeGateTest(unittest.TestCase):
    def _load(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def _pip_row(self, data: dict) -> dict:
        return {row["workload"]: row for row in data["comparisons"]}["pip"]

    def _candidate_count_median_ms(self, data: dict) -> float:
        samples = data["rtdl"]["pip"]["native_phase_samples"]
        return statistics.median(sample["candidate_count_pass"] for sample in samples) * 1000.0

    def test_report_records_negative_probe_and_gate(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Prepared Edge Layout Negative Probe and Gate",
            "gated off by default",
            "RTDL_OPTIX_POINT_PRIMITIVE_USE_PREPARED_EDGE_LAYOUT",
            "0.381375",
            "0.324178",
            "does not authorize release",
            "negative engineering result",
        ):
            self.assertIn(phrase, text)

    def test_artifacts_are_clean_count_preserving_and_claim_bounded(self) -> None:
        for path, prefix in ((NEGATIVE, "831df1b1"), (GATED, "2c77ff28")):
            data = self._load(path)
            pip = self._pip_row(data)

            self.assertTrue(data["rtdl_commit"].startswith(prefix))
            self.assertEqual(data["source_dirty"], [])
            self.assertEqual(data["rtdl"]["pip"]["query_axis"], "z_point")
            self.assertEqual(pip["rtdl_count"], 1430)
            self.assertEqual(pip["count_contract_status"], "rayjoin_pip_count_not_visible")
            self.assertTrue(all(value is False for value in data["claim_boundary"].values()))

    def test_prepared_edge_layout_is_slower_than_gated_default_on_this_probe(self) -> None:
        negative = self._load(NEGATIVE)
        gated = self._load(GATED)
        negative_pip = self._pip_row(negative)
        gated_pip = self._pip_row(gated)

        self.assertAlmostEqual(negative_pip["rtdl_prepared_query_ms_median"], 0.3813747316598892)
        self.assertAlmostEqual(gated_pip["rtdl_prepared_query_ms_median"], 0.3241784870624542)
        self.assertGreater(
            negative_pip["rtdl_prepared_query_ms_median"],
            gated_pip["rtdl_prepared_query_ms_median"] * 1.15,
        )
        self.assertGreater(self._candidate_count_median_ms(negative), self._candidate_count_median_ms(gated))

    def test_code_keeps_prepared_edge_layout_opt_in_not_default(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("static bool use_prepared_closed_shape_edge_layout()", text)
        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_USE_PREPARED_EDGE_LAYOUT", text)
        self.assertEqual(text.count("lp.prepared_edges = nullptr;"), 1)
        self.assertEqual(
            text.count(
                "reinterpret_cast<const GpuPreparedClosedShapeEdge2D*>(prepared->d_right_edges.ptr)\n"
                "        : nullptr;"
            ),
            3,
        )


if __name__ == "__main__":
    unittest.main()
