from __future__ import annotations

import unittest

import rtdsl as rt


def _hiprt_available() -> bool:
    try:
        rt.hiprt_version()
    except (FileNotFoundError, OSError, RuntimeError):
        return False
    return True


@unittest.skipUnless(_hiprt_available(), "RTDL HIPRT backend library is not available")
class Goal540HiprtProbeTest(unittest.TestCase):
    def test_hiprt_version_surface(self) -> None:
        major, minor, patch = rt.hiprt_version()
        self.assertGreaterEqual(major, 2)
        self.assertGreaterEqual(minor, 0)
        self.assertGreaterEqual(patch, 0)

    def test_hiprt_context_probe_surface(self) -> None:
        probe = rt.hiprt_context_probe()
        self.assertIsInstance(probe["device_name"], str)
        self.assertTrue(probe["device_name"])
        self.assertGreaterEqual(probe["api_version"], 2000)
        self.assertIn(probe["device_type"], (0, 1))


if __name__ == "__main__":
    unittest.main()
