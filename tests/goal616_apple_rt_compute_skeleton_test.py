from __future__ import annotations

import platform
import unittest

import rtdsl as rt


def apple_rt_available() -> bool:
    if platform.system() != "Darwin":
        return False
    try:
        rt.apple_rt_context_probe()
        return True
    except Exception:
        return False


@unittest.skipUnless(apple_rt_available(), "Apple RT backend is not available")
class Goal616AppleRtComputeSkeletonTest(unittest.TestCase):
    def test_u32_add_compute_roundtrip(self) -> None:
        self.assertEqual(
            rt.apple_rt_compute_u32_add((1, 2, 3, 1024), (10, 20, 30, 4096)),
            (11, 22, 33, 5120),
        )

    def test_u32_add_compute_empty_input(self) -> None:
        self.assertEqual(rt.apple_rt_compute_u32_add((), ()), ())

    def test_u32_add_compute_preserves_uint32_values(self) -> None:
        self.assertEqual(rt.apple_rt_compute_u32_add((0xFFFFFFFF,), (0,)), (0xFFFFFFFF,))

    def test_u32_add_compute_rejects_mismatched_lengths(self) -> None:
        with self.assertRaises(ValueError):
            rt.apple_rt_compute_u32_add((1,), (1, 2))

    def test_u32_add_compute_rejects_non_uint32_values(self) -> None:
        with self.assertRaises(ValueError):
            rt.apple_rt_compute_u32_add((-1,), (1,))
        with self.assertRaises(ValueError):
            rt.apple_rt_compute_u32_add((2**32,), (1,))


if __name__ == "__main__":
    unittest.main()
