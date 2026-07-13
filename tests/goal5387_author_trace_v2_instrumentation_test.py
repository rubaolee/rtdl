from __future__ import annotations

import importlib.util
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "instrument_xhd_author_lb_status_trace_v2.py"
)
AUTHOR_ROOT = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "xhd-author-src"


def _load_module():
    spec = importlib.util.spec_from_file_location("instrument_xhd_author_lb_status_trace_v2", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _copy_author_src(tmp_root: Path) -> Path:
    author_root = tmp_root / "author"
    for rel in (
        Path("src/rt/launch_parameters.h"),
        Path("src/rt/shaders/shaders_nn_uniform_grid.cu"),
        Path("src/hd_impl/hausdorff_distance_rt.h"),
    ):
        dst = author_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(AUTHOR_ROOT / rel, dst)
    return author_root


class Goal5387AuthorTraceV2InstrumentationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def setUp(self) -> None:
        self.assertTrue(AUTHOR_ROOT.exists(), AUTHOR_ROOT)

    def test_patcher_applies_to_author_tree_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rtdl_goal5387_") as tmp:
            author_root = _copy_author_src(Path(tmp))

            first = self.module.patch_author_root(author_root)
            second = self.module.patch_author_root(author_root)

            self.assertEqual(
                {"launch_parameters": True, "shader": True, "rt_impl": True},
                first,
            )
            self.assertEqual(
                {"launch_parameters": False, "shader": False, "rt_impl": False},
                second,
            )

    def test_patched_author_files_contain_trace_v2_fields(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rtdl_goal5387_") as tmp:
            author_root = _copy_author_src(Path(tmp))
            self.module.patch_author_root(author_root)

            launch_text = (author_root / self.module.LAUNCH_REL).read_text(encoding="utf-8")
            shader_text = (author_root / self.module.SHADER_REL).read_text(encoding="utf-8")
            rt_text = (author_root / self.module.RT_REL).read_text(encoding="utf-8")

            for text in (launch_text, shader_text, rt_text):
                self.assertIn(self.module.MARKER, text)

            for field in (
                "status_offloading_count",
                "status_cmax2_abort_count",
                "status_point_loop_abort_count",
                "status_miss_count",
                "status_completed_count",
            ):
                self.assertIn(field, launch_text)
                self.assertIn(field, shader_text)

            for snippet in (
                'json_iter["LBTraceV2"]',
                self.module.SCHEMA,
                "rtdl_goal5385_batch_trace",
                "cmin2_after_ray_hash",
                "cmin2_after_load_balance_hash",
                "raw_offload_row_hash",
                "raw_offload_row_sample_point_ids",
                "raw_offload_row_sample_cell_ids",
                "LoadBalanceFeedbackUpdateCount",
                "uint32_t loadBalanceProcessing",
                "return uniq_np;",
            ):
                self.assertIn(snippet, rt_text)

            self.assertIn("if (config_.profiling) {", rt_text)
            self.assertNotIn("if (config_.profiling) {{", rt_text)

    def test_cli_summary_records_author_only_trace_and_forbidden_claims_false(self) -> None:
        with tempfile.TemporaryDirectory(prefix="rtdl_goal5387_") as tmp:
            author_root = _copy_author_src(Path(tmp))
            summary_path = Path(tmp) / "summary.json"

            original_argv = [
                "instrument_xhd_author_lb_status_trace_v2.py",
                "--author-root",
                str(author_root),
                "--summary",
                str(summary_path),
            ]
            import sys

            old_argv = sys.argv
            try:
                sys.argv = original_argv
                rc = self.module.main()
            finally:
                sys.argv = old_argv

            self.assertEqual(0, rc)
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(
                "rtdl.paper_reproduction.xhd.goal5387.author_lb_status_trace_v2_patch.v1",
                payload["schema"],
            )
            self.assertEqual(self.module.SCHEMA, payload["trace_schema"])
            self.assertEqual(
                {"launch_parameters": True, "shader": True, "rt_impl": True},
                payload["changed"],
            )
            self.assertTrue(payload["claim_boundary"]["author_v2_trace_implemented"])
            self.assertFalse(payload["claim_boundary"]["author_v2_trace_executed_on_pod"])

            for key, value in payload["claim_boundary"].items():
                if key == "author_v2_trace_implemented":
                    continue
                self.assertIs(value, False, key)

    def test_patcher_targets_are_author_source_only(self) -> None:
        target_paths = {
            str(self.module.LAUNCH_REL).replace("\\", "/"),
            str(self.module.SHADER_REL).replace("\\", "/"),
            str(self.module.RT_REL).replace("\\", "/"),
        }
        self.assertEqual(
            {
                "src/rt/launch_parameters.h",
                "src/rt/shaders/shaders_nn_uniform_grid.cu",
                "src/hd_impl/hausdorff_distance_rt.h",
            },
            target_paths,
        )
        for path in target_paths:
            self.assertNotIn("src/rtdsl", path)
            self.assertNotIn("src/native", path)


if __name__ == "__main__":
    unittest.main()
