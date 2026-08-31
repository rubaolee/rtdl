from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4021_partition_convergence_component_reference_2026-06-08.md"


class Goal4021PartitionConvergenceComponentReferenceTest(unittest.TestCase):
    def _points(self):
        return (
            rt.Point3D(id=10, x=0.0, y=0.0, z=0.0),
            rt.Point3D(id=11, x=0.2, y=0.0, z=0.0),
            rt.Point3D(id=12, x=1.2, y=0.0, z=0.0),
            rt.Point3D(id=13, x=3.0, y=0.0, z=0.0),
        )

    def test_partition_convergence_reference_matches_all_pairs(self) -> None:
        result = rt.build_v2_8_fixed_radius_partition_convergence_component_labels_reference_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
        )
        self.assertEqual(result["metadata"]["status"], "accept")
        self.assertTrue(result["metadata"]["same_contract_against_all_pairs"])
        self.assertEqual(result["columns"]["point_ids"], (10, 11, 12, 13))
        self.assertEqual(result["columns"]["component_labels"], (0, 0, 0, 1))
        self.assertEqual(result["metadata"]["partition_pair_status_counts"]["safe_full_partition_pairs"], 3)
        self.assertEqual(result["metadata"]["partition_pair_status_counts"]["ambiguous_partition_pairs"], 1)
        self.assertFalse(result["metadata"]["release_authorized"])

    def test_corrupt_partition_summary_rejects_before_labels(self) -> None:
        summary = rt.build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
        )
        summary["columns"] = dict(summary["columns"])
        summary["columns"]["near_pair_status"] = (0, 0, 0, 0)
        result = rt.build_v2_8_fixed_radius_partition_convergence_component_labels_reference_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
            partition_summary=summary,
        )
        self.assertEqual(result["metadata"]["status"], "reject_partition_summary_mismatch")
        self.assertEqual(result["columns"]["component_labels"], ())
        self.assertIn("candidate column mismatch: near_pair_status", result["metadata"]["errors"])

    def test_overflow_partition_summary_fails_closed(self) -> None:
        summary = rt.build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
            pair_capacity=2,
        )
        result = rt.build_v2_8_fixed_radius_partition_convergence_component_labels_reference_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
            partition_summary=summary,
        )
        self.assertEqual(result["metadata"]["status"], "reject_partition_summary_overflow")
        self.assertTrue(result["metadata"]["overflow"])
        self.assertEqual(result["columns"]["component_labels"], ())
        self.assertFalse(result["metadata"]["public_speedup_claim_authorized"])

    def test_source_and_report_document_reference_boundary(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "build_v2_8_fixed_radius_partition_convergence_component_labels_reference_3d",
            "same_contract_against_all_pairs",
            "safe-full partition pairs",
            "ambiguous pairs",
            "does not add a native ABI",
            "does not authorize public speedup wording",
        ):
            self.assertIn(fragment, source + "\n" + report)


if __name__ == "__main__":
    unittest.main()
