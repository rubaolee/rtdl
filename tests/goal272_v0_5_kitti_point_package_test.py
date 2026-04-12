import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class Goal272V05KittiPointPackageTest(unittest.TestCase):
    def _write_frame(self, path: Path, rows: tuple[tuple[float, float, float, float], ...]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"".join(struct.pack("<ffff", *row) for row in rows))

    def test_point_package_writer_materializes_portable_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "source"
            self._write_frame(
                root / "0001" / "velodyne" / "000000.bin",
                (
                    (1.0, 2.0, 3.0, 0.1),
                    (4.0, 5.0, 6.0, 0.2),
                ),
            )
            manifest = rt.write_kitti_bounded_package_manifest(
                Path(tmpdir) / "manifest.json",
                source_root=root,
                max_frames=1,
                max_points_per_frame=2,
                max_total_points=2,
            )
            package_path = rt.write_kitti_bounded_point_package(
                Path(tmpdir) / "package.json",
                manifest,
                point_id_start=100,
            )
            payload = json.loads(package_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["package_kind"], "kitti_bounded_point_package_v1")
            self.assertEqual(payload["selected_point_count"], 2)
            self.assertEqual(payload["point_id_start"], 100)
            self.assertEqual(payload["points"][0]["id"], 100)
            self.assertEqual(payload["points"][1]["z"], 6.0)

    def test_point_package_loader_round_trips_point_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "source"
            self._write_frame(
                root / "0001" / "velodyne" / "000000.bin",
                (
                    (9.0, 8.0, 7.0, 0.1),
                    (6.0, 5.0, 4.0, 0.2),
                ),
            )
            manifest = rt.write_kitti_bounded_package_manifest(
                Path(tmpdir) / "manifest.json",
                source_root=root,
                max_frames=1,
                max_points_per_frame=2,
                max_total_points=2,
            )
            package_path = rt.write_kitti_bounded_point_package(Path(tmpdir) / "package.json", manifest)
            package = rt.load_kitti_bounded_point_package(package_path)
            self.assertEqual(package.selected_point_count, 2)
            self.assertEqual(
                package.points,
                (
                    rt.Point3D(id=1, x=9.0, y=8.0, z=7.0),
                    rt.Point3D(id=2, x=6.0, y=5.0, z=4.0),
                ),
            )

    def test_point_package_loader_rejects_unknown_kind(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            package = Path(tmpdir) / "package.json"
            package.write_text('{"package_kind":"bad_kind"}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unsupported KITTI bounded point package kind"):
                rt.load_kitti_bounded_point_package(package)


if __name__ == "__main__":
    unittest.main()
