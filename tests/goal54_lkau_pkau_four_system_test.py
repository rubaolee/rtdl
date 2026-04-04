from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "goal54_lkau_pkau_four_system.py"
SPEC = importlib.util.spec_from_file_location("goal54_lkau_pkau_four_system", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Goal54LkauPkauFourSystemTest(unittest.TestCase):
    def test_polygon_wkt_closes_ring(self) -> None:
        wkt = MODULE.polygon_wkt(((0.0, 0.0), (1.0, 0.0), (1.0, 1.0)))
        self.assertEqual(wkt, "POLYGON((0.0 0.0,1.0 0.0,1.0 1.0,0.0 0.0))")

    def test_parse_args_defaults(self) -> None:
        ns = MODULE.parse_args.__wrapped__ if hasattr(MODULE.parse_args, "__wrapped__") else None
        self.assertIsNone(ns)

    def test_render_markdown_mentions_boundaries(self) -> None:
        summary = {
            "host_label": "192.168.1.20",
            "bbox_label": "sunshine_tiny",
            "bbox": "-26.72,152.95,-26.55,153.10",
            "db_name": "rtdl_postgis",
            "compared_backends": ["cpu", "embree", "optix"],
            "load_sec": 1.0,
            "lakes": {"element_count": 280, "closed_way_count": 280, "feature_count": 280},
            "parks": {"element_count": 264, "closed_way_count": 264, "feature_count": 264},
            "lsi": {
                "postgis": {"row_count": 15},
                "postgis_sec": 0.1,
                "plan": {"uses_index": True},
                "cpu": {"sec": 1.0, "parity_vs_postgis": True},
                "embree": {"sec": 0.1, "parity_vs_postgis": True},
                "optix": {"sec": 0.2, "parity_vs_postgis": True},
            },
            "pip": {
                "postgis": {"row_count": 73920, "positive_row_count": 100},
                "postgis_sec": 0.2,
                "plan": {"uses_index": True},
                "cpu": {"sec": 1.0, "parity_vs_postgis": True},
                "embree": {"sec": 0.1, "parity_vs_postgis": True},
                "optix": {"sec": 0.2, "parity_vs_postgis": True},
            },
        }
        text = MODULE.render_markdown(summary)
        self.assertIn("bounded derived-input Australia slice", text)
        self.assertIn("not continent-scale", text)
        self.assertIn("PostGIS", text)

    def test_lsi_sql_uses_bbox_index_predicate(self) -> None:
        sql = MODULE.build_postgis_lsi_select_sql()
        self.assertIn("l.geom && r.geom", sql)

    def test_pip_sql_uses_bbox_and_covers(self) -> None:
        sql = MODULE.build_postgis_pip_select_sql()
        self.assertIn("g.geom && p.geom", sql)
        self.assertIn("ST_Covers(g.geom, p.geom)", sql)


if __name__ == "__main__":
    unittest.main()
