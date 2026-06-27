from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4640_public_docs_cleanup_decision import validate_v4_goal4640_public_docs_cleanup
import rtdsl.v4 as v4

PUBLIC_DOCS = (
    ROOT / "README.md",
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "current_v4_status.md",
    ROOT / "docs" / "app_level_benchmark_summary.md",
    ROOT / "docs" / "public_documentation_map.md",
    ROOT / "docs" / "learn" / "README.md",
    ROOT / "docs" / "learn" / "operator_catalog.md",
    ROOT / "docs" / "learn" / "performance_wording.md",
    ROOT / "docs" / "learn" / "source_tree_doctor.md",
    ROOT / "tutorials" / "README.md",
    ROOT / "tutorials" / "current" / "README.md",
    ROOT / "tutorials" / "current" / "01_first_run.md",
    ROOT / "tutorials" / "current" / "02_hello_world.md",
    ROOT / "tutorials" / "current" / "03_backend_choice.md",
    ROOT / "tutorials" / "current" / "04_prepared_runtime.md",
    ROOT / "tutorials" / "current" / "05_measurement_boundaries.md",
    ROOT / "tutorials" / "current" / "06_benchmark_apps.md",
    ROOT / "examples" / "README.md",
    ROOT / "examples" / "current" / "research_benchmarks" / "README.md",
    ROOT / "examples" / "v4" / "README.md",
)

PUBLIC_EXAMPLE_SOURCES = tuple(sorted((ROOT / "examples" / "v4").glob("*.py"))) + (
    ROOT / "future" / "v4" / "examples" / "v4_frontdoor_quickstart.py",
)

BENCHMARK_APP_NAMES = (
    "RTDBSCAN",
    "RTNN",
    "Triangle counting",
    "Robot collision",
    "RayDB-style",
    "LibRTS spatial index",
    "Contact manifold",
    "Spatial RayJoin",
    "Barnes-Hut",
    "Hausdorff XHD",
)

PUBLIC_SURFACE_FORBIDDEN = (
    re.compile(r"\bGoal\d+\b", re.IGNORECASE),
    re.compile(r"\bgoal\d+\b", re.IGNORECASE),
    re.compile(r"parity/control", re.IGNORECASE),
    re.compile(r"review debt", re.IGNORECASE),
    re.compile(r"\baudit\b", re.IGNORECASE),
    re.compile(r"\breviewer\b", re.IGNORECASE),
    re.compile(r"release-review", re.IGNORECASE),
    re.compile(r"\bClaude\b|\bGemini\b|\bAntigravity\b"),
    re.compile(r"release candidate", re.IGNORECASE),
    re.compile(r"docs/reviews", re.IGNORECASE),
    re.compile(r"future/v4", re.IGNORECASE),
)


def _json_contains_forbidden_goal(value: object) -> bool:
    if isinstance(value, dict):
        return any(_json_contains_forbidden_goal(key) or _json_contains_forbidden_goal(item) for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return any(_json_contains_forbidden_goal(item) for item in value)
    if isinstance(value, str):
        return re.search(r"goal\d+", value, flags=re.IGNORECASE) is not None
    return False


class V4Goal4640PublicDocsCleanupTest(unittest.TestCase):
    def test_public_docs_are_v4_current_not_v3_current(self) -> None:
        forbidden = (
            "V3.0.0",
            "current V3",
            "Current V3",
            "V3 tutorial",
            "V3 checkout",
            "V3 source-tree",
            "not a release announcement",
            "development surface",
            "development guidance",
            "development catalog",
        )
        for path in PUBLIC_DOCS:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                text = path.read_text(encoding="utf-8")
                self.assertIn("V4", text)
                for needle in forbidden:
                    self.assertNotIn(needle, text)

    def test_public_docs_do_not_leak_internal_review_language(self) -> None:
        for path in PUBLIC_DOCS:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                text = path.read_text(encoding="utf-8")
                for pattern in PUBLIC_SURFACE_FORBIDDEN:
                    self.assertIsNone(pattern.search(text), pattern.pattern)

    def test_public_docs_relative_links_resolve(self) -> None:
        link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        for path in PUBLIC_DOCS:
            text = path.read_text(encoding="utf-8")
            for label, target in link_pattern.findall(text):
                if "://" in target or target.startswith("#") or target.startswith("mailto:"):
                    continue
                clean_target = target.split("#", 1)[0]
                if not clean_target:
                    continue
                with self.subTest(path=path.relative_to(ROOT).as_posix(), label=label, target=target):
                    self.assertTrue((path.parent / clean_target).resolve().exists(), target)

    def test_public_v4_example_sources_do_not_leak_goal_labels(self) -> None:
        for path in PUBLIC_EXAMPLE_SOURCES:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                text = path.read_text(encoding="utf-8")
                for pattern in PUBLIC_SURFACE_FORBIDDEN[:3]:
                    self.assertIsNone(pattern.search(text), pattern.pattern)

    def test_public_v4_star_import_api_does_not_export_maintainer_goal_symbols(self) -> None:
        for symbol in v4.__all__:
            with self.subTest(symbol=symbol):
                self.assertIsNone(re.search(r"goal\d+", symbol, flags=re.IGNORECASE))
                self.assertNotIn("AUDIT", symbol.upper())
                self.assertNotIn("REVIEW", symbol.upper())

        self.assertEqual(tuple(v4.__all__), v4.PUBLIC_API_SYMBOLS_V4)
        self.assertIn("plan_operator_request_v4", v4.__all__)
        self.assertIn("prepare_ray_triangle_any_hit_weighted_sum_3d_device_arrays_v4", v4.__all__)
        self.assertNotIn("v4_goal4686_tier3_wrapper_abi_scaffold", v4.__all__)

    def test_public_v4_interactive_dir_hides_maintainer_goal_symbols(self) -> None:
        public_names = dir(v4)

        self.assertEqual(public_names, sorted(v4.PUBLIC_API_SYMBOLS_V4))
        for symbol in public_names:
            with self.subTest(symbol=symbol):
                self.assertIsNone(re.search(r"goal\d+", symbol, flags=re.IGNORECASE))
                self.assertNotIn("AUDIT", symbol.upper())
                self.assertNotIn("REVIEW", symbol.upper())

    def test_legacy_current_v3_status_is_not_in_public_docs(self) -> None:
        self.assertFalse((ROOT / "docs" / "current_v3_status.md").exists())
        self.assertTrue((ROOT / "docs" / "current_v4_status.md").exists())

    def test_clean_v4_example_entrypoints_run_without_cuda(self) -> None:
        commands = (
            ["examples/v4/v4_frontdoor_quickstart.py"],
            ["examples/v4/benchmark_app_recipes.py"],
            ["examples/v4/operator_callback_planning.py", "--case", "complex-callback"],
            ["examples/v4/custom_predicate_early_exit_planning.py"],
            ["examples/v4/fixed_radius_torch_device_arrays.py", "--dry-run", "--copies", "2"],
            ["examples/v4/closest_hit_grouped_argmin_torch_device_arrays.py", "--dry-run"],
            ["examples/v4/ray_triangle_any_hit_flags_torch_device_arrays.py", "--dry-run", "--ray-count", "16"],
            ["examples/v4/primitive_grouped_i64_reduction_torch_device_arrays.py", "--dry-run"],
            ["examples/v4/point_group_nearest_witness_torch_device_arrays.py", "--dry-run"],
            ["examples/v4/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py", "--dry-run", "--ray-count", "16"],
            ["examples/v4/aabb_index_all_ops_count.py", "--dry-run"],
        )
        for command in commands:
            with self.subTest(command=" ".join(command)):
                proc = subprocess.run(
                    [sys.executable, *command],
                    cwd=ROOT,
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                )
                payload = json.loads(proc.stdout)
                self.assertIn(payload["status"], {"ok", "dry_run", "rejected_action_shaped_callback_deferred"})
                if command[0].endswith("operator_callback_planning.py"):
                    self.assertEqual("rejected_action_shaped_callback_deferred", payload["status"])
                if command[0].endswith("fixed_radius_torch_device_arrays.py"):
                    self.assertEqual(2, payload["copies"])
                if command[0].endswith("benchmark_app_recipes.py"):
                    self.assertEqual(10, payload["app_count"])
                    self.assertEqual(BENCHMARK_APP_NAMES, tuple(row["app"] for row in payload["recipes"]))
                self.assertFalse(_json_contains_forbidden_goal(payload))
                self.assertFalse(payload["release_claim_authorized"])
                self.assertFalse(payload["tier3_callback_claim_authorized"])

    def test_tutorial_python_snippets_are_copy_paste_runnable(self) -> None:
        snippet_count = 0
        for path in sorted((ROOT / "tutorials" / "current").glob("*.md")):
            text = path.read_text(encoding="utf-8")
            snippets = re.findall(r"```python\n(.*?)\n```", text, flags=re.S)
            for index, snippet in enumerate(snippets, 1):
                snippet_count += 1
                with self.subTest(path=path.relative_to(ROOT).as_posix(), block=index):
                    proc = subprocess.run(
                        [sys.executable, "-c", snippet],
                        cwd=ROOT,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    self.assertEqual(proc.returncode, 0, proc.stderr)

        self.assertGreaterEqual(snippet_count, 10)

    def test_benchmark_app_tutorial_covers_all_promoted_apps(self) -> None:
        tutorial = (ROOT / "tutorials" / "current" / "06_benchmark_apps.md").read_text(encoding="utf-8")

        for app_name in BENCHMARK_APP_NAMES:
            with self.subTest(app=app_name):
                self.assertIn(app_name, tutorial)

    def test_operator_catalog_is_visible_without_overclaim(self) -> None:
        text = (ROOT / "docs" / "current_v4_status.md").read_text(encoding="utf-8")
        catalog = (ROOT / "docs" / "learn" / "operator_catalog.md").read_text(encoding="utf-8")
        wording = (ROOT / "docs" / "learn" / "performance_wording.md").read_text(encoding="utf-8")
        self.assertIn("V4 exposes measured generic operator/workflow surfaces", text)
        self.assertIn("fixed-radius count threshold", text)
        self.assertIn("custom predicate early-exit", text)
        self.assertIn("Representative result", catalog)
        self.assertIn("Most V4.0 measured operators are 1.2x-1.7x", wording)
        self.assertIn("denominator", wording)
        self.assertIn("whole-application speedup claim", text)
        self.assertIn("broad all-app", wording)

    def test_machine_decision_records_docs_cleanup_without_release_authorization(self) -> None:
        decision = validate_v4_goal4640_public_docs_cleanup(ROOT)

        self.assertEqual("complete_public_v4_docs_cleanup_pending_external_review", decision["decision"])
        self.assertTrue(decision["public_docs_current"])
        self.assertTrue(decision["examples_checked"])
        self.assertTrue(decision["v3_current_doc_archived"])
        self.assertFalse(decision["release_authorized"])
        self.assertFalse(decision["broad_v4_speedup_claim_authorized"])
        self.assertFalse(decision["whole_app_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
