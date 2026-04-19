import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")

from goal19_compare_embree_performance import compare_goal19
from tests._optional_native_compare import skip_optional_native_compare_failure


class Goal19CompareTest(unittest.TestCase):
    def test_goal19_compare_matches_native_on_smoke_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                payload = compare_goal19(
                    Path(tmpdir),
                    fixture_profile={
                        "lsi": {"build": 40, "probe": 24},
                        "pip": {"build": 40, "probe": 24},
                    },
                    large_profile={
                        "lsi": {"build": 120, "probe": 90},
                        "pip": {"build": 150, "probe": 120},
                    },
                    fixture_repeats=2,
                    large_repeats=2,
                )
            except Exception as exc:
                skip_optional_native_compare_failure(exc)
                raise
        self.assertTrue(payload["fixture"]["lsi"]["dict_matches_native"])
        self.assertTrue(payload["fixture"]["pip"]["dict_matches_native"])
        self.assertTrue(payload["fixture"]["lsi"]["raw_matches_dict"])
        self.assertTrue(payload["fixture"]["pip"]["raw_matches_dict"])
        self.assertTrue(payload["large_profile"]["lsi"]["dict_matches_native"])
        self.assertTrue(payload["large_profile"]["pip"]["dict_matches_native"])
        self.assertGreater(payload["total_wall_sec"], 0.0)


if __name__ == "__main__":
    unittest.main()
