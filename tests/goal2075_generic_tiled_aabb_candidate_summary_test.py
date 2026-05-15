from __future__ import annotations

import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
EXAMPLE = ROOT / "examples" / "rtdl_control_apps_cupy_rawkernel.py"
REPORT = ROOT / "docs" / "reports" / "goal2075_generic_tiled_aabb_candidate_summary_2026-05-15.md"


class Goal2075GenericTiledAabbCandidateSummaryTest(unittest.TestCase):
    def test_generic_tiled_aabb_candidate_payload_is_public(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")

        self.assertIn("def aabb_tiled_candidate_pair_payload_2d_partner_columns", adapters)
        self.assertIn("generic_tiled_aabb_candidate_pair_payload_2d", adapters)
        self.assertIn("bounded_materialization", adapters)
        self.assertIn("for left_start in range(0, left_count, tile_rows):", adapters)
        self.assertIn("for right_start in range(0, right_count, right_tile_rows):", adapters)
        self.assertIn("module.get_default_memory_pool().free_all_blocks()", adapters)
        self.assertIn("from .partner_adapters import aabb_tiled_candidate_pair_payload_2d_partner_columns", init_text)
        self.assertIn('"aabb_tiled_candidate_pair_payload_2d_partner_columns"', init_text)

    def test_polygon_cupy_extent_path_uses_generic_adapter(self) -> None:
        text = EXAMPLE.read_text(encoding="utf-8")

        self.assertIn("aabb_tiled_candidate_pair_payload_2d_partner_columns", text)
        self.assertIn('candidate_backend == "cupy_extent" and partner == "cupy"', text)
        self.assertIn("RTDL_CUPY_EXTENT_TILE_ROWS", text)
        self.assertIn("RTDL_CUPY_EXTENT_RIGHT_TILE_ROWS", text)
        self.assertIn("RTDL_CUPY_EXTENT_FREE_TILE_BLOCKS", text)
        self.assertNotIn("def _cupy_extent_candidate_indices", text)
        self.assertNotIn("POLYGON_EXTENT_RAWKERNEL_SOURCE", text)

    def test_generic_tiled_aabb_candidate_payload_torch_functional_edges(self) -> None:
        try:
            from rtdsl.partner_adapters import aabb_tiled_candidate_pair_payload_2d_partner_columns
        except Exception as exc:  # pragma: no cover - depends on optional torch install
            self.skipTest(f"partner adapter import unavailable: {exc}")

        try:
            import torch
        except Exception as exc:  # pragma: no cover - depends on optional torch install
            self.skipTest(f"torch unavailable: {exc}")

        left = {
            "min_x": [0, 5, 10],
            "min_y": [0, 5, 0],
            "max_x": [3, 7, 12],
            "max_y": [3, 7, 2],
            "area": [9, 4, 4],
        }
        right = {
            "min_x": [2, 3, 6, 20],
            "min_y": [2, 0, 6, 20],
            "max_x": [4, 5, 8, 22],
            "max_y": [4, 3, 8, 22],
            "area": [4, 0, 4, 4],
        }

        payload = aabb_tiled_candidate_pair_payload_2d_partner_columns(
            left,
            right,
            partner="torch",
            tile_rows=2,
            right_tile_rows=2,
        )

        pairs = set(
            zip(
                payload["left_index"].detach().cpu().tolist(),
                payload["right_index"].detach().cpu().tolist(),
            )
        )
        self.assertEqual({(0, 0), (1, 2)}, pairs)
        self.assertEqual("generic_tiled_aabb_candidate_pair_payload_2d", payload["_metadata"]["partner_reference_contract"])
        self.assertTrue(payload["_metadata"]["bounded_materialization"])
        self.assertFalse(payload["_metadata"]["v2_0_release_authorized"])
        self.assertEqual(torch.int32, payload["left_index"].dtype)

    def test_report_records_solution_and_pod_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("bounded candidate-summary", text)
        self.assertIn("generic partner primitive", text)
        self.assertIn("native RTDL engine remains app-agnostic", text)
        self.assertIn("fresh pod timing run is still required", text)
        self.assertIn("not arbitrary polygon overlay", text)
        self.assertIn("not reuse those ratios as release evidence", text)


if __name__ == "__main__":
    unittest.main()
