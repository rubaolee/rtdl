from __future__ import annotations

import json
import os
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5386_author_trace_v2_patch_plan.py"
)
RESULT_PATH = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5386_author_trace_v2_patch_plan.json"
)
SPEC_PATH = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5385_author_trace_v2_spec.json"
)
AUTHOR_ROOT = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "xhd-author-src"


def _load_builder():
    spec = importlib.util.spec_from_file_location("build_xhd_goal5386_author_trace_v2_patch_plan", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5386AuthorTraceV2PatchPlanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_builder()
        cls.artifact = cls.module.build(output=RESULT_PATH, author_root=AUTHOR_ROOT)
        cls.spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))

    def test_patch_plan_validates_real_author_hooks(self) -> None:
        self.assertTrue(AUTHOR_ROOT.exists(), AUTHOR_ROOT)
        self.assertTrue(self.artifact["patch_plan"]["all_hooks_found"])
        self.assertFalse(self.artifact["patch_plan"]["missing_files"])
        self.assertFalse(self.artifact["patch_plan"]["missing_hooks"])

        hooks = self.artifact["patch_plan"]["hooks"]
        self.assertGreaterEqual(len(hooks), 8)
        for hook in hooks:
            self.assertTrue(hook["anchor_found"], hook["name"])
            self.assertIsInstance(hook["anchor_line"], int)
            self.assertGreater(hook["anchor_line"], 0)
            self.assertTrue(hook["would_patch_author_only"])

    def test_all_goal5385_required_fields_are_covered_by_hooks(self) -> None:
        expected = set(self.spec["author_trace_v2_schema"]["required_batch_fields"])
        observed = set(self.artifact["field_coverage"]["required_batch_fields"])
        self.assertEqual(expected, observed)
        self.assertTrue(self.artifact["field_coverage"]["all_required_fields_covered"])
        self.assertEqual([], self.artifact["field_coverage"]["uncovered_fields"])

        coverage = self.artifact["field_coverage"]["coverage_by_field"]
        for field in expected:
            self.assertIn(field, coverage)
            self.assertTrue(coverage[field], field)

    def test_patch_plan_is_dry_run_and_keeps_claims_false(self) -> None:
        implementation = self.artifact["implementation_status"]
        self.assertTrue(implementation["dry_run_patch_plan_ready"])
        self.assertFalse(implementation["author_v2_trace_implemented"])
        self.assertFalse(implementation["author_v2_trace_executed_on_pod"])
        self.assertFalse(implementation["patch_applied_to_author_tree"])
        self.assertFalse(implementation["rtdl_core_patched"])

        for key, value in self.artifact["claim_boundary"].items():
            self.assertIs(value, False, key)

    def test_targets_are_author_only_and_marker_is_goal5385_v2(self) -> None:
        targets = self.artifact["patch_plan"]["targets"]
        target_paths = {target["path"] for target in targets}
        self.assertEqual(
            {
                "src/hd_impl/hausdorff_distance_rt.h",
                "src/rt/launch_parameters.h",
                "src/rt/shaders/shaders_nn_uniform_grid.cu",
            },
            target_paths,
        )
        for target in targets:
            self.assertEqual("paper_app_author_instrumentation", target["owner"])
            self.assertTrue(target["exists"], target)
            self.assertNotIn("src/rtdsl", target["path"])
            self.assertNotIn("src/native", target["path"])

        self.assertEqual(
            "RTDL_GOAL5385_LB_STATUS_TRACE_V2",
            self.artifact["patch_plan"]["instrumentation_marker"],
        )


if __name__ == "__main__":
    unittest.main()
