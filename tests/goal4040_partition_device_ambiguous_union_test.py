from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4040_partition_device_ambiguous_union_2026-06-08.md"


def _cupy_available() -> bool:
    return importlib.util.find_spec("cupy") is not None


class Goal4040PartitionDeviceAmbiguousUnionContractTest(unittest.TestCase):
    def test_partition_summary_contract_includes_point_ordinals(self) -> None:
        contract = rt.make_v2_8_fixed_radius_partition_convergence_summary_typed_stream_contract(
            32,
            8,
            64,
        )
        metadata = contract.to_metadata()
        self.assertIn("partition_point_ordinals", metadata["column_names"])
        self.assertEqual(contract.column("partition_point_ordinals").buffer.shape, (32,))

        summary = rt.build_v2_8_fixed_radius_partition_convergence_summary_reference_3d(
            (
                rt.Point3D(id=10, x=0.0, y=0.0, z=0.0),
                rt.Point3D(id=11, x=0.2, y=0.0, z=0.0),
                rt.Point3D(id=12, x=1.2, y=0.0, z=0.0),
                rt.Point3D(id=13, x=3.0, y=0.0, z=0.0),
            ),
            radius=1.0,
            cell_factor=0.5,
        )
        self.assertEqual(summary["columns"]["partition_point_ordinals"], (0, 1, 2, 3))
        self.assertIn("Goal4040", rt.plan_v2_8_fixed_radius_graph_component_continuation(
            point_count=32,
            radius=1.0,
            component_threshold=1,
            strategy="partition_convergence_hybrid",
        )["candidate_strategy_evidence_goals"])


@unittest.skipUnless(_cupy_available(), "CuPy is not available in this environment")
class Goal4040PartitionDeviceAmbiguousUnionRuntimeTest(unittest.TestCase):
    def test_device_ambiguous_union_matches_all_pairs(self) -> None:
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
            ambiguous_union_execution="cupy_partition_points",
            validate_against_all_pairs=True,
        )

        self.assertEqual(result["metadata"]["status"], "accept")
        self.assertTrue(result["metadata"]["same_contract_against_all_pairs"])
        self.assertTrue(result["metadata"]["device_ambiguous_union_used"])
        self.assertGreater(result["metadata"]["ambiguous_partition_pairs"], 0)
        self.assertGreater(result["metadata"]["ambiguous_point_comparisons"], 0)
        self.assertGreater(result["metadata"]["ambiguous_positive_edges"], 0)
        self.assertFalse(result["metadata"]["native_abi_added"])
        self.assertFalse(result["metadata"]["automatic_partner_selection_allowed"])
        self.assertFalse(result["metadata"]["public_speedup_claim_authorized"])

    def test_invalid_mode_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires cupy_safe_full"):
            rt.build_v2_8_fixed_radius_partition_convergence_component_labels_cupy_preview_3d(
                ((0.0, 0.0, 0.0),),
                radius=1.0,
                ambiguous_union_execution="cupy_partition_points",
            )


class Goal4040PartitionDeviceAmbiguousUnionSourceTest(unittest.TestCase):
    def test_source_and_report_record_boundaries(self) -> None:
        text = SOURCE.read_text(encoding="utf-8") + "\n" + REPORT.read_text(encoding="utf-8")
        for fragment in (
            "partition_point_ordinals",
            "ambiguous_union_execution",
            "cupy_partition_points",
            "fixed-radius partition summary plus component-label continuation",
            "does not add a native ABI",
            "does not choose partners automatically",
            "does not authorize public speedup wording",
        ):
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
