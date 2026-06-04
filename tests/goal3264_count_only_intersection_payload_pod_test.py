from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3264_count_only_intersection_payload_probe_2026-06-03.md"
BASELINE = ROOT / "docs" / "reports" / "goal3263_prepared_edge_layout_gated_default_pod_2026-06-03.json"
ARTIFACT = ROOT / "docs" / "reports" / "goal3264_count_only_intersection_payload_pod_2026-06-03.json"
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"


class Goal3264CountOnlyIntersectionPayloadPodTest(unittest.TestCase):
    def _load(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def _pip_row(self, data: dict) -> dict:
        return {row["workload"]: row for row in data["comparisons"]}["pip"]

    def test_report_records_small_positive_probe_without_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Count-Only Intersection Payload Probe",
            "small positive optimization",
            "0.322377",
            "1.662x",
            "does not authorize release",
            "not the any-hit shader dispatch itself",
        ):
            self.assertIn(phrase, text)

    def test_artifact_is_clean_count_preserving_and_claim_bounded(self) -> None:
        data = self._load(ARTIFACT)
        pip = self._pip_row(data)

        self.assertTrue(data["rtdl_commit"].startswith("4cfea7d7"))
        self.assertEqual(data["source_dirty"], [])
        self.assertEqual(data["rtdl"]["pip"]["query_axis"], "z_point")
        self.assertEqual(pip["rtdl_count"], 1430)
        self.assertEqual(pip["count_contract_status"], "rayjoin_pip_count_not_visible")
        self.assertTrue(all(value is False for value in data["claim_boundary"].values()))

    def test_count_payload_probe_is_slightly_faster_than_gated_default(self) -> None:
        baseline = self._pip_row(self._load(BASELINE))
        current = self._pip_row(self._load(ARTIFACT))

        self.assertAlmostEqual(baseline["rtdl_prepared_query_ms_median"], 0.3241784870624542)
        self.assertAlmostEqual(current["rtdl_prepared_query_ms_median"], 0.3223773092031479)
        self.assertLess(
            current["rtdl_prepared_query_ms_median"],
            baseline["rtdl_prepared_query_ms_median"],
        )
        self.assertLess(current["rtdl_over_rayjoin_query_ratio"], baseline["rtdl_over_rayjoin_query_ratio"])

    def test_intersection_short_circuit_precedes_report_intersection(self) -> None:
        text = CORE.read_text(encoding="utf-8")
        start = text.index('extern "C" __global__ void __intersection__pip_isect()')
        end = text.index('extern "C" __global__ void __anyhit__pip_anyhit()', start)
        body = text[start:end]

        self.assertIn("if (params.output == nullptr && params.output_capacity == 0u)", body)
        self.assertIn("optixSetPayload_2(optixGetPayload_2() + 1u);", body)
        self.assertLess(
            body.index("optixSetPayload_2(optixGetPayload_2() + 1u);"),
            body.index("optixReportIntersection(0.5f, 0u);"),
        )


if __name__ == "__main__":
    unittest.main()
