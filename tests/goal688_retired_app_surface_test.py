from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DOCS = (
    REPO_ROOT / "README.md",
    REPO_ROOT / "docs" / "quick_tutorial.md",
    REPO_ROOT / "docs" / "release_facing_examples.md",
    REPO_ROOT / "docs" / "tutorials" / "db_workloads.md",
    REPO_ROOT / "examples" / "README.md",
)


class Goal688RetiredAppSurfaceTest(unittest.TestCase):
    def test_only_unified_db_and_apple_apps_are_public_matrix_rows(self) -> None:
        apps = set(rt.public_apps())

        self.assertIn("database_analytics", apps)
        self.assertIn("apple_rt_demo", apps)
        self.assertNotIn("sales_risk_screening", apps)
        self.assertNotIn("regional_order_dashboard", apps)
        self.assertNotIn("regional_order_dashboard_kernel_form", apps)
        self.assertNotIn("apple_rt_closest_hit", apps)
        self.assertNotIn("apple_rt_visibility_count", apps)

    def test_public_docs_no_longer_advertise_retired_app_commands(self) -> None:
        retired_commands = (
            "python examples/rtdl_v0_7_db_app_demo.py",
            "python examples/rtdl_v0_7_db_kernel_app_demo.py",
            "python examples/rtdl_sales_risk_screening.py",
            "python examples/rtdl_apple_rt_closest_hit.py",
            "python examples/rtdl_apple_rt_visibility_count.py",
        )

        for path in PUBLIC_DOCS:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=str(path.relative_to(REPO_ROOT))):
                self.assertIn("rtdl_database_analytics_app.py", text)
                if path.name != "db_workloads.md":
                    self.assertIn("rtdl_apple_rt_demo_app.py", text)
                for command in retired_commands:
                    self.assertNotIn(command, text)

    def test_catalog_marks_scenario_specific_files_as_compatibility_helpers(self) -> None:
        catalog = (REPO_ROOT / "docs" / "application_catalog.md").read_text(encoding="utf-8")

        self.assertIn("older scenario-specific files remain runnable compatibility helpers", catalog)
        self.assertIn("users should start from the unified Apple", catalog)


if __name__ == "__main__":
    unittest.main()
