from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "instrument_xhd_author_lb_status_trace.py"
)
AUTHOR_ROOT = Path.home() / "AppData" / "Local" / "Temp" / "xhd-author-src"


def _load_module():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("goal5374_instrumenter", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5374AuthorLbStatusTraceInstrumentationTest(unittest.TestCase):
    def _copy_author_subset(self, root: Path) -> Path:
        target = root / "author"
        for rel in (
            "src/rt/launch_parameters.h",
            "src/rt/shaders/shaders_nn_uniform_grid.cu",
            "src/hd_impl/hausdorff_distance_rt.h",
        ):
            src = AUTHOR_ROOT / rel
            self.assertTrue(src.exists(), src)
            dst = target / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        return target

    def test_patcher_inserts_author_lb_status_trace_fields(self) -> None:
        module = _load_module()
        with tempfile.TemporaryDirectory() as td:
            author = self._copy_author_subset(Path(td))
            changed = module.patch_author_root(author)
            self.assertEqual(
                {"launch_parameters": True, "shader": True, "rt_impl": True},
                changed,
            )
            launch = (author / "src/rt/launch_parameters.h").read_text(encoding="utf-8")
            shader = (author / "src/rt/shaders/shaders_nn_uniform_grid.cu").read_text(encoding="utf-8")
            rt_impl = (author / "src/hd_impl/hausdorff_distance_rt.h").read_text(encoding="utf-8")

            self.assertIn("RTDL_GOAL5374_LB_STATUS_TRACE", launch)
            self.assertIn("status_offloading_count", launch)
            self.assertIn("status_cmax2_abort_count", launch)
            self.assertIn("status_point_loop_abort_count", launch)

            self.assertIn("StatusOffloadingAppendCount", rt_impl)
            self.assertIn("StatusCmax2MbrAbortCount", rt_impl)
            self.assertIn("StatusPointLoopEarlyBreakCount", rt_impl)
            self.assertIn("RawOffloadRowsBeforeSortReduce", rt_impl)
            self.assertIn("RawOffloadRowsAuthorWidthBytes", rt_impl)
            self.assertIn("LBTrace", rt_impl)

            self.assertIn("params.status_cmax2_abort_count", shader)
            self.assertIn("params.status_offloading_count", shader)
            self.assertIn("params.status_point_loop_abort_count", shader)

    def test_patcher_is_idempotent_after_first_apply(self) -> None:
        module = _load_module()
        with tempfile.TemporaryDirectory() as td:
            author = self._copy_author_subset(Path(td))
            first = module.patch_author_root(author)
            second = module.patch_author_root(author)
            self.assertTrue(any(first.values()))
            self.assertEqual(
                {"launch_parameters": False, "shader": False, "rt_impl": False},
                second,
            )


if __name__ == "__main__":
    unittest.main()
