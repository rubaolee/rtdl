from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
MIGRATION = ROOT / "src" / "rtdsl" / "v2_5_triton_app_migration.py"
REPORT = ROOT / "docs/reports/goal2861_v2_5_generic_partner_front_door_completion_2026-05-31.md"
REVIEW = ROOT / "docs/reviews/goal2862_gemini_review_goal2861_generic_front_door_completion_2026-05-31.md"
CONSENSUS = ROOT / "docs/reports/goal2862_goal2861_generic_front_door_completion_consensus_2026-05-31.md"


class Goal2861V25GenericPartnerFrontDoorCompletionTest(unittest.TestCase):
    def test_new_generic_front_doors_are_exported_and_app_agnostic(self) -> None:
        source = ADAPTERS.read_text(encoding="utf-8")
        migration = MIGRATION.read_text(encoding="utf-8")

        for name in (
            "grouped_argmin_f64_partner_columns",
            "grouped_argmax_f64_partner_columns",
            "grouped_topk_f64_partner_columns",
            "bounded_collect_finalize_i64_partner_columns",
        ):
            self.assertIn(f"def {name}", source)
            self.assertIn(name, rt.__all__)
        for operation in (
            "grouped_argmin_f64",
            "grouped_argmax_f64",
            "grouped_topk_f64",
            "bounded_collect_finalize_i64",
            "grouped_vector_sum_f64x2",
        ):
            self.assertIn(operation, migration)
        self.assertIn("not_called_partner_continuation_only", source)
        self.assertIn("does not embed app semantics", source)
        self.assertIn("does not authorize speedup", source)

    def test_all_ten_benchmark_apps_have_generic_front_door_coverage(self) -> None:
        coverage = rt.v2_5_triton_front_door_coverage()

        self.assertEqual(coverage["benchmark_app_count"], 10)
        self.assertEqual(coverage["fully_front_door_ready_count"], 10)
        self.assertEqual(
            set(coverage["adapter_front_door_operations"]),
            {
                "segmented_count_i64",
                "segmented_sum_f64",
                "segmented_min_f64",
                "segmented_max_f64",
                "compact_mask_i64",
                "bounded_collect_finalize_i64",
                "grouped_argmin_f64",
                "grouped_argmax_f64",
                "grouped_topk_f64",
                "grouped_vector_sum_f64x2",
            },
        )
        for row in coverage["apps"]:
            self.assertEqual(row["front_door_status"], "adapter_front_door_ready", row["app_id"])
            self.assertEqual(row["dispatcher_only_operations"], (), row["app_id"])
            self.assertEqual(row["missing_operations"], (), row["app_id"])
        self.assertIn("not CUDA pod evidence", coverage["claim_boundary"])

    def test_report_review_and_consensus_record_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Goal2861", report)
        self.assertIn("10/10", report)
        self.assertIn("not a speedup claim", report)
        self.assertIn("accept-with-boundary", review)
        self.assertIn("accept-with-boundary", consensus)

    def test_generic_front_doors_match_expected_rows_when_cuda_available(self) -> None:
        if not rt.triton_partner_available():
            self.skipTest("triton+torch CUDA are required for executable Triton front-door validation")

        import torch

        score_columns = {
            "group_ids": torch.tensor([0, 0, 0, 1, 1, 1, 1], dtype=torch.int64, device="cuda"),
            "item_ids": torch.tensor([9, 8, 8, 2, 1, 3, 4], dtype=torch.int64, device="cuda"),
            "scores": torch.tensor([4.0, 4.0, 3.5, 7.0, 9.0, 9.0, 6.0], dtype=torch.float64, device="cuda"),
        }

        argmin = rt.grouped_argmin_f64_partner_columns(
            score_columns,
            group_count=3,
            partner="triton",
            return_metadata=True,
        )
        self.assertEqual(argmin["columns"]["group_ids"].detach().cpu().tolist(), [0, 1])
        self.assertEqual(argmin["columns"]["item_ids"].detach().cpu().tolist(), [8, 4])
        self.assertEqual(argmin["columns"]["missing_group_ids"].detach().cpu().tolist(), [2])
        self.assertEqual(argmin["metadata"]["v2_5_partner_continuation_operation"], "grouped_argmin_f64")
        self.assertFalse(argmin["metadata"]["whole_app_speedup_claim_authorized"])

        argmax = rt.grouped_argmax_f64_partner_columns(score_columns, group_count=3, partner="triton")
        self.assertEqual(argmax["group_ids"].detach().cpu().tolist(), [0, 1])
        self.assertEqual(argmax["item_ids"].detach().cpu().tolist(), [8, 1])
        self.assertEqual(argmax["scores"].detach().cpu().tolist(), [4.0, 9.0])

        topk = rt.grouped_topk_f64_partner_columns(score_columns, group_count=3, k=2, partner="triton")
        self.assertEqual(topk["group_ids"].detach().cpu().tolist(), [0, 0, 1, 1])
        self.assertEqual(topk["item_ids"].detach().cpu().tolist(), [8, 9, 4, 2])
        self.assertEqual(topk["ranks"].detach().cpu().tolist(), [1, 2, 1, 2])
        self.assertEqual(topk["row_offsets"].detach().cpu().tolist(), [0, 2, 4, 4])

        bounded = rt.bounded_collect_finalize_i64_partner_columns(
            {
                "group_ids": torch.tensor([0, 1, 1, 2], dtype=torch.int64, device="cuda"),
                "item_ids": torch.tensor([10, 20, 21, 30], dtype=torch.int64, device="cuda"),
            },
            group_count=3,
            k=2,
            partner="triton",
            return_metadata=True,
        )
        self.assertEqual(bounded["columns"]["row_offsets"].detach().cpu().tolist(), [0, 1, 3, 4])
        self.assertEqual(bounded["metadata"]["failure_mode"], "fail_closed_overflow")
        with self.assertRaises(rt.PartnerContinuationOverflowError):
            rt.bounded_collect_finalize_i64_partner_columns(
                {
                    "group_ids": torch.tensor([0, 1, 1, 2], dtype=torch.int64, device="cuda"),
                    "item_ids": torch.tensor([10, 20, 21, 30], dtype=torch.int64, device="cuda"),
                },
                group_count=3,
                k=1,
                partner="triton",
            )


if __name__ == "__main__":
    unittest.main()
