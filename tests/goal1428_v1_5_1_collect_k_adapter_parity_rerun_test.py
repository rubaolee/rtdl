from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal1428V151CollectKAdapterParityRerunTest(unittest.TestCase):
    def test_contract_records_adapter_parity_ok_and_binary_validation_pending(self) -> None:
        contract = rt.validate_v1_5_1_collect_k_bounded_native_generic_abi_contract()

        self.assertEqual(
            contract["status"],
            "source_symbols_present_python_adapter_routed_embree_optix_adapter_parity_ok_binary_validation_pending",
        )
        self.assertFalse(contract["native_binary_validation_present"])
        self.assertFalse(contract["stable_promotion_authorized"])
        self.assertEqual(
            contract["required_adapter_work"],
            (
                "add_embree_optix_generic_abi_parity_tests",
                "validate_embree_optix_generic_i64_symbols_in_built_libraries",
            ),
        )
        self.assertIn("Post-adapter Embree and OptiX polygon-pair parity are accepted", contract["claim_boundary"])

    def test_summary_report_records_exact_post_adapter_parity_state(self) -> None:
        report = (
            ROOT
            / "docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_rerun_2026-05-06.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Post-adapter polygon-pair parity is accepted for Embree", report)
        self.assertIn("still pending for\nOptiX", report)
        self.assertIn("Embree: pass=4, fail=0, skipped=0", report)
        self.assertIn("OptiX: pass=0, fail=0, skipped=4", report)
        self.assertIn("librtdl_optix not found", report)
        self.assertIn("Connection refused", report)
        collapsed = " ".join(report.split())
        self.assertIn("not a speedup claim", collapsed)
        self.assertIn("not a zero-copy claim", collapsed)

    def test_required_artifacts_exist(self) -> None:
        for relative_path in (
            "docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_windows_optional_2026-05-06.json",
            "docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_windows_optional_2026-05-06.md",
            "docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_linux_embree_2026-05-06.json",
            "docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_linux_embree_2026-05-06.md",
            "docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_linux_optix_2026-05-06.json",
            "docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_linux_optix_2026-05-06.md",
        ):
            with self.subTest(relative_path=relative_path):
                self.assertTrue((ROOT / relative_path).exists())


if __name__ == "__main__":
    unittest.main()
