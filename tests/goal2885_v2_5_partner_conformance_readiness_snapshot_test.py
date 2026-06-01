from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2885_v2_5_partner_conformance_readiness_snapshot_2026-05-31.md"


class Goal2885V25PartnerConformanceReadinessSnapshotTest(unittest.TestCase):
    def test_readiness_packet_exposes_compact_partner_conformance_snapshot(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        snapshot = packet["partner_conformance_snapshot"]

        self.assertEqual("accept", validation["status"])
        self.assertEqual("rtdl.v2_5.partner_conformance_matrix.v1", snapshot["matrix_version"])
        self.assertEqual("accept", snapshot["status"])
        self.assertEqual(12, snapshot["operation_count"])
        self.assertEqual(48, snapshot["cell_count"])
        self.assertTrue(snapshot["preview_runtime_conformance_complete"])
        self.assertEqual(0, snapshot["runtime_conformance_gap_count"])
        self.assertEqual(0, snapshot["release_blocker_count"])
        self.assertFalse(snapshot["release_conformance_complete"])
        self.assertGreater(snapshot["pod_runtime_cell_count"], 0)
        self.assertGreater(snapshot["descriptor_only_cell_count"], 0)

    def test_snapshot_keeps_descriptor_only_cells_visible(self) -> None:
        snapshot = rt.v2_5_internal_readiness_packet(repo_root=ROOT)["partner_conformance_snapshot"]
        descriptor_cells = snapshot["descriptor_only_cells"]

        self.assertTrue(any(cell["partner"] == "cupy_conformance" for cell in descriptor_cells))
        self.assertTrue(
            any(cell["operation"] == "segmented_count_i64" for cell in descriptor_cells)
        )
        self.assertIn("does not authorize release", snapshot["claim_boundary"])

    def test_snapshot_keeps_pod_runtime_cells_visible(self) -> None:
        snapshot = rt.v2_5_internal_readiness_packet(repo_root=ROOT)["partner_conformance_snapshot"]
        pod_cells = snapshot["pod_runtime_cells"]

        self.assertTrue(
            any(
                cell["partner"] == "triton"
                and cell["operation"] == "grouped_topk_f64"
                and cell["evidence_goal"] == "Goal2872"
                for cell in pod_cells
            )
        )
        self.assertTrue(
            any(
                cell["partner"] == "numba"
                and cell["operation"] == "segmented_sum_f64"
                and cell["evidence_goal"] == "Goal2875"
                for cell in pod_cells
            )
        )

    def test_readiness_indexes_goal2885_report(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        path = "docs/reports/goal2885_v2_5_partner_conformance_readiness_snapshot_2026-05-31.md"

        self.assertTrue(packet["required_report_presence"][path])
        self.assertIn("keep_goal2885_partner_conformance_snapshot_green", packet["allowed_next_actions"])

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2885",
            "partner_conformance_snapshot",
            "runtime conformance gaps are zero",
            "release conformance remains false",
            "not a v2.5 release authorization",
            "not true-zero-copy wording",
            "does not promote descriptor-only",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
