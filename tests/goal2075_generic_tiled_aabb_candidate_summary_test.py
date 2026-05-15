from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
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
        self.assertNotIn("POLYGON_EXTENT_RAWKERNEL_SOURCE", text)

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
