from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3260_rayjoin_runner_explicit_query_axis_pod_evidence_2026-06-03.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3260_rayjoin_explicit_z_point_same_slice_pod_2026-06-03.json"
CLAUDE_REVIEW = ROOT / "docs" / "reviews" / "goal3259_claude_review_goal3256_3258_z_point_predicate_tuning_chain_2026-06-03.md"


class Goal3260RayJoinExplicitQueryAxisPodEvidenceTest(unittest.TestCase):
    def _artifact(self) -> dict:
        return json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def _rows(self) -> dict[str, dict]:
        return {row["workload"]: row for row in self._artifact()["comparisons"]}

    def test_report_records_runner_provenance_gap_closure(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "RayJoin Runner Explicit Query-Axis Evidence",
            "--rtdl-pip-query-axis",
            "query_axis: \"z_point\"",
            "1.675x",
            "does **not** authorize release",
            "prepared-edge layout",
        ):
            self.assertIn(phrase, text)

    def test_artifact_is_source_clean_and_claim_bounded(self) -> None:
        data = self._artifact()

        self.assertEqual(data["schema"], "rtdl.goal3244.rayjoin_same_slice_repeated_count.v1")
        self.assertTrue(data["rtdl_commit"].startswith("0a1aaeb8"))
        self.assertEqual(data["source_dirty"], [])
        self.assertEqual(data["rtdl"]["pip"]["query_axis"], "z_point")
        self.assertIn("rtdl_pip_query_axis", data["interpretation"])
        self.assertTrue(all(value is False for value in data["claim_boundary"].values()))

    def test_pip_row_records_explicit_z_point_timing_and_count(self) -> None:
        pip = self._rows()["pip"]

        self.assertEqual(pip["count_contract_status"], "rayjoin_pip_count_not_visible")
        self.assertEqual(pip["rtdl_count"], 1430)
        self.assertAlmostEqual(pip["rayjoin_query_ms_reported_median"], 0.195058)
        self.assertAlmostEqual(pip["rtdl_prepared_query_ms_median"], 0.3267992287874222)
        self.assertAlmostEqual(pip["rtdl_over_rayjoin_query_ratio"], 1.675395158298671)
        self.assertGreater(pip["rtdl_over_rayjoin_query_ratio"], 1.0)
        self.assertLess(pip["rtdl_over_rayjoin_query_ratio"], 1.8)

    def test_native_pip_phase_is_device_filtered_count_without_host_candidate_materialization(self) -> None:
        phases = self._artifact()["rtdl"]["pip"]["native_phase_samples"]

        self.assertEqual(len(phases), 9)
        self.assertTrue(all(sample["mode"] == "device_filtered_count" for sample in phases))
        self.assertTrue(all(sample["raw_candidate_count"] == 1430 for sample in phases))
        self.assertTrue(all(sample["emitted_count"] == 1430 for sample in phases))
        self.assertTrue(all(sample["candidate_write_pass"] == 0.0 for sample in phases))
        self.assertTrue(all(sample["candidate_download"] == 0.0 for sample in phases))
        self.assertTrue(all(sample["exact_refine"] == 0.0 for sample in phases))

    def test_claude_review_accepts_tuning_chain_with_boundary(self) -> None:
        text = CLAUDE_REVIEW.read_text(encoding="utf-8")

        for phrase in (
            "Goal3259: Claude Review",
            "Verdict:** `accept-with-boundary`",
            "z_point",
            "1.69x slower versus RayJoin",
            "No release, public speedup",
            "\"RTDL beats RayJoin\" claims are",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
