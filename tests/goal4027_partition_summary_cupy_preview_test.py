from __future__ import annotations

import importlib.util
import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4027_partition_summary_cupy_preview_2026-06-08.md"


def _cupy_available() -> bool:
    return importlib.util.find_spec("cupy") is not None


@unittest.skipUnless(_cupy_available(), "CuPy is not available in this environment")
class Goal4027PartitionSummaryCupyPreviewTest(unittest.TestCase):
    def _points(self):
        return (
            (0.0, 0.0, 0.0),
            (0.2, 0.0, 0.0),
            (1.2, 0.0, 0.0),
            (1.5, 0.0, 0.0),
        )

    def test_cupy_preview_matches_reference_summary_and_component_labels(self) -> None:
        candidate = rt.build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
        )
        validation = rt.validate_v2_8_fixed_radius_partition_convergence_summary_same_contract_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
            candidate=candidate,
            float_abs_tol=1.0e-5,
        )
        self.assertEqual(validation["status"], "accept")
        self.assertTrue(candidate["metadata"]["device_partition_columns_used"])
        self.assertTrue(candidate["metadata"]["host_pair_enumeration_used"])
        self.assertTrue(candidate["metadata"]["runtime_executable"])
        self.assertFalse(candidate["metadata"]["native_abi_added"])
        self.assertFalse(candidate["metadata"]["public_speedup_claim_authorized"])

        component = rt.build_v2_8_fixed_radius_partition_convergence_component_labels_reference_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
            partition_summary=candidate,
        )
        self.assertEqual(component["metadata"]["status"], "accept")
        self.assertTrue(component["metadata"]["same_contract_against_all_pairs"])

    def test_cupy_preview_overflow_fails_closed(self) -> None:
        candidate = rt.build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(
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
            float_abs_tol=1.0e-5,
        )
        self.assertEqual(validation["status"], "accept")
        self.assertTrue(candidate["metadata"]["overflow"])
        self.assertFalse(candidate["metadata"]["complete_candidate_coverage"])
        component = rt.build_v2_8_fixed_radius_partition_convergence_component_labels_reference_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
            partition_summary=candidate,
        )
        self.assertEqual(component["metadata"]["status"], "reject_partition_summary_overflow")

    def test_cupy_device_pair_preview_matches_reference(self) -> None:
        reference = rt.build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
        )
        candidate = rt.build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
            pair_capacity=reference["metadata"]["pair_count"],
            pair_enumeration="device_bounded_offsets",
        )
        validation = rt.validate_v2_8_fixed_radius_partition_convergence_summary_same_contract_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
            candidate=candidate,
            float_abs_tol=1.0e-5,
        )
        self.assertEqual(validation["status"], "accept")
        self.assertTrue(candidate["metadata"]["device_pair_enumeration_used"])
        self.assertFalse(candidate["metadata"]["host_pair_enumeration_used"])
        component = rt.build_v2_8_fixed_radius_partition_convergence_component_labels_reference_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
            partition_summary=candidate,
        )
        self.assertEqual(component["metadata"]["status"], "accept")


class Goal4027PartitionSummaryCupyPreviewSourceTest(unittest.TestCase):
    def test_source_and_report_record_preview_boundary(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "build_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d",
            "device_partition_columns_used",
            "host_pair_enumeration_used",
            "device_pair_enumeration_used",
            "device_bounded_offsets",
            "not the final fast native producer",
            "does not add a native ABI",
            "does not authorize public speedup wording",
        ):
            self.assertIn(fragment, source + "\n" + report)


if __name__ == "__main__":
    unittest.main()
