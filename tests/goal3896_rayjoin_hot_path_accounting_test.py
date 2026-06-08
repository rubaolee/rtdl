from __future__ import annotations

import unittest

from scripts.goal3866_rayjoin_representative_scale_profile import _hot_path_summary


class Goal3896RayJoinHotPathAccountingTest(unittest.TestCase):
    def test_hot_path_summary_separates_wrapper_elapsed_from_contract_medians(self) -> None:
        cases = [
            {
                "workload": "pip",
                "counts_match": True,
                "numba_hot_median_sec": 0.0005,
                "rtdl_optix_hot_median_sec": 0.0025,
                "rtdl_optix_speedup_vs_numba": 0.2,
            },
            {
                "workload": "lsi",
                "counts_match": True,
                "numba_hot_median_sec": 0.020,
                "rtdl_optix_hot_median_sec": 0.0001,
                "rtdl_optix_speedup_vs_numba": 200.0,
            },
            {
                "workload": "overlay_seed",
                "counts_match": True,
                "numba_hot_median_sec": 0.050,
                "rtdl_optix_hot_median_sec": 0.0002,
                "rtdl_optix_speedup_vs_numba": 250.0,
            },
        ]
        pip_batch = {
            "single_ms_median": 0.22,
            "largest_request_per_request_ms_median": 0.024,
            "largest_request_count": 100,
        }

        summary = _hot_path_summary(
            cases=cases,
            pip_batch=pip_batch,
            wrapper_elapsed_sec=10.5,
        )

        self.assertEqual(summary["metric_scope"], "per_contract_hot_medians_not_wrapper_wall_time")
        self.assertTrue(summary["scale_runner_elapsed_sec_is_not_hot_path_metric"])
        self.assertEqual(summary["wrapper_elapsed_sec"], 10.5)
        self.assertEqual(summary["contract_count"], 4)
        self.assertTrue(summary["all_contract_counts_match"])
        self.assertEqual(
            summary["pip_one_shot"]["recommended_route"],
            "numba_cuda_jit_scalar_count_no_rawkernel",
        )
        self.assertEqual(
            summary["pip_repeated_requests"]["recommended_route"],
            "rtdl_optix_prepared_batch_executor",
        )
        self.assertAlmostEqual(
            summary["pip_repeated_requests"]["per_request_speedup_vs_single_request"],
            0.22 / 0.024,
        )
        self.assertEqual(
            summary["lsi_scalar_count"]["recommended_route"],
            "rtdl_optix_prepared_segment_pair_count",
        )
        self.assertEqual(
            summary["overlay_active_count"]["recommended_route"],
            "rtdl_optix_prepared_shape_pair_active_count",
        )
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        self.assertFalse(summary["whole_app_speedup_claim_authorized"])
        self.assertFalse(summary["broad_rt_core_claim_authorized"])
        self.assertFalse(summary["paper_reproduction_claim_authorized"])
        self.assertFalse(summary["true_zero_copy_claim_authorized"])
        self.assertFalse(summary["automatic_partner_selection_authorized"])
        self.assertFalse(summary["app_specific_native_engine_logic_allowed"])


if __name__ == "__main__":
    unittest.main()
