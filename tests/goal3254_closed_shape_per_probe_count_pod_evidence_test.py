from __future__ import annotations

import json
import statistics
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3254_closed_shape_per_probe_count_accumulation_pod_evidence_2026-06-03.md"
DIRECT = ROOT / "docs" / "reports" / "goal3254_closed_shape_per_probe_count_probe_pod_2026-06-03.json"
DIRECT_STDOUT = ROOT / "docs" / "reports" / "goal3254_closed_shape_per_probe_count_probe_pod_2026-06-03.stdout"
COMPARISON = ROOT / "docs" / "reports" / "goal3254_rayjoin_per_probe_count_pod_2026-06-03.json"
COMPARISON_STDOUT = ROOT / "docs" / "reports" / "goal3254_rayjoin_per_probe_count_pod_2026-06-03.stdout"
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"


class Goal3254ClosedShapePerProbeCountPodEvidenceTest(unittest.TestCase):
    def test_report_records_modest_diagnostic_result(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Closed-Shape Per-Probe Count Accumulation Pod Evidence",
            "0.782767 ms",
            "0.794193 ms",
            "4.11x",
            "only slightly faster",
            "does not materially close the",
            "RayJoin PIP gap",
            "does not authorize release",
        ):
            self.assertIn(phrase, text)

    def test_kernel_uses_payload_accumulation_for_count_only_path(self) -> None:
        text = CORE.read_text(encoding="utf-8")

        self.assertIn("params.output == nullptr && params.output_capacity == 0u && p2 != 0u", text)
        self.assertIn("atomicAdd(params.output_count, p2)", text)
        self.assertIn("optixSetPayload_2(optixGetPayload_2() + 1u)", text)

    def test_direct_probe_artifact_is_clean_and_matches_exact(self) -> None:
        data = json.loads(DIRECT.read_text(encoding="utf-8"))

        self.assertEqual(data["repo_state"]["commit"], "96ec7f141691cee1a3988eee2bcaa8b7be911f82")
        self.assertEqual(data["repo_state"]["source_dirty"], [])
        self.assertTrue(all(value is False for value in data["claim_boundary"].values()))
        self.assertTrue(data["comparison"]["all_counts_match"])
        self.assertFalse(data["comparison"]["device_filtered_is_exact_authority"])
        self.assertEqual(data["exact_count"]["counts"], [1430] * 9)
        self.assertEqual(data["device_filtered_count"]["counts"], [1430] * 9)
        self.assertAlmostEqual(data["exact_count"]["median_sec"] * 1000.0, 0.8835475891828537)
        self.assertAlmostEqual(data["device_filtered_count"]["median_sec"] * 1000.0, 0.7827673107385635)
        self.assertGreater(data["comparison"]["speedup_over_exact_count"], 1.1)
        self.assertLess(data["comparison"]["speedup_over_exact_count"], 1.2)

    def test_comparison_artifact_keeps_gap_and_boundary_honest(self) -> None:
        data = json.loads(COMPARISON.read_text(encoding="utf-8"))

        self.assertEqual(data["rtdl_commit"], "96ec7f141691cee1a3988eee2bcaa8b7be911f82")
        self.assertEqual(data["source_dirty"], [])
        self.assertTrue(all(value is False for value in data["claim_boundary"].values()))

        rows = {row["workload"]: row for row in data["comparisons"]}
        self.assertEqual(rows["lsi"]["count_contract_status"], "matching_visible_lsi_count")
        self.assertEqual(rows["lsi"]["rtdl_count"], 269)
        self.assertGreater(rows["lsi"]["rtdl_over_rayjoin_query_ratio"], 1.5)

        self.assertEqual(rows["pip"]["count_contract_status"], "rayjoin_pip_count_not_visible")
        self.assertEqual(rows["pip"]["rtdl_count"], 1430)
        self.assertGreater(rows["pip"]["rtdl_over_rayjoin_query_ratio"], 4.0)
        self.assertAlmostEqual(rows["pip"]["rtdl_prepared_query_ms_median"], 0.7941927760839462)

        pip = data["rtdl"]["pip"]
        self.assertEqual(pip["count_mode"], "device_filtered_validated")
        self.assertAlmostEqual(pip["validation_exact_query_ms"]["median"], 0.9333286434412003)
        self.assertGreater(pip["validation_exact_query_ms"]["median"], pip["prepared_query_ms"]["median"])
        self.assertTrue(all(sample["candidate_write_pass"] == 0.0 for sample in pip["native_phase_samples"]))
        self.assertTrue(all(sample["candidate_download"] == 0.0 for sample in pip["native_phase_samples"]))
        self.assertTrue(all(sample["exact_refine"] == 0.0 for sample in pip["native_phase_samples"]))
        self.assertGreater(statistics.median(sample["candidate_count_pass"] for sample in pip["native_phase_samples"]), 0.0007)

    def test_stdout_files_record_progress(self) -> None:
        direct = DIRECT_STDOUT.read_text(encoding="utf-8")
        comparison = COMPARISON_STDOUT.read_text(encoding="utf-8")

        self.assertIn("[goal3252] repeat 9/9", direct)
        self.assertIn("device_filtered=1430", direct)
        self.assertIn("[goal3244] RayJoin lsi process 1/5", comparison)
        self.assertIn("[goal3244] RTDL pip repeat 7/7", comparison)
        self.assertIn('"source_dirty": []', comparison)


if __name__ == "__main__":
    unittest.main()
