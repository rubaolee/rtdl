from __future__ import annotations

import unittest
from pathlib import Path

from src.rtdsl.current_benchmark_front_doors import CURRENT_BENCHMARK_FRONT_DOORS
from src.rtdsl.current_benchmark_scale_profiles import CURRENT_BENCHMARK_SCALE_PROFILES


REPO_ROOT = Path(__file__).resolve().parents[1]

EXCLUDED_PREFIXES = (
    "docs/reports/",
    "docs/reviews/",
    "docs/handoff/",
    "docs/history/",
    "docs/release_reports/",
)

OLD_EXAMPLE_TOKENS = (
    "examples/" + "v2_0",
    "examples\\" + "v2_0",
    "examples." + "v2_0",
)


def _current_surface_files() -> list[Path]:
    roots = (
        REPO_ROOT / "README.md",
        REPO_ROOT / "docs",
        REPO_ROOT / "examples",
        REPO_ROOT / "src" / "rtdsl" / "current_benchmark_front_doors.py",
        REPO_ROOT / "src" / "rtdsl" / "current_benchmark_scale_profiles.py",
    )
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
            continue
        for path in root.rglob("*"):
            if path.suffix.lower() not in {".md", ".py", ".json"}:
                continue
            rel = path.relative_to(REPO_ROOT).as_posix()
            if any(rel.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
                continue
            files.append(path)
    return sorted(set(files), key=lambda path: path.relative_to(REPO_ROOT).as_posix())


class Goal4272CurrentExamplesCanonicalPathTest(unittest.TestCase):
    def test_current_examples_tree_replaces_version_named_tree(self) -> None:
        self.assertTrue((REPO_ROOT / "examples" / "current").is_dir())
        self.assertFalse((REPO_ROOT / "examples" / "v2_0").exists())
        for rel in (
            "README.md",
            "getting_started/rtdl_hello_world.py",
            "getting_started/rtdl_primitive_discovery_workflow.py",
            "features/ray_queries/rtdl_ray_triangle_any_hit.py",
            "research_benchmarks/README.md",
        ):
            self.assertTrue((REPO_ROOT / "examples" / "current" / rel).exists(), rel)

    def test_current_surface_does_not_point_to_old_examples_path(self) -> None:
        offenders: list[str] = []
        for path in _current_surface_files():
            rel = path.relative_to(REPO_ROOT).as_posix()
            text = path.read_text(encoding="utf-8")
            for token in OLD_EXAMPLE_TOKENS:
                if token in text:
                    offenders.append(f"{rel}: contains {token!r}")
        self.assertEqual([], offenders)

    def test_current_benchmark_command_paths_resolve(self) -> None:
        commands = [entry.command for entry in CURRENT_BENCHMARK_FRONT_DOORS]
        commands.extend(entry.command for entry in CURRENT_BENCHMARK_SCALE_PROFILES)
        missing: list[str] = []
        for command in commands:
            for arg in command:
                if not arg.startswith("examples/current/"):
                    continue
                if not (REPO_ROOT / arg).exists():
                    missing.append(arg)
        self.assertEqual([], sorted(set(missing)))

    def test_examples_package_aliases_use_current_namespace(self) -> None:
        init_text = (REPO_ROOT / "examples" / "__init__.py").read_text(encoding="utf-8")
        self.assertIn("examples.current.getting_started.rtdl_hello_world", init_text)
        for token in OLD_EXAMPLE_TOKENS:
            self.assertNotIn(token, init_text)


if __name__ == "__main__":
    unittest.main()
