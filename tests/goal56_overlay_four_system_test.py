from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "goal56_overlay_four_system.py"
SPEC = importlib.util.spec_from_file_location("goal56_overlay_four_system", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Goal56OverlayFourSystemTest(unittest.TestCase):
    def test_polygon_wkt_closes_ring(self) -> None:
        wkt = MODULE.polygon_wkt(((0.0, 0.0), (1.0, 0.0), (1.0, 1.0)))
        self.assertEqual(wkt, "POLYGON((0.0 0.0,1.0 0.0,1.0 1.0,0.0 0.0))")

    def test_overlay_lsi_sql_uses_bbox_index_predicate(self) -> None:
        sql = MODULE.build_overlay_lsi_positive_sql()
        self.assertIn("l.geom && r.geom", sql)

    def test_overlay_pip_sql_uses_bbox_and_covers(self) -> None:
        sql = MODULE.build_overlay_pip_positive_sql()
        self.assertIn("g.geom && p.geom", sql)
        self.assertIn("ST_Covers", sql)

    def test_render_markdown_mentions_seed_analogue_boundary(self) -> None:
        summary = {
            "host_label": "192.168.1.20",
            "bbox_label": "sunshine_tiny",
            "bbox": "-26.72,152.95,-26.55,153.10",
            "db_name": "rtdl_postgis",
            "compared_backends": ["cpu", "embree", "optix"],
            "load_sec": 1.0,
            "lakes": {"element_count": 280, "closed_way_count": 280, "feature_count": 280},
            "parks": {"element_count": 264, "closed_way_count": 264, "feature_count": 264},
            "overlay": {
                "postgis": {"row_count": 73920},
                "postgis_sec": 0.1,
                "lsi_plan": {"uses_index": True},
                "pip_plan": {"uses_index": True},
                "overlay_plan": {"uses_index": True},
                "cpu": {"sec": 1.0, "parity_vs_postgis": True},
                "embree": {"sec": 0.1, "parity_vs_postgis": True},
                "optix": {"sec": 0.2, "parity_vs_postgis": True},
            },
        }
        text = MODULE.render_markdown(summary)
        self.assertIn("overlay-seed analogue", text)
        self.assertIn("not continent-scale", text)
        self.assertIn("PostGIS", text)

    def test_overlay_quadruples_shape(self) -> None:
        rows = (
            {
                "left_polygon_id": 1,
                "right_polygon_id": 2,
                "requires_lsi": 1,
                "requires_pip": 0,
            },
        )
        self.assertEqual(MODULE.overlay_quadruples(rows), [(1, 2, 1, 0)])

    def test_backend_payload_uses_exact_row_hash_for_parity(self) -> None:
        rows = (
            {
                "left_polygon_id": 1,
                "right_polygon_id": 2,
                "requires_lsi": 0,
                "requires_pip": 1,
            },
            {
                "left_polygon_id": 3,
                "right_polygon_id": 4,
                "requires_lsi": 1,
                "requires_pip": 0,
            },
        )
        hashed = MODULE.hash_tuples(MODULE.overlay_quadruples(rows), presorted=False)
        payload = MODULE.backend_payload(
            rows,
            0.25,
            hashed["sha256"],
            hashed["row_count"],
        )
        self.assertTrue(payload["parity_vs_postgis"])
        self.assertEqual(payload["row_count"], 2)

    def test_overlay_seed_sql_joins_full_pair_matrix(self) -> None:
        sql = MODULE.build_overlay_seed_select_sql()
        self.assertIn("CROSS JOIN goal56.right_polygons", sql)
        self.assertIn("LEFT JOIN lsi_hits", sql)
        self.assertIn("LEFT JOIN pip_hits", sql)


if __name__ == "__main__":
    unittest.main()
