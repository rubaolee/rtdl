from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4045_partition_component_signature_preview_2026-06-08.md"


def _cupy_available() -> bool:
    return importlib.util.find_spec("cupy") is not None


@unittest.skipUnless(_cupy_available(), "CuPy is not available in this environment")
class Goal4045PartitionComponentSignaturePreviewRuntimeTest(unittest.TestCase):
    def test_component_signature_matches_full_labels(self) -> None:
        points = (
            (0.0, 0.0, 0.0),
            (0.2, 0.0, 0.0),
            (1.2, 0.0, 0.0),
            (1.5, 0.0, 0.0),
            (4.0, 0.0, 0.0),
        )
        signature = rt.build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d(
            points,
            radius=1.0,
            cell_factor=0.5,
            validate_against_component_labels=True,
        )
        labels = rt.build_v2_8_fixed_radius_partition_convergence_component_labels_cupy_preview_3d(
            points,
            radius=1.0,
            cell_factor=0.5,
            partition_union_execution="cupy_safe_full",
            ambiguous_union_execution="cupy_partition_points",
        )

        label_values = tuple(int(value) for value in labels["columns"]["component_labels"])
        expected = tuple(sorted(label_values.count(label) for label in set(label_values)))
        self.assertEqual(signature["metadata"]["status"], "accept")
        self.assertTrue(signature["metadata"]["same_contract_against_component_labels"])
        self.assertEqual(signature["columns"]["component_size_signature"], expected)
        self.assertEqual(signature["metadata"]["label_materialization"], "component_size_signature_only")
        self.assertFalse(signature["metadata"]["native_abi_added"])
        self.assertFalse(signature["metadata"]["automatic_partner_selection_allowed"])
        self.assertFalse(signature["metadata"]["public_speedup_claim_authorized"])

    def test_zero_ambiguous_signature_skips_device_classifier(self) -> None:
        points = (
            (0.0, 0.0, 0.0),
            (0.1, 0.0, 0.0),
            (4.0, 0.0, 0.0),
            (4.1, 0.0, 0.0),
        )
        result = rt.build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d(
            points,
            radius=1.0,
            cell_factor=0.5,
            validate_against_component_labels=True,
        )

        self.assertEqual(result["metadata"]["status"], "accept")
        self.assertFalse(result["metadata"]["device_ambiguous_union_used"])
        self.assertEqual(result["metadata"]["ambiguous_union_skipped_reason"], "no_ambiguous_partition_pairs")
        self.assertEqual(result["columns"]["component_size_signature"], (2, 2))


class Goal4045PartitionComponentSignaturePreviewSourceTest(unittest.TestCase):
    def test_source_and_report_record_generic_signature_preview(self) -> None:
        text = SOURCE.read_text(encoding="utf-8") + "\n" + REPORT.read_text(encoding="utf-8")
        for fragment in (
            "build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d",
            "component_size_signature",
            "component_size_signature_only",
            "fixed-radius graph",
            "native ABI",
            "choose partners automatically",
            "public speedup wording",
        ):
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
