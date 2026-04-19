import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")

from goal15_compare_embree import compare_goal15
from tests._optional_native_compare import skip_optional_native_compare_failure


class Goal15CompareTest(unittest.TestCase):
    def test_native_compare_matches_rtdl_on_small_uniform_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                payload = compare_goal15(Path(tmpdir))
            except Exception as exc:
                skip_optional_native_compare_failure(exc)
                raise
        self.assertTrue(payload["workloads"]["lsi"]["cpu_matches_native"])
        self.assertTrue(payload["workloads"]["lsi"]["embree_matches_native"])
        self.assertTrue(payload["workloads"]["pip"]["cpu_matches_native"])
        self.assertTrue(payload["workloads"]["pip"]["embree_matches_native"])
        self.assertGreater(payload["workloads"]["lsi"]["native_total_sec"], 0.0)
        self.assertGreater(payload["workloads"]["pip"]["native_total_sec"], 0.0)


if __name__ == "__main__":
    unittest.main()
