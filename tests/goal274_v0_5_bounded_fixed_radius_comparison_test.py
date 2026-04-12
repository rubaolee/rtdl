import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class Goal274V05BoundedFixedRadiusComparisonTest(unittest.TestCase):
    def _write_frame(self, path: Path, rows: tuple[tuple[float, float, float, float], ...]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"".join(struct.pack("<ffff", *row) for row in rows))

    def _write_package(self, root: Path, tmpdir: Path, frame_name: str, rows) -> Path:
        self._write_frame(root / "0001" / "velodyne" / f"{frame_name}.bin", rows)
        manifest = rt.write_kitti_bounded_package_manifest(
            tmpdir / f"{frame_name}_manifest.json",
            source_root=root,
            max_frames=1,
            max_points_per_frame=16,
            max_total_points=16,
        )
        return rt.write_kitti_bounded_point_package(tmpdir / f"{frame_name}_package.json", manifest)

    def test_comparison_result_reports_parity_when_rows_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            query_root = tmpdir / "query_source"
            search_root = tmpdir / "search_source"
            query_package = self._write_package(
                query_root,
                tmpdir,
                "000000",
                ((0.0, 0.0, 0.0, 0.1),),
            )
            search_package = self._write_package(
                search_root,
                tmpdir,
                "000001",
                (
                    (0.0, 0.0, 0.2, 0.1),
                    (2.0, 0.0, 0.0, 0.1),
                ),
            )
            response = tmpdir / "response.json"
            response.write_text(
                json.dumps(
                    {
                        "adapter": "cunsearch",
                        "response_format": "json_rows_v1",
                        "workload": "fixed_radius_neighbors",
                        "rows": [
                            {"query_id": 1, "neighbor_id": 1, "distance": 0.2},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = rt.compare_bounded_fixed_radius_from_packages(
                query_package_path=query_package,
                search_package_path=search_package,
                external_response_path=response,
                radius=0.5,
                k_max=4,
            )
            self.assertEqual(result.reference_row_count, 1)
            self.assertEqual(result.external_row_count, 1)
            self.assertTrue(result.parity_ok)

    def test_comparison_result_reports_non_parity_when_rows_differ(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            query_root = tmpdir / "query_source"
            search_root = tmpdir / "search_source"
            query_package = self._write_package(
                query_root,
                tmpdir,
                "000000",
                ((0.0, 0.0, 0.0, 0.1),),
            )
            search_package = self._write_package(
                search_root,
                tmpdir,
                "000001",
                ((0.0, 0.0, 0.2, 0.1),),
            )
            response = tmpdir / "response.json"
            response.write_text(
                json.dumps(
                    {
                        "adapter": "cunsearch",
                        "response_format": "json_rows_v1",
                        "workload": "fixed_radius_neighbors",
                        "rows": [],
                    }
                ),
                encoding="utf-8",
            )
            result = rt.compare_bounded_fixed_radius_from_packages(
                query_package_path=query_package,
                search_package_path=search_package,
                external_response_path=response,
                radius=0.5,
                k_max=4,
            )
            self.assertFalse(result.parity_ok)


if __name__ == "__main__":
    unittest.main()
