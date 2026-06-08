import unittest

import rtdsl as rt


class Goal3980CurrentScaleHotPathMetricContractTest(unittest.TestCase):
    def test_every_scale_row_declares_wrapper_elapsed_is_not_hot_path_metric(self) -> None:
        rows = rt.current_benchmark_scale_profiles()
        self.assertEqual(len(rows), 10)
        for row in rows:
            with self.subTest(row=row["row_id"]):
                self.assertEqual(
                    row["timing_metric_scope"],
                    "wrapper_elapsed_sec_is_pod_budget_not_hot_path_metric",
                )
                self.assertTrue(row["representative_hot_path_metric"])
                self.assertIsNone(row["hot_path_duration_target_sec"])
                self.assertTrue(row["scale_calibration_status"])

    def test_goal3979_short_rows_are_marked_as_repeat_calibration_rejected(self) -> None:
        rows = {row["row_id"]: row for row in rt.current_benchmark_scale_profiles()}
        self.assertEqual(
            rows["robot_collision_optix_scale_default_1024_no_probe_reference"][
                "scale_calibration_status"
            ],
            "short_row_repeat_calibration_rejected_goal3979",
        )
        self.assertEqual(
            rows["robot_collision_optix_scale_default_1024_no_probe_reference"][
                "representative_hot_path_metric"
            ],
            "benchmark_timing_sec.tail_phase_traversal_sec",
        )
        self.assertEqual(
            rows["raydb_style_optix_count_scale_default_262k"]["scale_calibration_status"],
            "short_row_repeat_calibration_rejected_goal3979",
        )
        self.assertEqual(
            rows["raydb_style_optix_count_scale_default_262k"]["representative_hot_path_metric"],
            "metadata.timings.native_call_wall",
        )

    def test_summary_and_validator_expose_contract(self) -> None:
        summary = rt.summarize_current_benchmark_scale_profiles()
        self.assertEqual(
            summary["timing_metric_scope"],
            "wrapper_elapsed_sec_is_pod_budget_not_hot_path_metric",
        )
        self.assertIn(
            "short_row_repeat_calibration_rejected_goal3979",
            summary["scale_calibration_statuses"],
        )
        validation = rt.validate_current_benchmark_scale_profiles()
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())

    def test_validator_rejects_wrapper_hot_path_overclaim(self) -> None:
        rows = [dict(row) for row in rt.current_benchmark_scale_profiles()]
        rows[0]["timing_metric_scope"] = "wrapper_elapsed_sec_is_hot_path_metric"
        validation = rt.validate_current_benchmark_scale_profiles(tuple(rows))
        self.assertEqual(validation["status"], "reject")
        self.assertTrue(
            any("timing_metric_scope" in error for error in validation["errors"]),
            validation["errors"],
        )


if __name__ == "__main__":
    unittest.main()
