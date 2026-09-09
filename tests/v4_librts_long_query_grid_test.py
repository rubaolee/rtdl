from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

import numpy as np

from experiments.v4_librts_long_workload.query_grid import (
    generate_query_grid,
    load_query_columns,
    point_grid_oracle,
    range_grid_oracle,
)
from scripts.v4_librts_long_c_only_calibrate import validate_candidates


class V4LibRTSLongQueryGridTest(unittest.TestCase):
    def setUp(self) -> None:
        self.indexed = {
            "min_x": np.asarray([0.0, 1.0], dtype=np.float32),
            "min_y": np.asarray([0.0, 1.0], dtype=np.float32),
            "max_x": np.asarray([1.0, 3.0], dtype=np.float32),
            "max_y": np.asarray([1.0, 3.0], dtype=np.float32),
        }

    def test_point_oracle_matches_brute_force(self) -> None:
        x = np.asarray([0.5, 1.0, 2.0], dtype=np.float32)
        y = np.asarray([0.5, 1.0, 2.0], dtype=np.float32)
        brute = 0
        for query_y in y:
            for query_x in x:
                brute += sum(
                    minimum_x <= query_x <= maximum_x
                    and minimum_y <= query_y <= maximum_y
                    for minimum_x, minimum_y, maximum_x, maximum_y in zip(
                        self.indexed["min_x"], self.indexed["min_y"],
                        self.indexed["max_x"], self.indexed["max_y"],
                    )
                )
        self.assertEqual(brute, point_grid_oracle(self.indexed, x, y))

    def test_range_oracle_matches_brute_force(self) -> None:
        min_x = np.asarray([0.2, 1.2], dtype=np.float32)
        max_x = np.asarray([0.8, 1.8], dtype=np.float32)
        min_y = np.asarray([0.2, 1.2], dtype=np.float32)
        max_y = np.asarray([0.8, 1.8], dtype=np.float32)
        brute = 0
        for yi in range(min_y.size):
            for xi in range(min_x.size):
                brute += sum(
                    box_min_x <= min_x[xi] and box_min_y <= min_y[yi]
                    and box_max_x >= max_x[xi] and box_max_y >= max_y[yi]
                    for box_min_x, box_min_y, box_max_x, box_max_y in zip(
                        self.indexed["min_x"], self.indexed["min_y"],
                        self.indexed["max_x"], self.indexed["max_y"],
                    )
                )
        self.assertEqual(
            brute,
            range_grid_oracle(self.indexed, min_x, max_x, min_y, max_y),
        )

    def test_generation_is_distinct_and_digest_checked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "points.wkt"
            source.write_text(
                "POINT (0.25 0.25)\nPOINT (1.0 1.0)\nPOINT (2.0 2.0)\n",
                encoding="utf-8",
            )
            output = root / "generated"
            manifest = generate_query_grid(
                indexed=self.indexed,
                source_query_path=source,
                operation="point_contains",
                x_count=3,
                y_count=3,
                output=output,
                indexed_identity={"indexed_npz_sha256": "0" * 64},
            )
            columns, loaded = load_query_columns(output / "MANIFEST.json")
            self.assertEqual(9, manifest["query_count"])
            self.assertEqual(manifest, loaded)
            self.assertEqual(9, len(set(zip(columns["x"], columns["y"]))))
            brute = sum(
                box_min_x <= query_x <= box_max_x
                and box_min_y <= query_y <= box_max_y
                for query_x, query_y in zip(columns["x"], columns["y"])
                for box_min_x, box_min_y, box_max_x, box_max_y in zip(
                    self.indexed["min_x"], self.indexed["min_y"],
                    self.indexed["max_x"], self.indexed["max_y"],
                )
            )
            self.assertEqual(brute, manifest["expected_count_u64"])
            self.assertEqual("0" * 64, manifest["indexed_identity"]["indexed_npz_sha256"])

    def test_range_generation_matches_brute_force(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "ranges.wkt"
            source.write_text(
                "POLYGON ((0.2 0.2, 0.8 0.2, 0.8 0.8, 0.2 0.8, 0.2 0.2))\n"
                "POLYGON ((1.2 1.2, 1.8 1.2, 1.8 1.8, 1.2 1.8, 1.2 1.2))\n"
                "POLYGON ((2.0 2.0, 2.4 2.0, 2.4 2.4, 2.0 2.4, 2.0 2.0))\n",
                encoding="utf-8",
            )
            output = root / "generated"
            manifest = generate_query_grid(
                indexed=self.indexed,
                source_query_path=source,
                operation="range_contains",
                x_count=3,
                y_count=3,
                output=output,
            )
            columns, _ = load_query_columns(output / "MANIFEST.json")
            query_rows = set(zip(
                columns["min_x"], columns["min_y"],
                columns["max_x"], columns["max_y"],
            ))
            self.assertEqual(9, len(query_rows))
            brute = sum(
                box_min_x <= query_min_x and box_min_y <= query_min_y
                and box_max_x >= query_max_x and box_max_y >= query_max_y
                for query_min_x, query_min_y, query_max_x, query_max_y in query_rows
                for box_min_x, box_min_y, box_max_x, box_max_y in zip(
                    self.indexed["min_x"], self.indexed["min_y"],
                    self.indexed["max_x"], self.indexed["max_y"],
                )
            )
            self.assertEqual(brute, manifest["expected_count_u64"])

    def test_generation_rejects_u32_launch_overflow_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "points.wkt"
            source.write_text("POINT (0 0)\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "U32 OptiX launch"):
                generate_query_grid(
                    indexed=self.indexed,
                    source_query_path=source,
                    operation="point_contains",
                    x_count=65536,
                    y_count=65536,
                    output=root / "overflow",
                )

    def test_c_only_calibration_validates_candidate_order_and_column_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "points.wkt"
            source.write_text(
                "POINT (0.25 0.25)\nPOINT (1.0 1.0)\nPOINT (2.0 2.0)\n",
                encoding="utf-8",
            )
            manifests = []
            for axis_count in (2, 3):
                output = root / f"generated-{axis_count}"
                generate_query_grid(
                    indexed=self.indexed,
                    source_query_path=source,
                    operation="point_contains",
                    x_count=axis_count,
                    y_count=axis_count,
                    output=output,
                    indexed_identity={"indexed_npz_sha256": "0" * 64},
                )
                manifests.append(output / "MANIFEST.json")
            candidates = validate_candidates(manifests, "point_contains")
            self.assertEqual([4, 9], [row["query_count"] for row in candidates])
            with self.assertRaisesRegex(ValueError, "invalid or unordered"):
                validate_candidates(list(reversed(manifests)), "point_contains")
            (manifests[0].parent / "x.npy").write_bytes(b"corrupt")
            with self.assertRaisesRegex(ValueError, "column differs"):
                validate_candidates(manifests, "point_contains")


if __name__ == "__main__":
    unittest.main()
