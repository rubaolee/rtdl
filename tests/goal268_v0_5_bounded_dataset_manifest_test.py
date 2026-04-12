import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class Goal268V05BoundedDatasetManifestTest(unittest.TestCase):
    def test_manifest_registry_covers_all_three_rtnn_dataset_families(self) -> None:
        manifests = rt.rtnn_bounded_dataset_manifests()
        self.assertEqual(len(manifests), 3)
        self.assertEqual(
            {manifest.dataset_handle for manifest in manifests},
            {
                "kitti_velodyne_point_sets",
                "stanford_3d_scan_point_sets",
                "nbody_or_millennium_snapshots",
            },
        )

    def test_every_manifest_keeps_same_runtime_budget(self) -> None:
        manifests = rt.rtnn_bounded_dataset_manifests()
        self.assertEqual({manifest.runtime_target for manifest in manifests}, {"<=10 minutes total package"})

    def test_writer_emits_expected_manifest_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "kitti_manifest.json"
            written = rt.write_rtnn_bounded_dataset_manifest("kitti_velodyne_point_sets", path)
            payload = json.loads(written.read_text(encoding="utf-8"))
            self.assertEqual(payload["manifest_kind"], "rtnn_bounded_dataset_manifest_v1")
            self.assertEqual(payload["dataset"]["handle"], "kitti_velodyne_point_sets")
            self.assertEqual(payload["bounded_manifest"]["bounded_profile_id"], "kitti_bounded_local_10min")
            self.assertEqual(payload["local_profile"]["artifact"], "dataset_packaging")

    def test_unknown_manifest_handle_fails_honestly(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaisesRegex(ValueError, "unknown RTNN bounded dataset manifest handle"):
                rt.write_rtnn_bounded_dataset_manifest("missing_handle", Path(tmpdir) / "out.json")


if __name__ == "__main__":
    unittest.main()
