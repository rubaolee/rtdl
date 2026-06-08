from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4019_partition_summary_same_contract_validator_2026-06-08.md"


class Goal4019PartitionSummarySameContractValidatorTest(unittest.TestCase):
    def _points(self):
        return (
            rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),
            rt.Point3D(id=2, x=0.2, y=0.0, z=0.0),
            rt.Point3D(id=3, x=1.2, y=0.0, z=0.0),
            rt.Point3D(id=4, x=3.0, y=0.0, z=0.0),
        )

    def test_reference_candidate_accepts_same_contract(self) -> None:
        candidate = rt.build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
        )
        validation = rt.validate_v2_8_fixed_radius_partition_convergence_summary_same_contract_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
            candidate=candidate,
        )
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["candidate_reference_contract"], "fixed_radius_partition_convergence_summary_3d_same_contract")
        self.assertEqual(validation["status_counts"]["safe_full_partition_pairs"], 3)
        self.assertEqual(validation["status_counts"]["ambiguous_partition_pairs"], 1)
        self.assertFalse(validation["release_authorized"])
        self.assertFalse(validation["public_speedup_claim_authorized"])

    def test_mismatched_candidate_column_rejects_with_column_name(self) -> None:
        candidate = rt.build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
        )
        candidate["columns"] = dict(candidate["columns"])
        candidate["columns"]["near_pair_status"] = (1, 1, 1, 1)
        validation = rt.validate_v2_8_fixed_radius_partition_convergence_summary_same_contract_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
            candidate=candidate,
        )
        self.assertEqual(validation["status"], "reject")
        self.assertIn("near_pair_status", validation["mismatch_columns"])
        self.assertIn("candidate column mismatch: near_pair_status", validation["errors"])

    def test_overflow_candidate_accepts_same_visible_contract(self) -> None:
        candidate = rt.build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
            pair_capacity=2,
        )
        validation = rt.validate_v2_8_fixed_radius_partition_convergence_summary_same_contract_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
            candidate=candidate,
        )
        self.assertEqual(validation["status"], "accept")
        self.assertTrue(validation["overflow"])
        self.assertEqual(validation["visible_pair_count"], 2)
        self.assertEqual(validation["pair_count"], 4)

    def test_candidate_claim_flags_fail_closed(self) -> None:
        candidate = rt.build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
        )
        candidate["metadata"] = dict(candidate["metadata"])
        candidate["metadata"]["release_authorized"] = True
        validation = rt.validate_v2_8_fixed_radius_partition_convergence_summary_same_contract_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
            candidate=candidate,
        )
        self.assertEqual(validation["status"], "reject")
        self.assertIn("candidate metadata must not authorize release_authorized", validation["errors"])

    def test_source_and_report_document_native_producer_gate(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "validate_v2_8_fixed_radius_partition_convergence_summary_same_contract_3d",
            "fixed_radius_partition_convergence_summary_3d_same_contract",
            "future native producer",
            "does not add a native ABI",
            "does not authorize public speedup wording",
        ):
            self.assertIn(fragment, source + "\n" + report)


if __name__ == "__main__":
    unittest.main()
