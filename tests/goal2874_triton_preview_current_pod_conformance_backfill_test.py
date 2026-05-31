from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2874_triton_preview_current_pod_conformance_backfill_2026-05-31.md"


class Goal2874TritonPreviewCurrentPodConformanceBackfillTest(unittest.TestCase):
    def test_all_triton_preview_operations_now_have_pod_runtime_conformance_rows(self) -> None:
        matrix = rt.v2_5_partner_conformance_matrix()
        validation = rt.validate_v2_5_partner_conformance_matrix(matrix)

        self.assertEqual("accept", validation["status"])
        for operation in rt.V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS:
            cell = rt.plan_v2_5_partner_conformance(operation, "triton")
            self.assertEqual(rt.V2_5_CONFORMANCE_STATUS_POD_RUNTIME, cell["conformance_status"], operation)
            self.assertFalse(cell["release_blocker"], operation)
            self.assertNotEqual("support-matrix", cell["evidence_goal"])

    def test_only_numba_preview_rows_remain_runtime_conformance_gaps(self) -> None:
        matrix = rt.v2_5_partner_conformance_matrix()
        blockers = {
            (cell["operation"], cell["partner"]): cell["conformance_status"]
            for cell in matrix["release_blockers"]
        }

        self.assertEqual(
            {
                ("segmented_count_i64", rt.V2_5_FALLBACK_PARTNER): rt.V2_5_CONFORMANCE_STATUS_RUNTIME_GAP,
                ("segmented_sum_f64", rt.V2_5_FALLBACK_PARTNER): rt.V2_5_CONFORMANCE_STATUS_RUNTIME_GAP,
            },
            blockers,
        )
        self.assertEqual(2, matrix["release_blocker_count"])
        self.assertEqual(2, matrix["runtime_conformance_gap_count"])

    def test_goal2874_rows_reference_current_pod_backfill_report(self) -> None:
        for operation in (
            "segmented_count_i64",
            "segmented_min_f64",
            "segmented_max_f64",
            "compact_mask_i64",
            "bounded_collect_finalize_i64",
        ):
            cell = rt.plan_v2_5_partner_conformance(operation, "triton")

            self.assertEqual("Goal2874", cell["evidence_goal"])
            self.assertIn(
                "docs/reports/goal2874_triton_preview_current_pod_conformance_backfill_2026-05-31.md",
                cell["report_paths"],
            )

    def test_readiness_packet_indexes_goal2874(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        path = "docs/reports/goal2874_triton_preview_current_pod_conformance_backfill_2026-05-31.md"

        self.assertEqual("accept", validation["status"])
        self.assertTrue(packet["required_report_presence"][path])

    def test_report_records_pod_backfill_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2874",
            "25 tests",
            "current pod",
            "segmented_count_i64",
            "bounded_collect_finalize_i64",
            "not a v2.5 release authorization",
            "Numba",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
