import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from scripts.goal43_optix_validation import TARGETS
from scripts.goal43_optix_validation import target_to_dict


class Goal43OptixValidationTest(unittest.TestCase):
    def test_targets_cover_expected_mix(self) -> None:
        pairs = {(target.workload, target.dataset) for target in TARGETS}
        self.assertIn(("lsi", "authored_lsi_minimal"), pairs)
        self.assertIn(("pip", "authored_pip_minimal"), pairs)
        self.assertIn(("overlay", "authored_overlay_minimal"), pairs)
        self.assertIn(("ray_tri_hitcount", "authored_ray_tri_minimal"), pairs)
        self.assertIn(("segment_polygon_hitcount", "authored_segment_polygon_minimal"), pairs)
        self.assertIn(("point_nearest_segment", "authored_point_nearest_segment_minimal"), pairs)
        self.assertIn(("lsi", "derived/br_county_subset_segments_tiled_x8"), pairs)
        self.assertIn(("pip", "derived/br_county_subset_polygons_tiled_x8"), pairs)

    def test_payload_shape_is_json_serializable(self) -> None:
        payload = {
            "suite": "goal43_optix_validation",
            "targets": [target_to_dict(target) for target in TARGETS],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "payload.json"
            path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
            loaded = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(loaded["suite"], "goal43_optix_validation")
        self.assertEqual(len(loaded["targets"]), len(TARGETS))


if __name__ == "__main__":
    unittest.main()
