from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4306_partner_column_contracts_foundation_2026-06-11.md"
CONTRACTS = ROOT / "src" / "rtdsl" / "partner_column_contracts.py"
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
NUMBA_CONTINUATION = ROOT / "src" / "rtdsl" / "numba_partner_continuation.py"


def _to_host_ints(column) -> list[int]:
    return [int(value) for value in column.copy_to_host().tolist()]


class Goal4306PartnerColumnContractsFoundationTest(unittest.TestCase):
    def test_group_id_contract_accepts_and_rejects_equal_segments(self) -> None:
        contract = rt.make_equal_contiguous_group_id_contract(
            operation="grouped_topk_f64",
            group_count=4,
            row_count=24,
            rows_per_group=6,
        )
        validation = rt.validate_group_id_contract(contract)
        self.assertEqual(validation["status"], "accept")
        metadata = validation["metadata"]
        self.assertEqual(metadata["partner_column_contract_version"], rt.PARTNER_COLUMN_CONTRACT_VERSION)
        self.assertEqual(metadata["group_id_layout"], rt.GROUP_LAYOUT_EQUAL_CONTIGUOUS_SEGMENTS)
        self.assertEqual(metadata["rows_per_group"], 6)

        rejected = rt.validate_group_id_contract(
            rt.make_equal_contiguous_group_id_contract(
                operation="grouped_topk_f64",
                group_count=4,
                row_count=25,
                rows_per_group=6,
            )
        )
        self.assertEqual(rejected["status"], "reject")
        self.assertIn("rows_per_group * group_count must equal row_count", rejected["errors"])

    def test_claim_boundary_defaults_fail_closed(self) -> None:
        metadata = rt.default_partner_claim_boundary_metadata()
        self.assertTrue(metadata)
        self.assertTrue(all(value is False for value in metadata.values()))
        self.assertEqual(rt.validate_partner_claim_boundary(metadata)["status"], "accept")

        leaked = dict(metadata)
        leaked["whole_app_speedup_claim_authorized"] = True
        validation = rt.validate_partner_claim_boundary(leaked)
        self.assertEqual(validation["status"], "reject")
        self.assertIn("whole_app_speedup_claim_authorized", validation["errors"][0])

    def test_contract_layer_is_wired_into_numba_topk_sources(self) -> None:
        contract_source = CONTRACTS.read_text(encoding="utf-8")
        self.assertIn("RtdlGroupIdContract", contract_source)
        self.assertIn("RtdlPartnerClaimBoundary", contract_source)
        self.assertIn("equal_contiguous_group_segments", contract_source)

        adapter_source = ADAPTERS.read_text(encoding="utf-8")
        self.assertIn("make_equal_contiguous_group_id_contract", adapter_source)
        self.assertIn("default_partner_claim_boundary_metadata", adapter_source)

        numba_source = NUMBA_CONTINUATION.read_text(encoding="utf-8")
        self.assertIn("require_group_id_contract", numba_source)
        self.assertIn("make_equal_contiguous_group_id_contract", numba_source)

    def test_report_documents_fable5_p2_slice(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal4306",
            "shared partner-column contract layer",
            "RtdlGroupIdContract",
            "RtdlPartnerClaimBoundary",
            "grouped_topk_f64",
            "does not authorize",
        ):
            self.assertIn(phrase, text)

    def test_numba_topk_emits_shared_contract_metadata_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is required for executable contract metadata validation")
        import numpy as np
        from numba import cuda

        group_ids = cuda.to_device(np.asarray([0, 0, 1, 1], dtype=np.int64))
        item_ids = cuda.to_device(np.asarray([3, 2, 8, 7], dtype=np.int64))
        scores = cuda.to_device(np.asarray([2.0, 1.0, 9.0, 4.0], dtype=np.float64))
        result = rt.run_numba_grouped_topk_f64(
            group_ids,
            item_ids,
            scores,
            group_count=2,
            k=1,
            rows_per_group=2,
        )
        self.assertEqual(_to_host_ints(result["outputs"]["item_ids"]), [2, 7])
        self.assertEqual(result["partner_column_contract_version"], rt.PARTNER_COLUMN_CONTRACT_VERSION)
        self.assertEqual(result["group_id_layout"], rt.GROUP_LAYOUT_EQUAL_CONTIGUOUS_SEGMENTS)
        self.assertEqual(result["rows_per_group"], 2)


if __name__ == "__main__":
    unittest.main()
