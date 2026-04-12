import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class Goal271V05KittiBoundedLoaderTest(unittest.TestCase):
    def _write_frame(self, path: Path, rows: tuple[tuple[float, float, float, float], ...]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = b"".join(struct.pack("<ffff", *row) for row in rows)
        path.write_bytes(payload)

    def test_loader_returns_point3d_records_from_manifest(self) -> None:
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
                max_points_per_frame=16,
                max_total_points=16,
            )
            package = rt.load_kitti_bounded_points_from_manifest(manifest)
            self.assertEqual(package.selected_frame_count, 1)
            self.assertEqual(package.selected_point_count, 2)
            self.assertEqual(package.points[0], rt.Point3D(id=1, x=1.0, y=2.0, z=3.0))
            self.assertEqual(package.points[1], rt.Point3D(id=2, x=4.0, y=5.0, z=6.0))

    def test_loader_applies_per_frame_and_total_caps_deterministically(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "source"
            self._write_frame(
                root / "0001" / "velodyne" / "000000.bin",
                (
                    (1.0, 0.0, 0.0, 0.0),
                    (2.0, 0.0, 0.0, 0.0),
                    (3.0, 0.0, 0.0, 0.0),
                ),
            )
            self._write_frame(
                root / "0001" / "velodyne" / "000001.bin",
                (
                    (4.0, 0.0, 0.0, 0.0),
                    (5.0, 0.0, 0.0, 0.0),
                    (6.0, 0.0, 0.0, 0.0),
                ),
            )
            manifest = rt.write_kitti_bounded_package_manifest(
                Path(tmpdir) / "manifest.json",
                source_root=root,
                max_frames=2,
                max_points_per_frame=2,
                max_total_points=3,
            )
            package = rt.load_kitti_bounded_points_from_manifest(manifest, point_id_start=10)
            self.assertEqual(package.selected_point_count, 3)
            self.assertEqual(tuple(point.id for point in package.points), (10, 11, 12))
            self.assertEqual(tuple(point.x for point in package.points), (1.0, 2.0, 4.0))

    def test_loader_rejects_invalid_frame_size_honestly(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "source"
            broken = root / "0001" / "velodyne" / "000000.bin"
            broken.parent.mkdir(parents=True, exist_ok=True)
            broken.write_bytes(b"\x00" * 5)
            manifest = rt.write_kitti_bounded_package_manifest(
                Path(tmpdir) / "manifest.json",
                source_root=root,
                max_frames=1,
            )
            with self.assertRaisesRegex(RuntimeError, "expected a multiple of 16"):
                rt.load_kitti_bounded_points_from_manifest(manifest)

    def test_loader_rejects_unknown_manifest_kind(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = Path(tmpdir) / "manifest.json"
            manifest.write_text('{"manifest_kind":"bad_kind"}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unsupported KITTI bounded package manifest kind"):
                rt.load_kitti_bounded_points_from_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
