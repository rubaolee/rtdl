from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "src" / "rtdsl" / "partner_column_contracts.py"
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
NUMBA_CONTINUATION = ROOT / "src" / "rtdsl" / "numba_partner_continuation.py"
REPORT = ROOT / "docs" / "reports" / "goal4323_dense_group_contract_metadata_2026-06-11.md"


class Goal4323DenseGroupContractMetadataTest(unittest.TestCase):
    def test_dense_zero_based_contract_helper_accepts_and_rejects(self) -> None:
        contract = rt.make_dense_zero_based_group_id_contract(
            operation="grouped_argmin_f64",
            group_count=3,
            row_count=12,
        )
        validation = rt.validate_group_id_contract(contract)

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["metadata"]["partner_column_contract_version"], rt.PARTNER_COLUMN_CONTRACT_VERSION)
        self.assertEqual(validation["metadata"]["group_id_layout"], rt.GROUP_LAYOUT_DENSE_ZERO_BASED)
        self.assertIsNone(validation["metadata"]["rows_per_group"])

        rejected = rt.validate_group_id_contract(
            rt.make_dense_zero_based_group_id_contract(
                operation="grouped_argmin_f64",
                group_count=0,
                row_count=1,
            )
        )
        self.assertEqual(rejected["status"], "reject")
        self.assertIn("non-empty dense zero-based group ids require group_count > 0", rejected["errors"])

    def test_public_exports_include_dense_contract_helper(self) -> None:
        for name in (
            "GROUP_LAYOUT_DENSE_ZERO_BASED",
            "make_dense_zero_based_group_id_contract",
            "make_equal_contiguous_group_id_contract",
            "require_group_id_contract",
            "validate_group_id_contract",
        ):
            self.assertIn(name, rt.__all__)
            self.assertTrue(hasattr(rt, name))

    def test_arg_reduction_sources_emit_shared_dense_contract_metadata(self) -> None:
        contracts_source = CONTRACTS.read_text(encoding="utf-8")
        adapter_source = ADAPTERS.read_text(encoding="utf-8")
        numba_source = NUMBA_CONTINUATION.read_text(encoding="utf-8")

        self.assertIn("make_dense_zero_based_group_id_contract", contracts_source)
        self.assertIn("dense zero-based group ids do not use rows_per_group", contracts_source)
        self.assertIn("_dense_group_id_contract_metadata", adapter_source)
        self.assertIn("grouped_argmin_f64", adapter_source)
        self.assertIn("grouped_argmax_f64", adapter_source)
        self.assertIn("grouped_topk_f64", adapter_source)
        self.assertIn("make_dense_zero_based_group_id_contract", numba_source)
        self.assertIn("device_resident_error_flag", numba_source)

    def test_report_documents_scope_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal4323",
            "dense zero-based group-id contract",
            "grouped argmin, grouped argmax, and non-Numba grouped top-k",
            "does not authorize",
        ):
            self.assertIn(phrase, text)

    def test_numba_argmin_emits_dense_contract_metadata_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is required for executable dense-contract validation")

        import numpy as np
        from numba import cuda

        group_ids = cuda.to_device(np.asarray([0, 0, 1, 1], dtype=np.int64))
        item_ids = cuda.to_device(np.asarray([4, 3, 9, 8], dtype=np.int64))
        scores = cuda.to_device(np.asarray([2.0, 1.0, 5.0, 4.0], dtype=np.float64))
        result = rt.run_numba_grouped_argmin_f64(
            group_ids,
            item_ids,
            scores,
            group_count=2,
        )

        self.assertEqual(result["partner_column_contract_version"], rt.PARTNER_COLUMN_CONTRACT_VERSION)
        self.assertEqual(result["group_id_layout"], rt.GROUP_LAYOUT_DENSE_ZERO_BASED)
        self.assertEqual(result["group_id_contract_operation"], "grouped_argmin_f64")
        self.assertEqual(result["group_count"], 2)
        self.assertEqual(result["row_count"], 4)


if __name__ == "__main__":
    unittest.main()
