import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class Goal277V05KittiLinuxReadyTest(unittest.TestCase):
    def test_missing_root_reports_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "missing"
            report = rt.inspect_kitti_linux_source_root(missing)
            self.assertFalse(report.exists)
            self.assertEqual(report.current_status, "missing")

    def test_existing_root_without_bins_reports_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "kitti"
            (root / "0001" / "velodyne").mkdir(parents=True, exist_ok=True)
            report = rt.inspect_kitti_linux_source_root(root)
            self.assertTrue(report.exists)
            self.assertEqual(report.current_status, "empty")
            self.assertEqual(report.velodyne_dir_count, 1)
            self.assertEqual(report.velodyne_bin_count, 0)

    def test_existing_root_with_velodyne_bins_reports_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "kitti"
            velodyne = root / "0001" / "velodyne"
            velodyne.mkdir(parents=True, exist_ok=True)
            (velodyne / "000000.bin").write_bytes(b"\x00" * 16)
            (velodyne / "000001.bin").write_bytes(b"\x00" * 16)
            report = rt.inspect_kitti_linux_source_root(root)
            self.assertEqual(report.current_status, "ready")
            self.assertEqual(report.velodyne_bin_count, 2)
            self.assertIn("0001/velodyne", report.sample_velodyne_dirs)

    def test_writer_emits_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "kitti"
            velodyne = root / "0001" / "velodyne"
            velodyne.mkdir(parents=True, exist_ok=True)
            (velodyne / "000000.bin").write_bytes(b"\x00" * 16)
            output = Path(tmpdir) / "report.json"
            written = rt.write_kitti_linux_ready_report(root, output)
            payload = json.loads(written.read_text(encoding="utf-8"))
            self.assertEqual(payload["report_kind"], "kitti_linux_ready_report_v1")
            self.assertEqual(payload["report"]["current_status"], "ready")


if __name__ == "__main__":
    unittest.main()
