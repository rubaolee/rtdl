import unittest

from scripts.goal3631_segment_pair_backend_conformance_runner import _trim_counts_payload


class Goal3641SegmentPairRunnerCountVectorCapTest(unittest.TestCase):
    def test_count_vectors_can_be_truncated_after_full_comparisons(self):
        payload = {"counts": list(range(10)), "hit_pair_count": 45}
        trimmed = _trim_counts_payload(payload, 3)
        self.assertEqual(trimmed["counts"], [0, 1, 2])
        self.assertTrue(trimmed["counts_truncated"])
        self.assertEqual(trimmed["counts_full_length"], 10)
        self.assertEqual(trimmed["hit_pair_count"], 45)
        self.assertIn("after comparisons", trimmed["counts_truncation_note"])

    def test_small_vectors_remain_unmodified_and_marked_not_truncated(self):
        payload = {"counts": [1, 2, 3]}
        trimmed = _trim_counts_payload(payload, 3)
        self.assertEqual(trimmed["counts"], [1, 2, 3])
        self.assertFalse(trimmed["counts_truncated"])
        self.assertEqual(trimmed["counts_full_length"], 3)

    def test_negative_limit_keeps_full_vector_for_back_compat(self):
        payload = {"counts": list(range(5))}
        trimmed = _trim_counts_payload(payload, -1)
        self.assertEqual(trimmed["counts"], list(range(5)))
        self.assertFalse(trimmed["counts_truncated"])


if __name__ == "__main__":
    unittest.main()
