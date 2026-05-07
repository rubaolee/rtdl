import unittest

import rtdsl as rt


def accepted_payload() -> dict:
    return {
        "accepted": True,
        "required_backends": ("embree", "optix"),
        "backend_summary": {
            "embree": {"pass": 4, "fail": 0, "skipped": 0},
            "optix": {"pass": 4, "fail": 0, "skipped": 0},
        },
        "failed": (),
        "skipped_required": (),
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "This package validates typed host input plus prepared host output "
            "same-contract backend parity only. It does not authorize true "
            "zero-copy, public speedup wording, whole-app claims, stable "
            "primitive promotion, partner tensor handoff, or release action."
        ),
    }


class Goal1469V153TypedHostPodParityPayloadTest(unittest.TestCase):
    def test_accepts_exact_required_embree_optix_payload(self) -> None:
        result = rt.validate_v1_5_3_typed_host_pod_parity_payload(accepted_payload())

        self.assertEqual(result["status"], "accepted_required_embree_optix_pod_parity_payload")
        self.assertTrue(result["backend_parity_where_claimed_satisfied"])
        self.assertTrue(result["required_pod_parity_accepted"])
        self.assertEqual(result["required_backends"], ("embree", "optix"))
        self.assertEqual(result["required_pass_count_per_backend"], 4)
        self.assertFalse(result["true_zero_copy_authorized"])
        self.assertFalse(result["public_speedup_wording_authorized"])

    def test_rejects_skipped_required_backend(self) -> None:
        payload = accepted_payload()
        payload["backend_summary"]["optix"]["skipped"] = 1

        with self.assertRaisesRegex(ValueError, "optix skipped count must be zero"):
            rt.validate_v1_5_3_typed_host_pod_parity_payload(payload)

    def test_rejects_wrong_required_backend_list(self) -> None:
        payload = accepted_payload()
        payload["required_backends"] = ("embree",)

        with self.assertRaisesRegex(ValueError, "required backends mismatch"):
            rt.validate_v1_5_3_typed_host_pod_parity_payload(payload)

    def test_rejects_public_claim_expansion(self) -> None:
        payload = accepted_payload()
        payload["public_speedup_wording_authorized"] = True

        with self.assertRaisesRegex(ValueError, "public_speedup_wording_authorized=False"):
            rt.validate_v1_5_3_typed_host_pod_parity_payload(payload)


if __name__ == "__main__":
    unittest.main()
