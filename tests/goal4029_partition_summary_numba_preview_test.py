from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4029_partition_summary_numba_preview_2026-06-08.md"


def _numba_cuda_available() -> bool:
    try:
        from numba import cuda
    except Exception:
        return False
    try:
        return bool(cuda.is_available())
    except Exception:
        return False


@unittest.skipUnless(_numba_cuda_available(), "Numba CUDA is not available in this environment")
class Goal4029PartitionSummaryNumbaPreviewTest(unittest.TestCase):
    def _points(self):
        return (
            (0.0, 0.0, 0.0),
            (0.2, 0.0, 0.0),
            (1.2, 0.0, 0.0),
            (1.5, 0.0, 0.0),
        )

    def test_numba_preview_matches_reference_summary_and_component_labels(self) -> None:
        candidate = rt.build_v2_8_fixed_radius_partition_convergence_summary_numba_preview_3d(
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
        self.assertTrue(candidate["metadata"]["host_partition_summary_used"])
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

    def test_numba_preview_overflow_fails_closed(self) -> None:
        candidate = rt.build_v2_8_fixed_radius_partition_convergence_summary_numba_preview_3d(
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


class Goal4029PartitionSummaryNumbaPreviewSourceTest(unittest.TestCase):
    def test_source_and_report_record_preview_boundary(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "build_v2_8_fixed_radius_partition_convergence_summary_numba_preview_3d",
            "host_partition_summary_used",
            "numba_cuda_array_interface",
            "not the final fast native producer",
            "does not add a native ABI",
            "does not authorize public speedup wording",
        ):
            self.assertIn(fragment, source + "\n" + report)


if __name__ == "__main__":
    unittest.main()
