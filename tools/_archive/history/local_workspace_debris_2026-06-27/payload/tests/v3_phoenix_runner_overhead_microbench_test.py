import unittest

from scripts import v3_phoenix_runner_overhead_microbench as microbench


class V3PhoenixRunnerOverheadMicrobenchTest(unittest.TestCase):
    def test_microbench_reports_generic_non_release_runner_overhead(self):
        payload = microbench.run_microbench(iterations=3, runner_iterations=2)

        self.assertEqual(payload["schema"], microbench.SCHEMA)
        self.assertEqual(payload["status"], "local_microbench_not_release_evidence")
        self.assertIn("stable_id_reads", payload["timing_sec"])
        self.assertIn("phase_to_dict", payload["timing_sec"])
        self.assertIn("report_to_dict", payload["timing_sec"])
        self.assertIn("noop_runner_calls", payload["timing_sec"])
        self.assertIn("heavy_full_runner_calls", payload["timing_sec"])
        self.assertIn("heavy_finalize_once_runner_calls", payload["timing_sec"])
        self.assertGreaterEqual(payload["timing_sec"]["stable_id_reads"], 0.0)
        self.assertGreaterEqual(payload["timing_sec"]["phase_to_dict"], 0.0)
        self.assertGreaterEqual(payload["timing_sec"]["report_to_dict"], 0.0)
        self.assertGreaterEqual(payload["timing_sec"]["noop_runner_calls"], 0.0)
        self.assertGreaterEqual(payload["timing_sec"]["heavy_full_runner_calls"], 0.0)
        self.assertGreaterEqual(payload["timing_sec"]["heavy_finalize_once_runner_calls"], 0.0)
        self.assertIn("heavy_finalize_once_speedup_vs_full", payload["comparison"])
        self.assertIn("heavy_finalize_once_saved_fraction", payload["comparison"])
        self.assertEqual(
            payload["last_runner_metadata"]["productized_execution_path"],
            "prepared_execution_session_runner",
        )
        self.assertTrue(payload["last_runner_metadata"]["runtime_executed"])
        self.assertEqual(
            payload["last_runner_metadata"]["prepared_execution_report_validation"]["status"],
            "accept",
        )
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["v4_embedding_or_external_zero_copy_authorized"])
        self.assertFalse(payload["full_all_app_rerun_authorized_by_this_packet"])
        self.assertFalse(
            payload["last_runner_metadata"]["app_specific_native_engine_logic_allowed"]
        )
        self.assertTrue(
            payload["finalized_runner_metadata"]["measured_run_prepared_override_used"]
        )
        self.assertTrue(payload["finalized_runner_metadata"]["measured_output_finalized_once"])
        self.assertTrue(
            payload["finalized_runner_metadata"]["per_repeat_output_finalization_avoided"]
        )
        self.assertGreaterEqual(payload["finalized_runner_metadata"]["output_finalize_sec"], 0.0)
        self.assertFalse(payload["finalized_runner_metadata"]["release_authorized"])
        self.assertFalse(payload["finalized_runner_metadata"]["public_speedup_claim_authorized"])

    def test_microbench_rejects_invalid_iteration_counts(self):
        with self.assertRaisesRegex(ValueError, "iterations must be positive"):
            microbench.run_microbench(iterations=0, runner_iterations=1)
        with self.assertRaisesRegex(ValueError, "runner_iterations must be positive"):
            microbench.run_microbench(iterations=1, runner_iterations=0)


if __name__ == "__main__":
    unittest.main()
