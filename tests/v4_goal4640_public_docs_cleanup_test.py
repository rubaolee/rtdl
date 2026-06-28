from __future__ import annotations

import json
import os
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
    ROOT / "docs" / "v4_release_notes.md",
    ROOT / "docs" / "v4_engineering_summary.md",
    ROOT / "docs" / "app_level_benchmark_summary.md",
    ROOT / "docs" / "public_documentation_map.md",
    ROOT / "docs" / "learn" / "README.md",
    ROOT / "docs" / "learn" / "operator_catalog.md",
    ROOT / "docs" / "learn" / "partner_choice.md",
    ROOT / "docs" / "learn" / "performance_wording.md",
    ROOT / "docs" / "learn" / "source_tree_doctor.md",
    ROOT / "tutorials" / "README.md",
    ROOT / "tutorials" / "current" / "README.md",
    ROOT / "tutorials" / "current" / "01_first_run.md",
    ROOT / "tutorials" / "current" / "02_hello_world.md",
    ROOT / "tutorials" / "current" / "03_sorting_rows.md",
    ROOT / "tutorials" / "current" / "04_relations_and_operators.md",
    ROOT / "tutorials" / "current" / "05_prepare_run_continue.md",
    ROOT / "tutorials" / "current" / "06_measure_a_program.md",
    ROOT / "tutorials" / "current" / "07_benchmark_apps.md",
    ROOT / "tutorials" / "current" / "08_choose_a_partner.md",
    ROOT / "tutorials" / "current" / "09_benchmark_harness_protocol.md",
    ROOT / "examples" / "README.md",
    ROOT / "examples" / "tutorial_programs" / "README.md",
    ROOT / "examples" / "benchmark_apps" / "README.md",
    ROOT / "examples" / "paper_reproduction" / "README.md",
)

PUBLIC_EXAMPLE_SOURCE_SUFFIXES = {".cpp", ".h", ".md", ".py", ".txt"}
PUBLIC_EXAMPLE_SOURCES = tuple(
    sorted(
        path
        for base in (
            ROOT / "examples" / "tutorial_programs",
            ROOT / "examples" / "benchmark_apps",
            ROOT / "examples" / "paper_reproduction",
        )
        for path in base.rglob("*")
        if path.is_file() and path.suffix.lower() in PUBLIC_EXAMPLE_SOURCE_SUFFIXES
    )
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
    re.compile(r"tools/_archive", re.IGNORECASE),
    re.compile(r"tools/_archive/future/v4", re.IGNORECASE),
    re.compile(r"(?<![\w/])history[\\/]", re.IGNORECASE),
    re.compile(r"(?<![\w/])future[\\/]", re.IGNORECASE),
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
                    self.assertFalse(
                        clean_target.replace("\\", "/").lower().startswith(
                            (
                                "history/",
                                "../history/",
                                "future/",
                                "../future/",
                                "tools/_archive/history/",
                                "../tools/_archive/history/",
                                "tools/_archive/future/",
                                "../tools/_archive/future/",
                            )
                        ),
                        target,
                    )
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

    def test_public_v4_source_is_static_analysis_clean(self) -> None:
        source = (ROOT / "src" / "rtdsl" / "v4.py").read_text(encoding="utf-8")

        forbidden = (
            "from .v4_goal",
            "V4_GOAL",
            "v4_goal",
            "Goal",
        )
        for needle in forbidden:
            with self.subTest(needle=needle):
                self.assertNotIn(needle, source)

        self.assertIn("PUBLIC_API_SYMBOLS_V4", source)
        self.assertNotIn("v4_maintainer", source)

    def test_legacy_current_v3_status_is_not_in_public_docs(self) -> None:
        self.assertFalse((ROOT / "docs" / "current_v3_status.md").exists())
        self.assertTrue((ROOT / "docs" / "current_v4_status.md").exists())

    def test_clean_v4_example_entrypoints_run_without_cuda(self) -> None:
        commands = (
            ["examples/tutorial_programs/hello_world.py"],
            ["examples/tutorial_programs/v4_frontdoor_quickstart.py"],
            ["examples/tutorial_programs/sorting_rows.py"],
            ["examples/tutorial_programs/operator_primitives.py"],
            ["examples/tutorial_programs/partner_choices.py"],
            ["examples/tutorial_programs/fixed_radius_neighbors.py"],
            ["examples/tutorial_programs/nearest_neighbor.py"],
            ["examples/tutorial_programs/ray_triangle_hits.py"],
            ["examples/tutorial_programs/continuation_grouped_sum.py"],
            ["examples/tutorial_programs/measure_phases.py"],
            ["examples/tutorial_programs/point_in_polygon.py"],
            ["examples/tutorial_programs/spatial_join_lsi.py"],
            ["examples/tutorial_programs/aggregate_frontier_rows.py"],
            ["examples/tutorial_programs/component_union_from_radius.py"],
            ["examples/tutorial_programs/ranked_summary_neighbors.py"],
            ["examples/tutorial_programs/bounded_witness_collection.py"],
            ["examples/tutorial_programs/contact_manifold_lowering.py"],
            ["examples/tutorial_programs/triangle_counting_graph_lowering.py"],
            ["examples/tutorial_programs/robot_collision_lowering.py"],
            ["examples/tutorial_programs/hausdorff_distance_recipe.py"],
            ["examples/tutorial_programs/raydb_table_to_ray.py"],
            ["examples/tutorial_programs/rayjoin_topology_intro.py"],
            ["examples/tutorial_programs/aabb_spatial_index_predicates.py"],
            ["examples/tutorial_programs/benchmark_app_recipes.py"],
            ["examples/tutorial_programs/operator_callback_planning.py", "--case", "complex-callback"],
            ["examples/tutorial_programs/custom_predicate_early_exit_planning.py"],
            ["examples/paper_reproduction/rt_barneshut.py", "--json"],
            ["examples/paper_reproduction/rayjoin.py", "--json"],
            ["examples/tutorial_programs/fixed_radius_torch_device_arrays.py", "--dry-run", "--copies", "2"],
            ["examples/tutorial_programs/closest_hit_grouped_argmin_torch_device_arrays.py", "--dry-run"],
            ["examples/tutorial_programs/ray_triangle_any_hit_flags_torch_device_arrays.py", "--dry-run", "--ray-count", "16"],
            ["examples/tutorial_programs/primitive_grouped_i64_reduction_torch_device_arrays.py", "--dry-run"],
            ["examples/tutorial_programs/point_group_nearest_witness_torch_device_arrays.py", "--dry-run"],
            ["examples/tutorial_programs/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py", "--dry-run", "--ray-count", "16"],
            ["examples/tutorial_programs/aabb_index_all_ops_count.py", "--dry-run"],
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
                if command[0].endswith("benchmark_app_recipes.py"):
                    self.assertIn("RTDL V4 benchmark app recipes", proc.stdout)
                    for app_name in BENCHMARK_APP_NAMES:
                        self.assertIn(app_name, proc.stdout)
                    self.assertIn("request: fixed_radius", proc.stdout)
                    self.assertIn("surface: v4_ray_triangle_any_hit_flags_2d_device_arrays", proc.stdout)
                    self.assertNotIn("json.dumps", (ROOT / command[0]).read_text(encoding="utf-8"))
                    continue

                payload = json.loads(proc.stdout)
                self.assertIn(payload["status"], {"ok", "dry_run", "rejected_action_shaped_callback_deferred"})
                if command[0].endswith("operator_callback_planning.py"):
                    self.assertEqual("rejected_action_shaped_callback_deferred", payload["status"])
                if command[0].endswith("fixed_radius_torch_device_arrays.py"):
                    self.assertEqual(2, payload["copies"])
                self.assertFalse(_json_contains_forbidden_goal(payload))
                if "release_claim_authorized" in payload:
                    self.assertFalse(payload["release_claim_authorized"])
                if "tier3_callback_claim_authorized" in payload:
                    self.assertFalse(payload["tier3_callback_claim_authorized"])

    def test_tutorial_python_snippets_are_copy_paste_runnable(self) -> None:
        snippet_count = 0
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
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
                        env=env,
                    )
                    self.assertEqual(proc.returncode, 0, proc.stderr)

        self.assertGreaterEqual(snippet_count, 10)

    def test_benchmark_app_tutorial_covers_all_promoted_apps(self) -> None:
        tutorial = (ROOT / "tutorials" / "current" / "07_benchmark_apps.md").read_text(encoding="utf-8")
        readme = (ROOT / "examples" / "benchmark_apps" / "README.md").read_text(encoding="utf-8")

        for app_name in BENCHMARK_APP_NAMES:
            with self.subTest(app=app_name):
                self.assertIn(app_name, tutorial)
        self.assertIn("v4_app.py", readme)
        self.assertNotIn("rtdl_rayjoin_v2_spatial_join_app.py", readme)
        self.assertNotIn("rtdl_rt_dbscan_benchmark_app.py", tutorial)

    def test_clean_benchmark_app_entrypoints_run_without_cuda(self) -> None:
        commands = (
            "examples/benchmark_apps/rt_dbscan/v4_app.py",
            "examples/benchmark_apps/rtnn/v4_app.py",
            "examples/benchmark_apps/triangle_counting/v4_app.py",
            "examples/benchmark_apps/robot_collision/v4_app.py",
            "examples/benchmark_apps/raydb_style/v4_app.py",
            "examples/benchmark_apps/librts_spatial_index/v4_app.py",
            "examples/benchmark_apps/contact_manifold/v4_app.py",
            "examples/benchmark_apps/spatial_rayjoin/v4_app.py",
            "examples/benchmark_apps/barnes_hut/v4_app.py",
            "examples/benchmark_apps/hausdorff_xhd/v4_app.py",
        )
        for command in commands:
            with self.subTest(command=command):
                proc = subprocess.run(
                    [sys.executable, command, "--json"],
                    cwd=ROOT,
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                )
                payload = json.loads(proc.stdout)
                self.assertIn("app", payload)
                self.assertIn("operators", payload)
                self.assertIn("partners", payload)
                self.assertIn("current_entry", payload)
                self.assertTrue(payload["current_entry"].endswith("v4_app.py"))
                self.assertFalse(_json_contains_forbidden_goal(payload))

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
        self.assertIn("It does not say every benchmark app is\n  faster in V4", (ROOT / "docs" / "app_level_benchmark_summary.md").read_text(encoding="utf-8"))
        self.assertIn("Avoid summarizing the release as if every row has the same behavior", wording)

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
