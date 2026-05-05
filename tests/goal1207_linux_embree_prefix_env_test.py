from __future__ import annotations

import os
import tempfile
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

    def test_embree4_header_takes_priority_when_both_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            prefix = Path(tmp)
            (prefix / "include" / "embree3").mkdir(parents=True)
            (prefix / "include" / "embree4").mkdir(parents=True)
            (prefix / "include" / "embree3" / "rtcore.h").write_text("", encoding="utf-8")
            (prefix / "include" / "embree4" / "rtcore.h").write_text("", encoding="utf-8")

            self.assertEqual(embree_runtime._embree_header_dir_name(prefix), "embree4")
            self.assertEqual(embree_runtime._embree_library_name("embree4"), "embree4")

    def test_embree3_header_is_accepted_for_ubuntu_default_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            prefix = Path(tmp)
            (prefix / "include" / "embree3").mkdir(parents=True)
            (prefix / "include" / "embree3" / "rtcore.h").write_text("", encoding="utf-8")

            self.assertEqual(embree_runtime._embree_header_dir_name(prefix), "embree3")
            self.assertEqual(embree_runtime._embree_library_name("embree3"), "embree3")

    def test_missing_embree_header_reports_no_detected_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            prefix = Path(tmp)
            (prefix / "include").mkdir()

            self.assertIsNone(embree_runtime._embree_header_dir_name(prefix))


if __name__ == "__main__":
    unittest.main()
