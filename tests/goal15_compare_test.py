import json
import platform
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")
sys.path.insert(0, "scripts")

from goal15_compare_embree import compare_goal15
from goal15_compare_embree import local_embree_link_args
from goal15_compare_embree import native_source_path
from goal15_compare_embree import write_legacy_goal15_shim
from tests._optional_native_compare import skip_optional_native_compare_failure
from tests._optional_native_compare import skip_unless_optional_native_compare_toolchain_present


ROOT = Path(__file__).resolve().parents[1]


class Goal15CompareTest(unittest.TestCase):
    def test_native_compare_sources_resolve_from_archive_when_apps_dir_is_absent(self) -> None:
        lsi = native_source_path("goal15_lsi_native.cpp")
        pip = native_source_path("goal15_pip_native.cpp")

        self.assertTrue(lsi.exists())
        self.assertTrue(pip.exists())
        self.assertIn("docs/history/source_archive/apps", lsi.as_posix())
        self.assertIn("docs/history/source_archive/apps", pip.as_posix())

    def test_native_compare_prefers_local_embree_library_and_legacy_shim(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            shim = write_legacy_goal15_shim(Path(tmpdir))
            text = shim.read_text(encoding="utf-8")

        self.assertIn("rtdl_embree_run_lsi", text)
        self.assertIn("rtdl_embree_run_segment_pair_intersection", text)
        self.assertIn("rtdl_embree_run_pip", text)
        self.assertIn("rtdl_embree_run_point_primitive_anyhit_packet", text)
        system = platform.system()
        expected_local_lib = ROOT / "build" / ("librtdl_embree.lib" if system == "Windows" else "librtdl_embree.dylib" if system == "Darwin" else "librtdl_embree.so")
        if expected_local_lib.exists():
            self.assertTrue(local_embree_link_args(system))

    def test_native_compare_matches_rtdl_on_small_uniform_cases(self) -> None:
        skip_unless_optional_native_compare_toolchain_present()
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
