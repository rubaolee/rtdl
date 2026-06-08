from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4023_partition_summary_status_invariants_2026-06-08.md"


class Goal4023PartitionSummaryStatusInvariantsTest(unittest.TestCase):
    def _points(self):
        return (
            (0.0, 0.0, 0.0),
            (0.2, 0.0, 0.0),
            (1.2, 0.0, 0.0),
            (3.0, 0.0, 0.0),
        )

    def test_reference_summary_reports_complete_coverage_when_not_overflowed(self) -> None:
        summary = rt.build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
        )
        metadata = summary["metadata"]
        self.assertFalse(metadata["overflow"])
        self.assertTrue(metadata["complete_candidate_coverage"])
        self.assertEqual(metadata["status_column_values"]["row_count"], metadata["visible_pair_count"])
        self.assertEqual(metadata["status_column_values"]["capacity"], metadata["pair_capacity"])
        self.assertFalse(metadata["status_column_values"]["overflow"])
        self.assertTrue(metadata["status_column_values"]["complete_candidate_coverage"])

    def test_overflow_summary_reports_incomplete_coverage(self) -> None:
        summary = rt.build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
            pair_capacity=2,
        )
        metadata = summary["metadata"]
        self.assertTrue(metadata["overflow"])
        self.assertFalse(metadata["complete_candidate_coverage"])
        self.assertEqual(metadata["status_column_values"]["row_count"], 2)
        self.assertEqual(metadata["status_column_values"]["capacity"], 2)
        self.assertTrue(metadata["status_column_values"]["overflow"])
        self.assertFalse(metadata["status_column_values"]["complete_candidate_coverage"])

    def test_validator_rejects_overflow_claiming_complete_coverage(self) -> None:
        summary = rt.build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
            pair_capacity=2,
        )
        summary["metadata"] = dict(summary["metadata"])
        summary["metadata"]["complete_candidate_coverage"] = True
        validation = rt.validate_v2_8_fixed_radius_partition_convergence_summary_same_contract_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
            candidate=summary,
        )
        self.assertEqual(validation["status"], "reject")
        self.assertIn("candidate complete_candidate_coverage mismatch", validation["errors"])
        self.assertIn("candidate overflow cannot claim complete_candidate_coverage", validation["errors"])

    def test_component_reference_surfaces_complete_coverage_boundary(self) -> None:
        complete = rt.build_v2_8_fixed_radius_partition_convergence_component_labels_reference_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
        )
        self.assertTrue(complete["metadata"]["complete_candidate_coverage"])

        overflow_summary = rt.build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
            pair_capacity=2,
        )
        incomplete = rt.build_v2_8_fixed_radius_partition_convergence_component_labels_reference_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
            partition_summary=overflow_summary,
        )
        self.assertEqual(incomplete["metadata"]["status"], "reject_partition_summary_overflow")
        self.assertFalse(incomplete["metadata"]["complete_candidate_coverage"])

    def test_source_and_report_document_status_fail_closed_boundary(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "complete_candidate_coverage",
            "status_column_values",
            "candidate overflow cannot claim complete_candidate_coverage",
            "fail closed",
            "does not add a native ABI",
            "does not authorize public speedup wording",
        ):
            self.assertIn(fragment, source + "\n" + report)


if __name__ == "__main__":
    unittest.main()
