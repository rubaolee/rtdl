import unittest

from scripts import goal1504_v1_5_4_optix_collect_k_tiled_overflow_probe as probe


def make_case(candidate_count: int) -> dict:
    unique_count = max(1, candidate_count // 2)
    return {
        "candidate_count": candidate_count,
        "row_width": 2,
        "unique_count": unique_count,
        "capacity": unique_count - 1,
        "expected_native_path": "row_width2_bounded_multi_tile_sort_merge",
        "valid_count": unique_count,
        "overflowed": True,
        "output_sentinel": probe.OUTPUT_SENTINEL,
        "output_flat_sample": [probe.OUTPUT_SENTINEL] * 4,
        "fail_closed_output_preserved": True,
        "same_valid_count": True,
        "same_overflowed_flag": True,
        "transfer_accounting": {
            "host_to_device_transfers_before_backend_execution": 0,
            "device_to_host_transfers_after_backend_execution": 2,
            "internal_device_transfers_if_any": 3,
            "allocation_only_transfers_distinguished_from_content_transfers": True,
        },
    }


def make_payload() -> dict:
    return {
        "goal": "Goal1504",
        "status": "goal1504_optix_collect_k_tiled_overflow_probe_recorded",
        "git_commit": "synthetic",
        "platform": "synthetic",
        "device_name": "NVIDIA synthetic",
        "cuda_driver_version": 0,
        "library_path": "synthetic",
        "measured_on_real_nvidia": True,
        "python_entry_point": "rtdsl.optix_runtime.collect_k_bounded_i64_device_optix",
        "native_symbol": "rtdl_optix_collect_k_bounded_i64_device",
        "cases": [make_case(count) for count in probe.DEFAULT_COUNTS],
        "all_fail_closed_passed": True,
        "claim_flags": {
            "true_zero_copy_authorized": False,
            "public_speedup_wording_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "stable_public_primitive_authorized": False,
            "partner_tensor_handoff_authorized": False,
            "release_action_authorized": False,
        },
        "claim_boundary": (
            "Goal1504 records overflow/fail-closed behavior for the experimental Python "
            "OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize "
            "true zero-copy wording, public speedup wording, whole-app claims, partner "
            "tensor handoff, stable primitive promotion, or release action."
        ),
    }


class Goal1504V154OptixCollectKTiledOverflowProbeTest(unittest.TestCase):
    def test_default_counts_cover_tiled_boundaries(self) -> None:
        self.assertEqual(probe.DEFAULT_COUNTS, (4097, 65537, 131072))
        self.assertEqual(probe._expected_native_path(4097, 2), "row_width2_bounded_multi_tile_sort_merge")
        self.assertEqual(probe._expected_native_path(131072, 2), "row_width2_bounded_multi_tile_sort_merge")

    def test_validate_accepts_synthetic_fail_closed_payload(self) -> None:
        payload = make_payload()
        self.assertIs(probe.validate_probe(payload), payload)

    def test_validate_rejects_partial_output_on_overflow(self) -> None:
        payload = make_payload()
        payload["cases"][0]["fail_closed_output_preserved"] = False
        payload["all_fail_closed_passed"] = False
        with self.assertRaisesRegex(ValueError, "fail closed"):
            probe.validate_probe(payload)

    def test_validate_rejects_claim_expansion(self) -> None:
        payload = make_payload()
        payload["claim_flags"]["public_speedup_wording_authorized"] = True
        with self.assertRaisesRegex(ValueError, "public_speedup_wording_authorized"):
            probe.validate_probe(payload)


if __name__ == "__main__":
    unittest.main()
