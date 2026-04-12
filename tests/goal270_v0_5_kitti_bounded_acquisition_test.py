import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class Goal270V05KittiBoundedAcquisitionTest(unittest.TestCase):
    def _make_kitti_tree(self, root: Path) -> None:
        for sequence, frames in {
            "0001": ("000000", "000001", "000002"),
            "0002": ("000000", "000001"),
        }.items():
            velodyne = root / sequence / "velodyne"
            velodyne.mkdir(parents=True, exist_ok=True)
            for frame_id in frames:
                (velodyne / f"{frame_id}.bin").write_bytes(b"\x00" * 16)

    def test_source_config_reports_planned_when_unconfigured(self) -> None:
        old = os.environ.pop("RTDL_KITTI_SOURCE_ROOT", None)
        try:
            config = rt.kitti_source_config()
            self.assertEqual(config.current_status, "planned")
            self.assertIn("Linux host", config.notes)
        finally:
            if old is not None:
                os.environ["RTDL_KITTI_SOURCE_ROOT"] = old

    def test_discover_frames_returns_stable_sorted_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._make_kitti_tree(root)
            records = rt.discover_kitti_velodyne_frames(root)
            self.assertEqual(len(records), 5)
            self.assertEqual(records[0].sequence, "0001")
            self.assertEqual(records[0].frame_id, "000000")
            self.assertEqual(records[-1].sequence, "0002")
            self.assertEqual(records[-1].frame_id, "000001")

    def test_bounded_selection_obeys_stride_and_max_frames(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._make_kitti_tree(root)
            selected = rt.select_kitti_bounded_frames(source_root=root, max_frames=2, stride=2)
            self.assertEqual(len(selected), 2)
            self.assertEqual(
                tuple((record.sequence, record.frame_id) for record in selected),
                (("0001", "000000"), ("0001", "000002")),
            )

    def test_manifest_writer_emits_selected_frames_and_point_caps(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "source"
            self._make_kitti_tree(root)
            manifest = Path(tmpdir) / "kitti_manifest.json"
            written = rt.write_kitti_bounded_package_manifest(
                manifest,
                source_root=root,
                max_frames=3,
                stride=1,
                max_points_per_frame=128,
                max_total_points=1024,
            )
            payload = json.loads(written.read_text(encoding="utf-8"))
            self.assertEqual(payload["manifest_kind"], "kitti_bounded_package_manifest_v1")
            self.assertEqual(payload["selected_frame_count"], 3)
            self.assertEqual(payload["frames"][0]["sequence"], "0001")
            self.assertEqual(payload["max_points_per_frame"], 128)
            self.assertEqual(payload["max_total_points"], 1024)

    def test_unconfigured_source_root_fails_honestly(self) -> None:
        old = os.environ.pop("RTDL_KITTI_SOURCE_ROOT", None)
        try:
            with self.assertRaisesRegex(RuntimeError, "KITTI source root is not configured"):
                rt.discover_kitti_velodyne_frames()
        finally:
            if old is not None:
                os.environ["RTDL_KITTI_SOURCE_ROOT"] = old


if __name__ == "__main__":
    unittest.main()
