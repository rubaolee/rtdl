from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3244_rayjoin_same_slice_repeated_count_runner_2026-06-03.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3244_rayjoin_same_slice_repeated_count_pod_2026-06-03.json"
STDOUT = ROOT / "docs" / "reports" / "goal3244_rayjoin_same_slice_repeated_count_pod_2026-06-03.stdout"


class Goal3244RayJoinSameSliceRepeatedCountArtifactTest(unittest.TestCase):
    def test_report_records_repeated_medians_and_phase_diagnosis(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Repeated RTDL/RayJoin Same-Slice Count Runner",
            "0.233793 ms",
            "1.449205 ms",
            "6.20x",
            "0.193946 ms",
            "1.116930 ms",
            "5.76x",
            "host exact-refine authority path",
            "count-only contract",
            "avoid writing/downloading candidate rows",
            "does not authorize release",
            "paper-reproduction claims",
        ):
            self.assertIn(phrase, text)

    def test_artifact_preserves_counts_and_claim_boundaries(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["schema"], "rtdl.goal3244.rayjoin_same_slice_repeated_count.v1")
        self.assertEqual(data["status"], "pass_with_optimization_gap")
        self.assertTrue(all(value is False for value in data["claim_boundary"].values()))

        rows = {row["workload"]: row for row in data["comparisons"]}
        self.assertEqual(rows["lsi"]["count_contract_status"], "matching_visible_lsi_count")
        self.assertEqual(rows["lsi"]["rayjoin_visible_count"], 269)
        self.assertEqual(rows["lsi"]["rtdl_count"], 269)
        self.assertGreater(rows["lsi"]["rtdl_over_rayjoin_query_ratio"], 6.0)
        self.assertLess(rows["lsi"]["rtdl_over_rayjoin_query_ratio"], 6.4)

        self.assertEqual(rows["pip"]["count_contract_status"], "rayjoin_pip_count_not_visible")
        self.assertIsNone(rows["pip"]["rayjoin_visible_count"])
        self.assertFalse(rows["pip"]["rayjoin_positive_assignment_count_available"])
        self.assertEqual(rows["pip"]["rtdl_count"], 1430)

    def test_stdout_contains_progress_markers(self) -> None:
        text = STDOUT.read_text(encoding="utf-8")

        for phrase in (
            "[goal3244] RayJoin lsi process 1/5",
            "[goal3244] RayJoin pip process 5/5",
            "[goal3244] RTDL lsi repeat 7/7",
            "[goal3244] RTDL pip repeat 7/7",
        ):
            self.assertIn(phrase, text)

    def test_native_phase_samples_explain_distinct_lsi_and_pip_bottlenecks(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        lsi_samples = data["rtdl"]["lsi"]["native_phase_samples"]
        pip_samples = data["rtdl"]["pip"]["native_phase_samples"]
        self.assertTrue(all(sample["emitted_count"] == 269 for sample in lsi_samples))
        self.assertTrue(all(sample["emitted_count"] == 1430 for sample in pip_samples))
        self.assertTrue(all(sample["exact_refine"] > sample["candidate_write_pass"] for sample in lsi_samples))
        self.assertTrue(all(sample["candidate_write_pass"] > sample["exact_refine"] for sample in pip_samples))


if __name__ == "__main__":
    unittest.main()
