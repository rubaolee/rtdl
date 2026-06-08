from __future__ import annotations

import importlib.util
import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4035_partition_component_labels_cupy_preview_2026-06-08.md"


def _cupy_available() -> bool:
    return importlib.util.find_spec("cupy") is not None


@unittest.skipUnless(_cupy_available(), "CuPy is not available in this environment")
class Goal4035PartitionComponentLabelsCupyPreviewRuntimeTest(unittest.TestCase):
    def test_component_preview_matches_all_pairs_with_ambiguous_pair(self) -> None:
        points = (
            (0.0, 0.0, 0.0),
            (0.2, 0.0, 0.0),
            (1.2, 0.0, 0.0),
            (1.5, 0.0, 0.0),
            (4.0, 0.0, 0.0),
        )
        result = rt.build_v2_8_fixed_radius_partition_convergence_component_labels_cupy_preview_3d(
            points,
            radius=1.0,
            cell_factor=0.5,
            partition_union_execution="cupy_safe_full",
            validate_against_all_pairs=True,
        )
        self.assertEqual(result["metadata"]["status"], "accept")
        self.assertTrue(result["metadata"]["same_contract_against_all_pairs"])
        self.assertTrue(result["metadata"]["summary_same_contract_validation_enabled"])
        self.assertEqual(result["metadata"]["partition_summary_pair_enumeration"], "device_bounded_offsets")
        self.assertEqual(result["metadata"]["partition_union_execution"], "cupy_safe_full")
        self.assertEqual(result["metadata"]["partition_summary_pair_capacity_source"], "device_upper_bound")
        self.assertGreaterEqual(result["metadata"]["safe_full_partition_union_iterations"], 1)
        self.assertGreater(result["metadata"]["ambiguous_partition_pairs"], 0)
        self.assertFalse(result["metadata"]["native_abi_added"])
        self.assertFalse(result["metadata"]["public_speedup_claim_authorized"])
        self.assertFalse(result["metadata"]["automatic_partner_selection_allowed"])


class Goal4035PartitionComponentLabelsCupyPreviewSourceTest(unittest.TestCase):
    def test_source_and_report_record_component_preview_boundary(self) -> None:
        text = SOURCE.read_text(encoding="utf-8") + "\n" + REPORT.read_text(encoding="utf-8")
        for fragment in (
            "build_v2_8_fixed_radius_partition_convergence_component_labels_cupy_preview_3d",
            "safe_full",
            "ambiguous",
            "device_bounded_offsets",
            "cupy_safe_full",
            "device_upper_bound",
            "partition_union_execution",
            "validate_summary_same_contract",
            "not a promoted release route",
            "does not choose partners automatically",
        ):
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
