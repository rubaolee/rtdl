from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2872_triton_tie_break_conformance_smoke_2026-05-31.md"


def _torch():
    import torch

    return torch


def _to_list(tensor):
    return tensor.detach().cpu().tolist()


@unittest.skipUnless(rt.triton_partner_available(), "Triton CUDA conformance smoke requires an NVIDIA CUDA runtime")
class Goal2872TritonTieBreakConformanceSmokeTest(unittest.TestCase):
    def test_grouped_argmin_tie_break_matches_reference(self) -> None:
        torch = _torch()
        group_ids = torch.tensor([0, 0, 0, 1, 1], dtype=torch.int64, device="cuda")
        item_ids = torch.tensor([7, 3, 5, 4, 2], dtype=torch.int64, device="cuda")
        scores = torch.tensor([1.0, 1.0, 0.5, 9.0, 9.0], dtype=torch.float64, device="cuda")
        expected = rt.execute_v2_5_partner_continuation_reference(
            "grouped_argmin_f64",
            {"group_ids": [0, 0, 0, 1, 1], "item_ids": [7, 3, 5, 4, 2], "scores": [1.0, 1.0, 0.5, 9.0, 9.0], "group_count": 3},
        )["outputs"]

        actual = rt.run_triton_grouped_argmin_f64(group_ids, item_ids, scores, group_count=3)["outputs"]

        self.assertEqual(expected["group_ids"], _to_list(actual["group_ids"]))
        self.assertEqual(expected["item_ids"], _to_list(actual["item_ids"]))
        self.assertEqual(expected["scores"], _to_list(actual["scores"]))
        self.assertEqual(expected["missing_group_ids"], _to_list(actual["missing_group_ids"]))

    def test_grouped_argmax_tie_break_matches_reference(self) -> None:
        torch = _torch()
        group_ids = torch.tensor([0, 0, 1, 1], dtype=torch.int64, device="cuda")
        item_ids = torch.tensor([8, 1, 6, 5], dtype=torch.int64, device="cuda")
        scores = torch.tensor([2.0, 2.0, 3.0, 3.0], dtype=torch.float64, device="cuda")
        expected = rt.execute_v2_5_partner_continuation_reference(
            "grouped_argmax_f64",
            {"group_ids": [0, 0, 1, 1], "item_ids": [8, 1, 6, 5], "scores": [2.0, 2.0, 3.0, 3.0], "group_count": 3},
        )["outputs"]

        actual = rt.run_triton_grouped_argmax_f64(group_ids, item_ids, scores, group_count=3)["outputs"]

        self.assertEqual(expected["group_ids"], _to_list(actual["group_ids"]))
        self.assertEqual(expected["item_ids"], _to_list(actual["item_ids"]))
        self.assertEqual(expected["scores"], _to_list(actual["scores"]))
        self.assertEqual(expected["missing_group_ids"], _to_list(actual["missing_group_ids"]))

    def test_grouped_topk_tie_and_duplicate_policy_matches_reference(self) -> None:
        torch = _torch()
        group_ids = torch.tensor([0, 0, 0, 0, 1, 1], dtype=torch.int64, device="cuda")
        item_ids = torch.tensor([5, 5, 2, 3, 9, 8], dtype=torch.int64, device="cuda")
        scores = torch.tensor([1.0, 0.8, 0.8, 1.5, 4.0, 4.0], dtype=torch.float64, device="cuda")
        expected = rt.execute_v2_5_partner_continuation_reference(
            "grouped_topk_f64",
            {
                "group_ids": [0, 0, 0, 0, 1, 1],
                "item_ids": [5, 5, 2, 3, 9, 8],
                "scores": [1.0, 0.8, 0.8, 1.5, 4.0, 4.0],
                "group_count": 3,
                "k": 2,
            },
        )["outputs"]

        actual = rt.run_triton_grouped_topk_f64(group_ids, item_ids, scores, group_count=3, k=2)["outputs"]

        self.assertEqual(expected["group_ids"], _to_list(actual["group_ids"]))
        self.assertEqual(expected["item_ids"], _to_list(actual["item_ids"]))
        self.assertEqual(expected["scores"], _to_list(actual["scores"]))
        self.assertEqual(expected["ranks"], _to_list(actual["ranks"]))
        self.assertEqual(expected["row_offsets"], _to_list(actual["row_offsets"]))
        self.assertEqual(expected["missing_group_ids"], _to_list(actual["missing_group_ids"]))

    def test_float_reduction_previews_match_reference_on_ordered_fixture(self) -> None:
        torch = _torch()
        group_ids = torch.tensor([0, 0, 1, 1, 1], dtype=torch.int64, device="cuda")
        values = torch.tensor([1.25, -0.25, 2.0, 3.5, -1.0], dtype=torch.float64, device="cuda")
        values_x = torch.tensor([1.0, 2.0, -1.0, 4.0, 3.0], dtype=torch.float64, device="cuda")
        values_y = torch.tensor([0.5, 1.5, -2.0, 2.0, 1.0], dtype=torch.float64, device="cuda")
        sum_expected = rt.execute_v2_5_partner_continuation_reference(
            "segmented_sum_f64",
            {"group_ids": [0, 0, 1, 1, 1], "values": [1.25, -0.25, 2.0, 3.5, -1.0], "group_count": 3},
        )["outputs"]
        vector_expected = rt.execute_v2_5_partner_continuation_reference(
            "grouped_vector_sum_f64x2",
            {
                "group_ids": [0, 0, 1, 1, 1],
                "values_x": [1.0, 2.0, -1.0, 4.0, 3.0],
                "values_y": [0.5, 1.5, -2.0, 2.0, 1.0],
                "group_count": 3,
            },
        )["outputs"]

        sum_actual = rt.run_triton_segmented_sum_f64(group_ids, values, group_count=3)["outputs"]
        vector_actual = rt.run_triton_grouped_vector_sum_f64x2(group_ids, values_x, values_y, group_count=3)["outputs"]

        self.assertEqual(sum_expected["sums"], _to_list(sum_actual["sums"]))
        self.assertEqual(vector_expected["sum_x"], _to_list(vector_actual["sum_x"]))
        self.assertEqual(vector_expected["sum_y"], _to_list(vector_actual["sum_y"]))


class Goal2872TritonTieBreakConformanceMetadataTest(unittest.TestCase):
    def test_readiness_packet_indexes_goal2872_report(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        path = "docs/reports/goal2872_triton_tie_break_conformance_smoke_2026-05-31.md"

        self.assertEqual("accept", validation["status"])
        self.assertTrue(packet["required_report_presence"][path])

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2872",
            "Triton",
            "tie-break",
            "reference",
            "not a v2.5 release authorization",
            "not a public speedup claim",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
