from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

COUNTY_ZIPCODE_SCALE_BOUNDS = (-179.148909, 179.778465, -14.548692, 71.390482)


def _format_xy(row, prefix: str) -> str:
    return f"{row[prefix + '_x']:.6f} {row[prefix + '_y']:.6f}"


class Goal4866RayjoinSection57OutputContractTest(unittest.TestCase):
    def _row_for_segments(self, left, right):
        from rtdsl.rayjoin_overlay import _rows_from_segment_pairs

        left_coords = tuple(np.asarray([value], dtype=np.float64) for value in left)
        right_coords = tuple(np.asarray([value], dtype=np.float64) for value in right)
        return _rows_from_segment_pairs(
            [[1, 1]],
            None,
            None,
            left_coords=left_coords,
            right_coords=right_coords,
            scale_bounds=COUNTY_ZIPCODE_SCALE_BOUNDS,
        )[0]

    def test_xsect_display_uses_author_internal_integer_path_not_endpoint_world_snap(self):
        row = self._row_for_segments(
            (-83.848725, 33.989941, -83.848772, 33.989988),
            (-83.848538, 33.989855, -83.8487335, 33.9899495),
        )

        self.assertEqual(
            "-83.848733 33.989949",
            _format_xy(row, "intersection_display_point"),
        )
        self.assertEqual(
            "-83.848733 33.989949",
            _format_xy(row, "intersection_point"),
        )

    def test_xsect_display_preserves_author_endpoint_like_negative_case(self):
        row = self._row_for_segments(
            (-86.684974, 34.08009, -86.684859, 34.080196),
            (-86.6850297, 34.0800418, -86.6849395, 34.0801218),
        )

        self.assertEqual(
            "-86.684939 34.080122",
            _format_xy(row, "intersection_display_point"),
        )
        self.assertEqual(
            "-86.684940 34.080122",
            _format_xy(row, "intersection_point"),
        )

    def test_xsect_display_handles_negative_half_boundary_segment_case(self):
        row = self._row_for_segments(
            (-75.054387, 38.486999, -75.054504, 38.487142),
            (-75.054434, 38.487059, -75.05456, 38.487185),
        )

        self.assertEqual(
            "-75.054445 38.487071",
            _format_xy(row, "intersection_display_point"),
        )
        self.assertEqual(
            "-75.054446 38.487071",
            _format_xy(row, "intersection_point"),
        )

    def test_streaming_writer_matches_materialized_writer_on_tiny_overlay(self):
        from rtdsl.datasets import CdbChain
        from rtdsl.datasets import CdbDataset
        from rtdsl.datasets import CdbPoint
        from rtdsl.rayjoin_overlay import RayjoinOverlayIntersection
        from rtdsl.rayjoin_overlay import _assemble_output_chains
        from rtdsl.rayjoin_overlay import _write_output_chains_streaming
        from rtdsl.rayjoin_overlay import write_output_chains

        map0 = CdbDataset(
            name="map0",
            chains=(
                CdbChain(
                    chain_id=1,
                    point_count=2,
                    first_point_id=1,
                    last_point_id=2,
                    left_face_id=10,
                    right_face_id=0,
                    points=(CdbPoint(0.0, 0.0), CdbPoint(2.0, 0.0)),
                ),
            ),
        )
        map1 = CdbDataset(
            name="map1",
            chains=(
                CdbChain(
                    chain_id=1,
                    point_count=2,
                    first_point_id=1,
                    last_point_id=2,
                    left_face_id=20,
                    right_face_id=0,
                    points=(CdbPoint(1.0, -1.0), CdbPoint(1.0, 1.0)),
                ),
            ),
        )
        xsect = RayjoinOverlayIntersection(
            eid0=0,
            eid1=0,
            x=1.0,
            y=0.0,
            display_x=1.0,
            display_y=0.0,
        )

        chains, _ = _assemble_output_chains(
            (map0, map1),
            ([xsect], [xsect]),
            ([20, 20], [10, 10]),
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            materialized = root / "materialized.txt"
            streaming = root / "streaming.txt"
            write_output_chains(chains, materialized)
            stats = _write_output_chains_streaming(
                (map0, map1),
                ([xsect], [xsect]),
                ([20, 20], [10, 10]),
                streaming,
            )

            self.assertEqual(materialized.read_text(encoding="utf-8"), streaming.read_text(encoding="utf-8"))
            self.assertEqual(len(chains), stats["chain_count"])
            self.assertGreaterEqual(stats["face_count"], 1)
            self.assertEqual(
                sum(len(chain.points) for chain in chains),
                stats["point_count"],
            )


if __name__ == "__main__":
    unittest.main()
