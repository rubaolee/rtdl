from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest import mock

from rtdsl import embree_runtime


class Goal1207LinuxEmbreePrefixEnvTest(unittest.TestCase):
    def test_linux_honors_rtdl_embree_prefix(self) -> None:
        with mock.patch.dict(os.environ, {"RTDL_EMBREE_PREFIX": "/opt/embree-4.4.0"}):
            self.assertEqual(
                embree_runtime._default_embree_prefix("Linux"),
                Path("/opt/embree-4.4.0"),
            )

    def test_darwin_honors_rtdl_embree_prefix(self) -> None:
        with mock.patch.dict(os.environ, {"RTDL_EMBREE_PREFIX": "/tmp/custom-embree"}):
            self.assertEqual(
                embree_runtime._default_embree_prefix("Darwin"),
                Path("/tmp/custom-embree"),
            )

    def test_linux_default_remains_usr_without_override(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(embree_runtime._default_embree_prefix("Linux"), Path("/usr"))


if __name__ == "__main__":
    unittest.main()
