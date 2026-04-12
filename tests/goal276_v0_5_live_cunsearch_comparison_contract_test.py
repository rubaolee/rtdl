import json
import stat
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class Goal276V05LiveCuNSearchComparisonContractTest(unittest.TestCase):
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

    def test_live_comparison_reuses_offline_harness_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            query_package = self._write_package(
                tmpdir / "query_source",
                tmpdir,
                "000000",
                ((0.0, 0.0, 0.0, 0.1),),
            )
            search_package = self._write_package(
                tmpdir / "search_source",
                tmpdir,
                "000001",
                ((0.0, 0.0, 0.2, 0.1),),
            )

            request = tmpdir / "request.json"
            response = tmpdir / "response.json"
            binary = tmpdir / "demo"
            binary.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            binary.chmod(binary.stat().st_mode | stat.S_IXUSR)

            # Instead of executing the live driver in unit tests, mimic the already-validated
            # response contract and verify the comparison result shape and message discipline.
            rt.write_cunsearch_fixed_radius_request(
                request,
                query_points=(rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),),
                search_points=(rt.Point3D(id=1, x=0.0, y=0.0, z=0.2),),
                radius=0.5,
                k_max=4,
                binary_path=binary,
            )
            response.write_text(
                json.dumps(
                    {
                        "adapter": "cunsearch",
                        "response_format": "json_rows_v1",
                        "workload": "fixed_radius_neighbors",
                        "rows": [{"query_id": 1, "neighbor_id": 1, "distance": 0.2}],
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
            self.assertTrue(result.parity_ok)
            self.assertEqual(result.reference_row_count, 1)


if __name__ == "__main__":
    unittest.main()
