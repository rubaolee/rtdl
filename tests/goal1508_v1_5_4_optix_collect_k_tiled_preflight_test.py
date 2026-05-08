import unittest

from scripts import goal1508_v1_5_4_optix_collect_k_tiled_preflight as preflight


def make_payload(max_shared: int) -> dict:
    cases = [
        preflight._case_for_count(count, max_shared)
        for count in (4097, 65537, 131072)
    ]
    return {
        "goal": "Goal1508",
        "status": "goal1508_optix_collect_k_tiled_preflight_recorded",
        "git_commit": "synthetic",
        "platform": "synthetic",
        "device_name": "NVIDIA synthetic",
        "cuda_driver_version": 0,
        "cuda_attribute": {
            "name": "CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK_OPTIN",
            "value": preflight.CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK_OPTIN,
            "max_optin_shared_memory_per_block_bytes": max_shared,
        },
        "row_width2_tile_shared_memory_bytes": preflight.ROW_WIDTH2_TILE_SHARED_BYTES,
        "cases": cases,
        "all_requested_counts_are_goal1506_profile_candidates": all(
            case["accepted_goal1506_profile_candidate"] for case in cases
        ),
        "claim_flags": {
            "true_zero_copy_authorized": False,
            "public_speedup_wording_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "stable_public_primitive_authorized": False,
            "partner_tensor_handoff_authorized": False,
            "release_action_authorized": False,
        },
        "claim_boundary": "synthetic boundary",
    }


class Goal1508V154OptixCollectKTiledPreflightTest(unittest.TestCase):
    def test_row_width2_tile_shared_memory_requirement_is_stable(self) -> None:
        self.assertEqual(preflight.ROW_WIDTH2_TILE_SHARED_BYTES, 69632)
        self.assertEqual(preflight.CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK_OPTIN, 97)

    def test_preflight_accepts_sufficient_shared_memory_payload(self) -> None:
        payload = make_payload(preflight.ROW_WIDTH2_TILE_SHARED_BYTES)

        self.assertIs(preflight.validate_preflight(payload), payload)
        self.assertTrue(payload["all_requested_counts_are_goal1506_profile_candidates"])
        for case in payload["cases"]:
            with self.subTest(count=case["candidate_count"]):
                self.assertEqual(case["predicted_profile_native_path"], case["expected_native_path"])
                self.assertTrue(case["accepted_goal1506_profile_candidate"])

    def test_preflight_accepts_insufficient_shared_memory_as_non_candidate(self) -> None:
        payload = make_payload(preflight.ROW_WIDTH2_TILE_SHARED_BYTES - 1)

        self.assertIs(preflight.validate_preflight(payload), payload)
        self.assertFalse(payload["all_requested_counts_are_goal1506_profile_candidates"])
        for case in payload["cases"]:
            with self.subTest(count=case["candidate_count"]):
                self.assertEqual(case["predicted_profile_native_path"], "dynamic_row_width_single_thread_fallback")
                self.assertFalse(case["accepted_goal1506_profile_candidate"])

    def test_preflight_rejects_inconsistent_aggregate_flag(self) -> None:
        payload = make_payload(preflight.ROW_WIDTH2_TILE_SHARED_BYTES)
        payload["all_requested_counts_are_goal1506_profile_candidates"] = False

        with self.assertRaisesRegex(ValueError, "aggregate profile candidate"):
            preflight.validate_preflight(payload)

    def test_preflight_rejects_claim_expansion(self) -> None:
        payload = make_payload(preflight.ROW_WIDTH2_TILE_SHARED_BYTES)
        payload["claim_flags"]["public_speedup_wording_authorized"] = True

        with self.assertRaisesRegex(ValueError, "public_speedup_wording_authorized"):
            preflight.validate_preflight(payload)


if __name__ == "__main__":
    unittest.main()
