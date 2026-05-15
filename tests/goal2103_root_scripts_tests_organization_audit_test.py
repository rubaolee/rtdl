from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def git_ls(*pathspecs: str) -> list[str]:
    output = subprocess.check_output(["git", "ls-files", *pathspecs], cwd=ROOT, text=True)
    return [line for line in output.splitlines() if line.strip()]


class RootScriptsTestsOrganizationAuditTest(unittest.TestCase):
    def test_no_tracked_apps_generated_schemas_or_build_frontdoor(self) -> None:
        self.assertEqual([], git_ls("apps", "generated", "schemas", "build"))

    def test_relocated_material_has_clear_homes(self) -> None:
        required = (
            "examples/internal/rtdsl_python_demo.py",
            "docs/history/source_archive/apps/embree_remote_validation.cpp",
            "docs/history/source_archive/apps/goal15_lsi_native.cpp",
            "docs/history/source_archive/apps/goal15_pip_native.cpp",
            "examples/generated/plan_bundles/central_ray_triangle_stats/plan.json",
            "examples/generated/plan_bundles/county_soil_overlay/plan.json",
            "examples/generated/plan_bundles/county_zip_join/plan.json",
            "examples/generated/plan_bundles/point_in_counties/plan.json",
            "src/rtdsl/schemas/rtdl_plan.schema.json",
            "scripts/schemas/system_audit_schema.sql",
        )
        for rel in required:
            with self.subTest(rel=rel):
                self.assertTrue((ROOT / rel).exists())

    def test_scripts_and_tests_have_reader_indexes(self) -> None:
        scripts = (ROOT / "scripts" / "README.md").read_text(encoding="utf-8")
        tests = (ROOT / "tests" / "README.md").read_text(encoding="utf-8")
        self.assertIn("not the learner path", scripts)
        self.assertIn("Use First", scripts)
        self.assertIn("Use First", tests)
        self.assertIn("goal2101_frontpage_navigation_link_audit_test", tests)

    def test_runtime_schema_paths_resolve(self) -> None:
        import rtdsl.plan_schema as plan_schema

        self.assertTrue(plan_schema.schema_path().exists())
        self.assertTrue((ROOT / "scripts" / "schemas" / "system_audit_schema.sql").exists())


if __name__ == "__main__":
    unittest.main()

