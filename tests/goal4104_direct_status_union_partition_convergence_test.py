from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"


class Goal4104DirectStatusUnionPartitionConvergenceTest(unittest.TestCase):
    def test_direct_status_union_preview_is_exported_and_non_materializing(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")

        self.assertTrue(
            hasattr(
                rt,
                "build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_direct_status_union_preview_3d",
            )
        )
        self.assertIn("direct_partition_status_union_kernel", source)
        self.assertIn('"partition_summary_materialized": False', source)
        self.assertIn('"near_pair_columns_materialized": False', source)
        self.assertIn('"pair_order": "not_materialized_direct_status_scan"', source)
        self.assertIn('"native_abi_added": False', source)
        direct_section = source.split(
            "def build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_direct_status_union_preview_3d",
            1,
        )[1].split("def _cupy_union_partition_pairs_with_ambiguous_points", 1)[0]
        self.assertNotIn("dbscan", direct_section.lower())

    def test_direct_status_union_matches_materialized_signature_when_cupy_available(self) -> None:
        try:
            import cupy  # noqa: F401
        except Exception:
            self.skipTest("CuPy is not available in this local environment")

        points = [
            (0.00, 0.00, 0.00),
            (0.01, 0.00, 0.00),
            (0.02, 0.00, 0.00),
            (1.00, 1.00, 1.00),
            (1.01, 1.00, 1.00),
            (4.00, 4.00, 4.00),
        ]
        result = rt.build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_direct_status_union_preview_3d(
            points,
            radius=0.05,
            cell_factor=0.5,
            validate_against_materialized_signature=True,
        )
        metadata = result["metadata"]

        self.assertEqual(metadata["status"], "accept")
        self.assertTrue(metadata["same_contract_against_materialized_signature"])
        self.assertFalse(metadata["partition_summary_materialized"])
        self.assertFalse(metadata["near_pair_columns_materialized"])
        self.assertTrue(metadata["pair_materialization_avoided"])
        self.assertEqual(metadata["pair_enumeration"], "device_direct_status_union")
        self.assertEqual(metadata["pair_order"], "not_materialized_direct_status_scan")
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertFalse(metadata["whole_app_speedup_claim_authorized"])
        self.assertFalse(metadata["native_abi_added"])
        self.assertEqual(tuple(result["columns"]["component_size_signature"]), (1, 2, 3))


if __name__ == "__main__":
    unittest.main()
