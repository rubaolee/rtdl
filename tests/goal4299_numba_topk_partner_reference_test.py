from __future__ import annotations

from pathlib import Path
import json
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
ANN_APP = ROOT / "examples" / "current" / "apps" / "ml" / "rtdl_ann_candidate_app.py"
REPORT = ROOT / "docs" / "reports" / "goal4299_numba_topk_partner_reference_for_v2_11_embree_cpu_packet_2026-06-11.md"
ANN_CLI_ARTIFACT = ROOT / "docs" / "reports" / "goal4299_ann_candidate_numba_cli_local_linux.json"


def _to_host_ints(column) -> list[int]:
    return [int(value) for value in column.copy_to_host().tolist()]


def _to_host_rounded_floats(column) -> list[float]:
    return [round(float(value), 12) for value in column.copy_to_host().tolist()]


class Goal4299NumbaTopKPartnerReferenceTest(unittest.TestCase):
    def test_adapter_source_exposes_honest_numba_reference_path(self) -> None:
        source = ADAPTERS.read_text(encoding="utf-8")
        self.assertIn('partner == "numba"', source)
        self.assertIn("pairwise_l2_sq_score_rows_2d_partner_columns", source)
        self.assertIn("reference_host_rank_after_device_score_rows", source)
        self.assertIn("host_rank_materialization_used", source)
        self.assertIn("host_rank_topk_f64_reference", source)

        ann_source = ANN_APP.read_text(encoding="utf-8")
        self.assertIn('if partner == "numba"', ann_source)
        self.assertIn("copy_to_host().tolist()", ann_source)
        self.assertIn('choices=("torch", "cupy", "numba")', ann_source)

    def test_report_documents_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal4299",
            "partner=\"numba\"",
            "pairwise_l2_sq_score_rows_2d",
            "reference_host_rank_after_device_score_rows",
            "host_rank_materialization_used: True",
            "does not authorize public speedup wording",
            "future high-performance target",
        ):
            self.assertIn(phrase, text)

    def test_numba_topk_matches_same_contract_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is required for executable top-k validation")

        queries = (
            rt.Point(100, 0.0, 0.0),
            rt.Point(101, 2.0, 0.0),
        )
        candidates = (
            rt.Point(9, 1.0, 0.0),
            rt.Point(5, -1.0, 0.0),
            rt.Point(7, 3.0, 0.0),
        )
        query_columns = rt.point_rows_to_partner_columns(queries, partner="numba")
        candidate_columns = rt.point_rows_to_partner_columns(candidates, partner="numba")

        result = rt.top_k_nearest_points_2d_partner_columns(
            query_columns,
            candidate_columns,
            k=2,
            partner="numba",
            return_metadata=True,
        )
        columns = result["columns"]
        metadata = result["metadata"]

        self.assertEqual(_to_host_ints(columns["query_ids"]), [100, 100, 101, 101])
        self.assertEqual(_to_host_ints(columns["neighbor_ids"]), [5, 9, 7, 9])
        self.assertEqual(_to_host_ints(columns["neighbor_rank"]), [1, 2, 1, 2])
        self.assertEqual(_to_host_rounded_floats(columns["distances"]), [1.0, 1.0, 1.0, 1.0])

        self.assertEqual(metadata["partner"], "numba")
        self.assertEqual(metadata["partner_reference_contract"], "generic_exact_top_k_nearest_points_2d")
        self.assertEqual(
            metadata["v2_11_numba_preview_kernel_status"],
            "reference_host_rank_after_device_score_rows",
        )
        self.assertTrue(metadata["numba_score_rows_generated_on_partner_device"])
        self.assertTrue(metadata["host_rank_materialization_used"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
        self.assertFalse(metadata["whole_app_speedup_claim_authorized"])

    def test_ann_cli_numba_artifact_closes_review_reachability_note(self) -> None:
        payload = json.loads(ANN_CLI_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["backend"], "partner_exact_quality")
        self.assertEqual(payload["partner"], "numba")
        self.assertEqual(
            payload["approximate_metadata"]["v2_11_numba_preview_kernel_status"],
            "reference_host_rank_after_device_score_rows",
        )
        self.assertTrue(payload["approximate_metadata"]["host_rank_materialization_used"])
        self.assertFalse(payload["claim_boundary"]["whole_app_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
