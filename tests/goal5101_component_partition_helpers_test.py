from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import rtdsl as rt


class Goal5101ComponentPartitionHelpersTest(unittest.TestCase):
    def test_canonical_partition_is_label_renaming_invariant(self):
        self.assertEqual(
            rt.canonical_partition_labels([10, 10, 20, -1, 20]),
            (0, 0, 1, -1, 1),
        )
        self.assertTrue(rt.partition_equivalent([10, 10, 20, -1, 20], [5, 5, 9, -1, 9]))
        self.assertFalse(rt.partition_equivalent([10, 10, 20, -1, 20], [5, 9, 9, -1, 9]))

    def test_component_signature_uses_partition_not_raw_label_ids(self):
        first = rt.component_signature_from_partition([10, 10, 20, -1, 20], core_count=4)
        second = rt.component_signature_from_partition([5, 5, 9, -1, 9], core_flags=[1, 1, 1, 0, 1])
        self.assertEqual(first, second)
        self.assertEqual(
            first,
            {
                "core_count": 4,
                "component_count": 2,
                "component_sizes": [2, 2],
                "noise_count": 1,
            },
        )

    def test_signature_requires_core_count_or_flags(self):
        with self.assertRaises(ValueError):
            rt.component_signature_from_partition([0, 0, -1])


if __name__ == "__main__":
    unittest.main()
