from __future__ import annotations

import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal3036_numba_global_argmax_block_reduce_hardening_2026-06-02.md"
NUMBA_SOURCE = REPO_ROOT / "src" / "rtdsl" / "numba_partner_continuation.py"
PARTNER_ADAPTERS = REPO_ROOT / "src" / "rtdsl" / "partner_adapters.py"


class Goal3036NumbaGlobalArgmaxBlockReduceHardeningTest(unittest.TestCase):
    def test_report_records_pod_issue_fix_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3036",
            "multi_stage_block_reduce_no_global_atomics",
            "global CUDA atomics",
            "cuda-python>=12,<13",
            "NUMBA_CUDA_USE_NVIDIA_BINDING=1",
            "NVIDIA RTX A4000, driver 580.159.03",
            "Dirty overlay files",
            "does not authorize",
        ):
            self.assertIn(phrase, text)

    def test_source_uses_block_reduction_instead_of_global_atomics(self) -> None:
        source = NUMBA_SOURCE.read_text(encoding="utf-8")
        start = source.index("def run_numba_global_argmax_u32_f64")
        end = source.index("def run_numba_pairwise_l2_sq_score_rows_2d", start)
        body = source[start:end]

        self.assertIn("_numba_global_argmax_initial_block_reduce_u32_f64_kernel", body)
        self.assertIn("_numba_global_argmax_block_reduce_u32_f64_kernel", source)
        self.assertIn("multi_stage_block_reduce_no_global_atomics", body)
        self.assertNotIn("_numba_global_argmax_score_u32_f64_kernel", source)
        self.assertNotIn("_numba_global_argmax_item_u32_f64_kernel", source)
        self.assertNotIn("_numba_global_argmax_row_u32_f64_kernel", source)

    def test_adapter_metadata_is_self_describing(self) -> None:
        adapter = PARTNER_ADAPTERS.read_text(encoding="utf-8")
        start = adapter.index("def global_argmax_u32_f64_partner_columns")
        end = adapter.index("def _torch_grouped_topk", start)
        body = adapter[start:end]

        self.assertIn('"operation": "global_argmax_u32_f64"', body)
        self.assertIn('"contract": "generic_global_argmax_u32_f64"', body)
        self.assertIn('"reduction_strategy": result.get("reduction_strategy")', body)

    def test_roadmap_indexes_hardening_without_claims(self) -> None:
        roadmap = rt.v2_6_roadmap()
        validation = rt.validate_v2_6_roadmap(repo_root=REPO_ROOT)

        self.assertEqual(roadmap["numba_global_argmax_hardening_goal"], "Goal3036")
        self.assertIn("block_reduce_no_global_atomics", roadmap["numba_global_argmax_hardening_status"])
        self.assertFalse(roadmap["release_authorized"])
        self.assertFalse(roadmap["numba_speedup_claim_authorized"])
        self.assertFalse(roadmap["true_zero_copy_claim_authorized"])
        self.assertEqual(validation["status"], "accept")


if __name__ == "__main__":
    unittest.main()
