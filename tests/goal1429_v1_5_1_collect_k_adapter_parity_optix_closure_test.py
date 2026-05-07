from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal1429V151CollectKAdapterParityOptixClosureTest(unittest.TestCase):
    def test_contract_records_embree_and_optix_adapter_parity_accepted(self) -> None:
        contract = rt.validate_v1_5_1_collect_k_bounded_native_generic_abi_contract()

        self.assertEqual(
            contract["status"],
            "source_symbols_present_python_adapter_routed_embree_optix_adapter_parity_ok_binary_validation_ok_stable_review_pending",
        )
        self.assertTrue(contract["native_binary_validation_present"])
        self.assertFalse(contract["stable_promotion_authorized"])
        self.assertIn("pod_optix_required", contract["post_adapter_parity_evidence"])
        self.assertIn("Post-adapter Embree and OptiX polygon-pair parity are accepted", contract["claim_boundary"])
        self.assertIn("direct same-ABI smoke validation", contract["claim_boundary"])

    def test_required_optix_pod_artifacts_record_acceptance(self) -> None:
        report = (
            ROOT
            / "docs/reports/goal1429_v1_5_1_collect_k_adapter_parity_pod_optix_required_2026-05-06.md"
        ).read_text(encoding="utf-8")

        self.assertIn("ACCEPTED for this measured package", report)
        self.assertIn("Required backends: optix", report)
        self.assertIn("Git HEAD: da7664f88c54aefdbe4d6f6069f26e5c4eb2e8da", report)
        self.assertIn("optix: pass=4, fail=0, skipped=0", report)
        self.assertIn("Required backend skips: none", report)
        self.assertIn("not a public primitive promotion", report)
        self.assertIn("not a performance claim", report)
        self.assertIn("not a zero-copy claim", report)

    def test_summary_keeps_remaining_work_narrow(self) -> None:
        summary = (
            ROOT
            / "docs/reports/goal1429_v1_5_1_collect_k_adapter_parity_optix_closure_2026-05-06.md"
        ).read_text(encoding="utf-8")

        self.assertIn("accepted for both Embree and OptiX", summary)
        self.assertIn("NVIDIA RTX A5000", summary)
        self.assertIn("pass=4, fail=0, skipped=0", summary)
        self.assertIn("does not claim built generic i64 symbol validation", " ".join(summary.split()))
        self.assertIn("Validate `rtdl_embree_collect_k_bounded_i64`", summary)
        self.assertIn("`rtdl_optix_collect_k_bounded_i64`", summary)

    def test_pod_env_and_build_log_exist(self) -> None:
        for relative_path in (
            "docs/reports/goal1429_v1_5_1_collect_k_pod_env_2026-05-06.json",
            "docs/reports/goal1429_v1_5_1_collect_k_build_optix_2026-05-06.txt",
            "docs/reports/goal1429_v1_5_1_collect_k_adapter_parity_pod_optix_required_2026-05-06.json",
            "docs/reports/goal1429_v1_5_1_collect_k_adapter_parity_pod_optix_required_2026-05-06.md",
        ):
            with self.subTest(relative_path=relative_path):
                self.assertTrue((ROOT / relative_path).exists())


if __name__ == "__main__":
    unittest.main()
