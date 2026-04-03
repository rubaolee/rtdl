import json
import tempfile
import unittest
from pathlib import Path

from scripts.goal44_optix_benchmark import POINT_COUNT
from scripts.goal44_optix_benchmark import POINT_SEED
from scripts.goal44_optix_benchmark import SCALE_FEATURE_LIMITS
from scripts.goal44_optix_benchmark import _generate_points


class Goal44OptixBenchmarkTest(unittest.TestCase):
    def test_scale_limits_are_expected(self) -> None:
        self.assertEqual(SCALE_FEATURE_LIMITS, {"smoke": 10, "medium": 250})

    def test_point_generation_is_deterministic(self) -> None:
        a = _generate_points(POINT_COUNT, seed=POINT_SEED)
        b = _generate_points(POINT_COUNT, seed=POINT_SEED)
        self.assertEqual(a.count, POINT_COUNT)
        self.assertEqual(b.count, POINT_COUNT)
        self.assertEqual(
            [(a.records[i].id, a.records[i].x, a.records[i].y) for i in range(5)],
            [(b.records[i].id, b.records[i].x, b.records[i].y) for i in range(5)],
        )

    def test_payload_shape_is_json_serializable(self) -> None:
        payload = {
            "dataset": "uscounty_zipcode/uscounty_feature_layer",
            "point_seed": POINT_SEED,
            "point_count": POINT_COUNT,
            "scales": [
                {
                    "scale": "smoke",
                    "max_features": 10,
                    "n_polygons": 25,
                    "n_points": POINT_COUNT,
                    "total_intersections": 250000,
                    "embree_sec": 1.0,
                    "optix_jit_sec": 0.5,
                    "optix_warm_sec": 0.02,
                    "speedup": 50.0,
                    "row_count_parity": True,
                    "exact_row_parity": True,
                    "parity_mode": "exact_rows",
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "goal44.json"
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            loaded = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(loaded["point_seed"], POINT_SEED)
        self.assertEqual(loaded["scales"][0]["parity_mode"], "exact_rows")


if __name__ == "__main__":
    unittest.main()
