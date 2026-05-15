from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


LINK_RE = re.compile(r"(?<!!)\[[^\]\n]*\]\(([^)\n]+)\)")


class ExamplesDirectoryOrganizationAuditTest(unittest.TestCase):
    def test_root_examples_do_not_expose_archived_version_or_goal_files(self) -> None:
        bad_names = [
            path.name
            for path in EXAMPLES.glob("*.py")
            if re.search(r"(?:^|_)v[0-9]_|goal[0-9]", path.name, re.IGNORECASE)
        ]
        self.assertEqual([], bad_names)

    def test_archived_example_helpers_are_internal(self) -> None:
        archived = EXAMPLES / "internal" / "archived_apps"
        self.assertTrue((archived / "README.md").exists())
        self.assertTrue((archived / "rtdl_v0_7_db_app_demo.py").exists())
        self.assertTrue((archived / "rtdl_v0_7_db_kernel_app_demo.py").exists())
        self.assertTrue((archived / "rtdl_apple_rt_closest_hit.py").exists())
        self.assertTrue((archived / "rtdl_apple_rt_visibility_count.py").exists())

    def test_examples_readme_local_links_resolve(self) -> None:
        readmes = [EXAMPLES / "README.md", *(EXAMPLES.glob("*/*README.md"))]
        broken: list[str] = []
        checked = 0
        for readme in readmes:
            if not readme.exists():
                continue
            text = readme.read_text(encoding="utf-8")
            for match in LINK_RE.finditer(text):
                raw = match.group(1).strip()
                if not raw or raw.startswith("#"):
                    continue
                parsed = urlparse(raw)
                if parsed.scheme in {"http", "https", "mailto", "computer", "file", "app"}:
                    continue
                target = raw.split("#", 1)[0].split("?", 1)[0]
                if not target:
                    continue
                try:
                    target = unquote(target)
                except ValueError:
                    pass
                resolved = (readme.parent / target).resolve()
                checked += 1
                if not resolved.exists():
                    broken.append(f"{readme.relative_to(ROOT).as_posix()} -> {raw}")
        self.assertGreaterEqual(checked, 10)
        self.assertEqual([], broken)

    def test_current_wrappers_import_internal_archived_helpers(self) -> None:
        database = (EXAMPLES / "rtdl_database_analytics_app.py").read_text(encoding="utf-8")
        apple = (EXAMPLES / "rtdl_apple_rt_demo_app.py").read_text(encoding="utf-8")
        rawkernel = (EXAMPLES / "rtdl_control_apps_cupy_rawkernel.py").read_text(encoding="utf-8")
        self.assertIn("from examples.internal.archived_apps import rtdl_v0_7_db_app_demo", database)
        self.assertIn("from examples.internal.archived_apps import rtdl_v0_7_db_app_demo", rawkernel)
        self.assertIn("from examples.internal.archived_apps import rtdl_apple_rt_closest_hit", apple)


if __name__ == "__main__":
    unittest.main()

