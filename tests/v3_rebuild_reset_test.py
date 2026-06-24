from __future__ import annotations

import unittest
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "history" / "legacy_project_archive_2026-06-24"


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class V3RebuildResetTest(unittest.TestCase):
    def test_version_marker_is_current_v3_capability_line(self) -> None:
        self.assertEqual("v3.0.0", _read("VERSION").strip())
        pyproject = tomllib.loads(_read("pyproject.toml"))
        self.assertEqual(pyproject["project"]["version"], "3.0.0")
        self.assertIn("RTDL V3", pyproject["project"]["description"])

    def test_old_docs_are_not_in_current_docs_tree(self) -> None:
        old_current_paths = (
            "docs/rebuild",
            "docs/reviews",
            "docs/handoff",
            "docs/reports",
            "docs/release_reports",
            "docs/history",
            "docs/research",
            "docs/audit",
            "docs/engineering",
            "docs/features",
            "docs/rtdl",
            "docs/application_catalog.md",
            "docs/performance_model.md",
            "tutorials/current/07_grouped_sum_prepared_query.md",
            "examples/legacy_or_backend_proofs",
            "examples/generated",
            "examples/internal",
        )
        for rel in old_current_paths:
            self.assertFalse((ROOT / rel).exists(), rel)

    def test_history_archive_preserves_removed_material(self) -> None:
        self.assertTrue((ARCHIVE / "README.md").exists())
        expected = (
            "docs/rebuild",
            "docs/reviews",
            "docs/handoff",
            "docs/reports",
            "docs/release_reports",
            "docs/history",
            "docs/learn",
            "tutorials/current",
            "examples/generated",
            "examples/internal",
            "examples/legacy_or_backend_proofs",
            "scratch",
            "unused",
        )
        for rel in expected:
            self.assertTrue((ARCHIVE / rel).exists(), rel)

    def test_current_front_doors_are_short_and_do_not_link_to_old_docs(self) -> None:
        current_files = (
            "README.md",
            "docs/README.md",
            "docs/current_v3_status.md",
            "docs/public_documentation_map.md",
            "docs/learn/performance_wording.md",
            "tutorials/README.md",
            "tutorials/current/README.md",
            "examples/README.md",
            "examples/current/README.md",
        )
        combined = "\n".join(_read(path) for path in current_files)
        self.assertIn("RTDL V3", combined)
        self.assertNotIn("docs/rebuild", combined)
        self.assertNotIn("docs/reviews", combined)
        self.assertNotIn("history/", combined)
        self.assertNotIn("archive", combined.lower())
        self.assertNotIn("review", combined.lower())
        self.assertNotIn("handoff", combined.lower())
        self.assertNotIn("release_authorized", combined)
        self.assertNotIn("V4.0.0 is the current", combined)
        self.assertNotIn("V3.0.2 is the current", combined)

    def test_rtdsl_import_does_not_export_depublished_v4_api(self) -> None:
        import sys

        sys.path.insert(0, str(ROOT / "src"))
        import rtdsl  # noqa: PLC0415

        blocked = (
            "run_v4_fixed_radius_count_threshold_2d",
            "prepare_v4_fixed_radius_count_threshold_2d",
            "plan_v4_fixed_radius_count_threshold_2d",
            "describe_v4_fixed_radius_count_threshold_2d_route",
            "V4FixedRadiusCountThreshold2D",
        )
        for name in blocked:
            self.assertFalse(hasattr(rtdsl, name), name)


if __name__ == "__main__":
    unittest.main()
