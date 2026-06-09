from __future__ import annotations

import importlib.util
import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"


def _cupy_available() -> bool:
    return importlib.util.find_spec("cupy") is not None


class Goal4107PreparedDirectStatusUnionSourceTest(unittest.TestCase):
    def test_public_surface_and_non_materializing_boundary_are_present(self) -> None:
        for name in (
            "V28PreparedFixedRadiusPartitionConvergenceDirectStatusUnionCupyPreview3D",
            "prepare_v2_8_fixed_radius_partition_convergence_direct_status_union_cupy_preview_3d",
            "run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_direct_status_union_preview_3d",
        ):
            self.assertTrue(hasattr(rt, name), name)

        source = SOURCE.read_text(encoding="utf-8")
        start = source.index("def _prepare_direct_status_union_runtime_columns_cupy_3d")
        end = source.index("def build_v2_8_fixed_radius_partition_convergence_summary_numba_preview_3d")
        section = source[start:end].lower()

        self.assertNotIn("dbscan", section)
        self.assertNotIn("cluster", section)
        for fragment in (
            "prepared_direct_status_union_handle",
            "prepared_direct_status_runtime_columns",
            '"near_pair_columns_materialized": False',
            '"partition_pair_rows_materialized": False',
            '"pair_materialization_avoided": True',
            '"partition_convergence_hybrid_promoted": False',
            '"automatic_partner_selection_allowed": False',
            '"true_zero_copy_claim_authorized": False',
        ):
            self.assertIn(fragment.lower(), section)


@unittest.skipUnless(_cupy_available(), "CuPy is not available in this environment")
class Goal4107PreparedDirectStatusUnionRuntimeTest(unittest.TestCase):
    def _points(self):
        return (
            (0.0, 0.0, 0.0),
            (0.01, 0.0, 0.0),
            (0.02, 0.0, 0.0),
            (1.0, 1.0, 1.0),
            (1.01, 1.0, 1.0),
            (4.0, 4.0, 4.0),
        )

    def test_prepared_direct_status_reuses_columns_and_matches_materialized_signature(self) -> None:
        prepared = rt.prepare_v2_8_fixed_radius_partition_convergence_direct_status_union_cupy_preview_3d(
            self._points(),
            radius=0.05,
            cell_factor=0.5,
        )

        handle_metadata = prepared.to_metadata()
        self.assertTrue(handle_metadata["prepared_direct_status_union_handle"])
        self.assertFalse(handle_metadata["near_pair_columns_materialized"])
        self.assertFalse(handle_metadata["partition_pair_rows_materialized"])
        self.assertTrue(handle_metadata["pair_materialization_avoided"])
        self.assertFalse(handle_metadata["partition_convergence_hybrid_promoted"])
        self.assertFalse(handle_metadata["release_authorized"])
        self.assertFalse(handle_metadata["automatic_partner_selection_allowed"])

        result = rt.run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_direct_status_union_preview_3d(
            prepared,
            validate_against_materialized_signature=True,
        )
        metadata = result["metadata"]

        self.assertEqual(metadata["status"], "accept")
        self.assertEqual(tuple(result["columns"]["component_size_signature"]), (1, 2, 3))
        self.assertTrue(metadata["same_contract_against_materialized_signature"])
        self.assertTrue(metadata["prepared_direct_status_union_reused"])
        self.assertTrue(metadata["prepared_direct_status_runtime_columns_reused"])
        self.assertTrue(metadata["point_coordinate_columns_reused"])
        self.assertFalse(metadata["near_pair_columns_materialized"])
        self.assertFalse(metadata["partition_pair_rows_materialized"])
        self.assertTrue(metadata["pair_materialization_avoided"])
        self.assertEqual(metadata["prepared_direct_status_union_run_index"], 1)
        self.assertEqual(prepared.component_signature_runs, 1)

        prepared.close()
        with self.assertRaisesRegex(RuntimeError, "closed"):
            prepared.run_component_signature()


if __name__ == "__main__":
    unittest.main()
