from __future__ import annotations

import unittest


from scripts.goal3866_rayjoin_representative_scale_profile import _case_summary


class Goal3912RayJoinRepresentativeSubprobeTimingPropagationTest(unittest.TestCase):
    def test_case_summary_carries_nested_subprobe_timing_and_loaded_route(self) -> None:
        row = {
            "workload": "lsi",
            "dataset": "left.cdb + right.cdb",
            "counts_match": True,
            "numba_cuda_jit_baseline": {
                "hot_median_sec": 0.020,
            },
            "rtdl_optix": {
                "hot_median_sec": 0.001,
                "execution_route": "prepared_optix_left_id_dense_count_loaded_case_reuse",
                "loaded_case_reuse_enabled": True,
            },
            "wrapper_phase_timing_sec": {
                "shared_load_case_sec": 0.50,
                "rtdl_optix_call_sec": 0.75,
                "case_total_sec": 1.25,
            },
        }

        summary = _case_summary(row)

        self.assertEqual(
            summary["rtdl_optix_execution_route"],
            "prepared_optix_left_id_dense_count_loaded_case_reuse",
        )
        self.assertTrue(summary["loaded_case_reuse_enabled"])
        self.assertEqual(summary["subprobe_wrapper_phase_timing_sec"]["shared_load_case_sec"], 0.50)
        self.assertEqual(summary["subprobe_wrapper_phase_timing_sec"]["rtdl_optix_call_sec"], 0.75)
        self.assertGreater(summary["rtdl_optix_speedup_vs_numba"], 1.0)

    def test_case_summary_keeps_old_rows_without_nested_timing_valid(self) -> None:
        row = {
            "workload": "pip",
            "dataset": "points.cdb",
            "counts_match": True,
            "numba_cuda_jit_baseline": {"hot_median_sec": 0.001},
            "rtdl_optix": {"hot_median_sec": 0.002},
        }

        summary = _case_summary(row)

        self.assertNotIn("subprobe_wrapper_phase_timing_sec", summary)
        self.assertNotIn("loaded_case_reuse_enabled", summary)
        self.assertEqual(summary["recommended_route"], "numba_cuda_jit_scalar_count")


if __name__ == "__main__":
    unittest.main()
