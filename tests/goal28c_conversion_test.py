import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class Goal28CConversionTest(unittest.TestCase):
    def test_arcgis_pages_to_cdb_converts_polygon_rings(self) -> None:
        payload = {
            "features": [
                {
                    "attributes": {"OBJECTID": 101},
                    "geometry": {
                        "rings": [
                            [[0.0, 0.0], [2.0, 0.0], [2.0, 2.0], [0.0, 0.0]],
                            [[5.0, 5.0], [6.0, 5.0], [5.0, 5.0]],
                        ]
                    },
                }
            ]
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            page_path = Path(tmpdir) / "page_000000.json.gz"
            with gzip.open(page_path, "wt", encoding="utf-8") as handle:
                json.dump(payload, handle)

            dataset = rt.arcgis_pages_to_cdb(tmpdir, name="arcgis_test")

        self.assertEqual(dataset.name, "arcgis_test")
        self.assertEqual(len(dataset.chains), 2)
        self.assertEqual(dataset.chains[0].left_face_id, 101)
        self.assertEqual(dataset.chains[0].point_count, 4)
        self.assertEqual(dataset.chains[1].first_point_id, 5)

    def test_chains_to_polygons_returns_vertices(self) -> None:
        dataset = rt.parse_cdb_text(
            "\n".join(
                [
                    "1 4 1 4 0 7",
                    "0 0",
                    "1 0",
                    "1 1",
                    "0 0",
                ]
            ),
            name="mini",
        )
        polygons = rt.chains_to_polygons(dataset)
        self.assertEqual(len(polygons), 1)
        self.assertEqual(polygons[0]["id"], 1)
        self.assertEqual(len(polygons[0]["vertices"]), 4)

    def test_arcgis_loader_can_ignore_invalid_tail_page(self) -> None:
        payload = {
            "features": [
                {
                    "attributes": {"OBJECTID": 1},
                    "geometry": {"rings": [[[0.0, 0.0], [1.0, 0.0], [0.0, 0.0]]]},
                }
            ]
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            good = Path(tmpdir) / "page_000000.json.gz"
            bad = Path(tmpdir) / "page_000250.json.gz"
            with gzip.open(good, "wt", encoding="utf-8") as handle:
                json.dump(payload, handle)
            bad.write_bytes(b"not-a-valid-gzip-json")

            dataset = rt.arcgis_pages_to_cdb(tmpdir, name="tail_ok", ignore_invalid_tail=True)
            page_count = rt.count_arcgis_loaded_pages(tmpdir, ignore_invalid_tail=True)

        self.assertEqual(len(dataset.chains), 1)
        self.assertEqual(page_count, 1)

    def test_arcgis_loader_merges_json_and_gz_pages_in_page_order(self) -> None:
        payload_a = {
            "features": [
                {
                    "attributes": {"OBJECTID": 10},
                    "geometry": {"rings": [[[0.0, 0.0], [1.0, 0.0], [0.0, 0.0]]]},
                }
            ]
        }
        payload_b = {
            "features": [
                {
                    "attributes": {"OBJECTID": 20},
                    "geometry": {"rings": [[[2.0, 0.0], [3.0, 0.0], [2.0, 0.0]]]},
                }
            ]
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            plain = Path(tmpdir) / "page_000250.json"
            gz = Path(tmpdir) / "page_000000.json.gz"
            plain.write_text(json.dumps(payload_b), encoding="utf-8")
            with gzip.open(gz, "wt", encoding="utf-8") as handle:
                json.dump(payload_a, handle)
            dataset = rt.arcgis_pages_to_cdb(tmpdir, name="ordered")

        self.assertEqual([chain.left_face_id for chain in dataset.chains], [10, 20])

    def test_arcgis_converter_skips_two_point_degenerate_ring(self) -> None:
        payload = {
            "features": [
                {
                    "attributes": {"OBJECTID": 7},
                    "geometry": {"rings": [[[0.0, 0.0], [1.0, 1.0]]]},
                }
            ]
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            page_path = Path(tmpdir) / "page_000000.json"
            page_path.write_text(json.dumps(payload), encoding="utf-8")
            dataset = rt.arcgis_pages_to_cdb(tmpdir, name="degenerate")

        self.assertEqual(len(dataset.chains), 0)


if __name__ == "__main__":
    unittest.main()
