from __future__ import annotations

import json
import tempfile
from pathlib import Path
import unittest

from scripts import goal1615_v1_6_4_collect_k_reduced_copy_benchmark as goal1615


class Goal1615CollectKReducedCopyBenchmarkTest(unittest.TestCase):
    def test_fake_native_package_accepts_multiscale_materialization_delta(self) -> None:
        payload = goal1615.validate_package(
            goal1615.run_package(
                scales=(
                    goal1615.BenchmarkScale(unique_rows=8, repeats=2, iterations=3),
                    goal1615.BenchmarkScale(unique_rows=16, repeats=2, iterations=4),
                )
            )
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["status"], "accepted_reduced_copy_benchmark_evidence")
        self.assertEqual(len(payload["records"]), 2)
        for record in payload["records"]:
            comparison = record["path_comparison"]
            self.assertEqual(comparison["baseline_input_materialization_count"], record["iterations"])
            self.assertEqual(comparison["prepared_input_materialization_count"], 1)
            self.assertEqual(comparison["input_materialization_count_delta"], record["iterations"] - 1)
            self.assertEqual(comparison["accepted_metric"], "input_materialization_count_delta")
            self.assertTrue(comparison["prepared_host_output_buffer_reused"])
            self.assertTrue(comparison["stable_typed_input_buffer_address"])
            self.assertTrue(comparison["timing_recorded_for_diagnostics_only"])

    def test_record_validator_rejects_timing_or_materialization_overclaim(self) -> None:
        payload = goal1615.run_package(scales=(goal1615.BenchmarkScale(8, 2, 3),))
        record = dict(payload["records"][0])
        record["phase_times_sec"] = dict(record["phase_times_sec"])
        record["copy_counts"] = dict(record["copy_counts"])
        record["claim_flags"] = dict(record["claim_flags"])
        record["path_comparison"] = dict(record["path_comparison"])

        record["path_comparison"]["timing_recorded_for_diagnostics_only"] = False
        with self.assertRaisesRegex(ValueError, "diagnostic only"):
            goal1615.validate_record(record, manifest=payload["manifest"])

        record["path_comparison"]["timing_recorded_for_diagnostics_only"] = True
        record["path_comparison"]["prepared_input_materialization_count"] = 2
        with self.assertRaisesRegex(ValueError, "materialize once"):
            goal1615.validate_record(record, manifest=payload["manifest"])

    def test_package_validator_keeps_claim_flags_false(self) -> None:
        payload = goal1615.validate_package(goal1615.run_package())

        for flag, value in payload["claim_flags"].items():
            with self.subTest(flag=flag):
                self.assertIs(value, False)
        self.assertIn("copy/materialization-count reduction", payload["claim_boundary"])
        self.assertIn("Timing is diagnostic only", payload["claim_boundary"])
        self.assertIn("true zero-copy wording", payload["claim_boundary"])

    def test_artifact_generation_records_accepted_metric_without_speedup_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            json_path = Path(tmp) / "reduced_copy.json"
            md_path = Path(tmp) / "reduced_copy.md"
            rc = goal1615.main(
                [
                    "--scale",
                    "8:2:3",
                    "--json-out",
                    str(json_path),
                    "--md-out",
                    str(md_path),
                ]
            )

            self.assertEqual(rc, 0)
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            markdown = md_path.read_text(encoding="utf-8")

        self.assertTrue(payload["accepted"])
        self.assertIn("input_materialization_count_delta", markdown)
        self.assertIn("Timing is diagnostic only", markdown)
        self.assertIn("does not authorize public speedup wording", markdown)
        self.assertIn("stable COLLECT_K_BOUNDED promotion", markdown)

    def test_external_reviews_and_consensus_exist_for_materialization_metric_only(self) -> None:
        root = Path(__file__).resolve().parents[1]
        review_paths = (
            root
            / "docs/reviews/goal1615_v1_6_4_collect_k_reduced_copy_benchmark_claude_review_2026-05-09.md",
            root
            / "docs/reviews/goal1615_v1_6_4_collect_k_reduced_copy_benchmark_gemini_review_2026-05-09.md",
            root
            / "docs/reviews/goal1615_v1_6_4_collect_k_reduced_copy_benchmark_3ai_consensus_2026-05-09.md",
        )

        for path in review_paths:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("ACCEPTED", text)
                self.assertIn("COLLECT_K_BOUNDED", text)
        consensus = review_paths[-1].read_text(encoding="utf-8")
        self.assertIn("input_materialization_count_delta", consensus)
        self.assertIn("Timing remains diagnostic only", consensus)
        self.assertIn("does not authorize public\nspeedup wording", consensus)


if __name__ == "__main__":
    unittest.main()
