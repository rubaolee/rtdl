from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
SCRIPT_DIR = APP / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import xhd_input_loader


GENERATED = APP / "data" / "generated" / "goal5303_arcgis_county_zcta_bounded"
MANIFEST = GENERATED / "manifest.json"


def _load_tmp_points(text: str, *, n_dims: int = 2) -> list[tuple[float, ...]]:
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "fixture.wkt"
        path.write_text(text, encoding="utf-8")
        return xhd_input_loader.load_wkt_points(path, n_dims=n_dims)


class Goal5305XhdWktAuthorLoaderSemanticsTest(unittest.TestCase):
    def test_point_and_linestring_vertices_are_emitted(self) -> None:
        points = _load_tmp_points(
            "\n".join(
                [
                    "POINT (1 2)",
                    "LINESTRING (0 0, 1 1, 2 2)",
                    "MULTILINESTRING ((3 3, 4 4), (5 5, 6 6))",
                ]
            )
        )
        self.assertEqual(
            points,
            [
                (1.0, 2.0),
                (0.0, 0.0),
                (1.0, 1.0),
                (2.0, 2.0),
                (3.0, 3.0),
                (4.0, 4.0),
                (5.0, 5.0),
                (6.0, 6.0),
            ],
        )

    def test_polygon_uses_outer_ring_only_and_preserves_closed_vertex(self) -> None:
        points = _load_tmp_points(
            "POLYGON ((0 0, 1 0, 1 1, 0 0), (9 9, 10 9, 9 9))\n"
        )
        self.assertEqual(points, [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 0.0)])

    def test_multipolygon_uses_each_outer_ring_only(self) -> None:
        points = _load_tmp_points(
            "MULTIPOLYGON (((0 0, 1 0, 0 0)), ((2 2, 3 2, 2 2), (8 8, 9 8, 8 8)))\n"
        )
        self.assertEqual(
            points,
            [(0.0, 0.0), (1.0, 0.0), (0.0, 0.0), (2.0, 2.0), (3.0, 2.0), (2.0, 2.0)],
        )

    def test_unsupported_or_dim_mismatched_wkt_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported X-HD WKT geometry type"):
            _load_tmp_points("GEOMETRYCOLLECTION (POINT (0 0))\n")
        with self.assertRaisesRegex(ValueError, "expected 2"):
            _load_tmp_points("POINT (0 0 0)\n", n_dims=2)
        with self.assertRaisesRegex(ValueError, "exactly one coordinate"):
            _load_tmp_points("POINT (0 0, 1 1)\n", n_dims=2)

    def test_goal5303_generated_fixture_counts_match_author_loader_estimates(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        for key in ("county", "zipcode"):
            with self.subTest(key=key):
                meta = manifest["outputs"][key]
                path = ROOT / pathlib.Path(meta["path"].replace("\\", "/"))
                points = xhd_input_loader.load_wkt_points(path, n_dims=2)
                self.assertEqual(len(points), meta["outer_ring_point_count_author_loader_estimate"])


if __name__ == "__main__":
    unittest.main()
