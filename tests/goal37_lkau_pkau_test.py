from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import rtdsl as rt


SAMPLE_PAYLOAD = {
    "elements": [
        {
            "type": "way",
            "id": 101,
            "geometry": [
                {"lat": -26.7, "lon": 153.0},
                {"lat": -26.7, "lon": 153.1},
                {"lat": -26.6, "lon": 153.1},
                {"lat": -26.7, "lon": 153.0},
            ],
        },
        {
            "type": "way",
            "id": 102,
            "geometry": [
                {"lat": -26.5, "lon": 153.0},
                {"lat": -26.5, "lon": 153.1},
                {"lat": -26.4, "lon": 153.1},
            ],
        },
        {
            "type": "relation",
            "id": 103,
            "geometry": [],
        },
    ]
}


class Goal37LkauPkauTest(unittest.TestCase):
    def test_overpass_elements_stats_counts_closed_ways(self) -> None:
        stats = rt.overpass_elements_stats(tuple(SAMPLE_PAYLOAD["elements"]))
        self.assertEqual(stats.element_count, 3)
        self.assertEqual(stats.polygon_like_count, 1)
        self.assertEqual(stats.closed_way_count, 1)
        self.assertEqual(stats.skipped_open_way_count, 0)
        self.assertEqual(stats.skipped_short_geometry_count, 1)
        self.assertEqual(stats.skipped_non_way_count, 1)

    def test_overpass_elements_to_cdb_skips_non_closed_shapes(self) -> None:
        dataset = rt.overpass_elements_to_cdb(tuple(SAMPLE_PAYLOAD["elements"]), name="sample")
        self.assertEqual(dataset.face_ids(), (101,))
        self.assertEqual(len(dataset.chains), 1)
        chain = dataset.chains[0]
        self.assertEqual(chain.left_face_id, 101)
        self.assertEqual(chain.point_count, 4)
        self.assertAlmostEqual(chain.points[0].x, 153.0)
        self.assertAlmostEqual(chain.points[0].y, -26.7)

    def test_load_overpass_elements_reads_saved_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload_path = Path(temp_dir) / "parks.json"
            payload_path.write_text(json.dumps(SAMPLE_PAYLOAD), encoding="utf-8")
            elements = rt.load_overpass_elements(payload_path)
        self.assertEqual(len(elements), 3)
        self.assertEqual(elements[0]["id"], 101)


if __name__ == "__main__":
    unittest.main()
