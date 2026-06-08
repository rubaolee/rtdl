from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.goal3828_current_benchmark_scale_profile_runner import (
    _payload_timing_summary,
    _semantic_file_check,
)


class Goal3901ScaleRunnerPayloadTimingSummaryTest(unittest.TestCase):
    def test_payload_timing_summary_collects_generic_hot_timing_scalars(self) -> None:
        payload = {
            "elapsed_sec": 0.080,
            "wrapper_elapsed_sec": 3.7,
            "representative_hot_path_summary": {
                "metric_scope": "per_contract_hot_medians_not_wrapper_wall_time",
                "scale_runner_elapsed_sec_is_not_hot_path_metric": True,
                "lsi_scalar_count": {"rtdl_optix_hot_median_sec": 0.00009},
            },
            "metadata": {
                "benchmark_timing_breakdown": {
                    "host_observed_sec": {"column_signature_sec": 0.006},
                    "derived_sec": {"grouped_native_sec": 0.073},
                }
            },
            "cases": [
                {
                    "workload": "lsi",
                    "subprobe_wrapper_phase_timing_sec": {
                        "shared_load_case_sec": 0.12,
                        "rtdl_optix_call_sec": 0.34,
                    },
                }
            ],
        }

        summary = _payload_timing_summary(payload)

        self.assertTrue(summary["payload_json_object"])
        self.assertEqual(summary["top_level_elapsed_sec"], 0.080)
        self.assertEqual(summary["top_level_wrapper_elapsed_sec"], 3.7)
        self.assertEqual(
            summary["representative_hot_path_metric_scope"],
            "per_contract_hot_medians_not_wrapper_wall_time",
        )
        self.assertTrue(summary["scale_runner_elapsed_sec_is_not_hot_path_metric"])
        scalar_paths = {row["path"] for row in summary["timing_scalars_sample"]}
        self.assertIn("$.elapsed_sec", scalar_paths)
        self.assertIn("$.wrapper_elapsed_sec", scalar_paths)
        self.assertIn(
            "$.metadata.benchmark_timing_breakdown.host_observed_sec.column_signature_sec",
            scalar_paths,
        )
        self.assertIn(
            "$.metadata.benchmark_timing_breakdown.derived_sec.grouped_native_sec",
            scalar_paths,
        )
        self.assertIn(
            "$.cases[0].subprobe_wrapper_phase_timing_sec.shared_load_case_sec",
            scalar_paths,
        )
        self.assertIn(
            "$.cases[0].subprobe_wrapper_phase_timing_sec.rtdl_optix_call_sec",
            scalar_paths,
        )

    def test_semantic_file_check_embeds_timing_summary_for_parseable_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stdout.json"
            path.write_text(
                json.dumps(
                    {
                        "elapsed_sec": 0.5,
                        "claim_boundary": {"release_authorized": False},
                        "run_phases": {"prepared_query_sec": 0.01},
                    }
                ),
                encoding="utf-8",
            )

            result = _semantic_file_check(path)

        self.assertTrue(result["stdout_json_parseable"])
        self.assertEqual(result["claim_flag_violations"], ())
        timing = result["payload_timing_summary"]
        self.assertEqual(timing["top_level_elapsed_sec"], 0.5)
        self.assertGreaterEqual(timing["timing_scalar_count"], 2)
        scalar_paths = {row["path"] for row in timing["timing_scalars_sample"]}
        self.assertIn("$.elapsed_sec", scalar_paths)
        self.assertIn("$.run_phases.prepared_query_sec", scalar_paths)


if __name__ == "__main__":
    unittest.main()
