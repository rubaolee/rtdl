import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class Goal287KittiDuplicateFreeSelectorTest(unittest.TestCase):
    def _write_frame(self, path: Path, xyzs: tuple[tuple[float, float, float], ...]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = b"".join(struct.pack("<ffff", x, y, z, 1.0) for x, y, z in xyzs)
        path.write_bytes(payload)

    def test_selector_skips_duplicate_pair_and_finds_next_clean_pair(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "source"
            frame_dir = root / "2011_09_26" / "2011_09_26_drive_0001_sync" / "velodyne_points" / "data"
            self._write_frame(frame_dir / "0000000000.bin", ((1.0, 2.0, 3.0), (9.0, 9.0, 9.0)))
            self._write_frame(frame_dir / "0000000001.bin", ((1.0, 2.0, 3.0), (8.0, 8.0, 8.0)))
            self._write_frame(frame_dir / "0000000002.bin", ((4.0, 5.0, 6.0), (7.0, 7.0, 7.0)))
            records = rt.discover_kitti_velodyne_frames(root)
            pair = rt.find_duplicate_free_kitti_pair(
                source_root=root,
                candidate_records=records,
                query_start_index=0,
                max_search_offset=3,
                max_points_per_frame=2,
                max_total_points=2,
                work_dir=Path(tmpdir) / "selector",
            )
            self.assertEqual(pair.query_start_index, 0)
            self.assertEqual(pair.search_start_index, 2)
            self.assertEqual(pair.duplicate_match_count, 0)


if __name__ == "__main__":
    unittest.main()
