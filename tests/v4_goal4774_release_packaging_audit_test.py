from __future__ import annotations

import sys
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4774_release_packaging_audit import (  # noqa: E402
    validate_v4_goal4774_release_packaging_audit,
)


class V4Goal4774ReleasePackagingAuditTest(unittest.TestCase):
    def test_packaging_audit_requires_clean_release_commit_before_tag(self) -> None:
        audit = validate_v4_goal4774_release_packaging_audit(ROOT)

        self.assertFalse(audit["direct_git_tag_allowed_now"])
        self.assertTrue(audit["clean_commit_required_before_tag"])

    def test_packaging_audit_excludes_external_and_dist(self) -> None:
        audit = validate_v4_goal4774_release_packaging_audit(ROOT)

        self.assertFalse(any(path.startswith("external/") for path in audit["release_commit_candidates"]))
        self.assertFalse(any(path.startswith("dist/") for path in audit["release_commit_candidates"]))

    def test_packaging_audit_includes_current_release_authorization_files(self) -> None:
        audit = validate_v4_goal4774_release_packaging_audit(ROOT)
        candidates = set(audit["release_commit_candidates"])
        already_tracked_or_clean = set(audit["required_current_files_not_dirty"])
        included = candidates | already_tracked_or_clean

        self.assertIn("future/v4/reviews/antigravity_v4_gemini_full_coverage_review_2026-06-27.md", included)
        self.assertIn("future/v4/v4_goal4773_antigravity_review_intake_and_release_owner_status_2026-06-27.md", included)
        self.assertIn("src/rtdsl/v4_goal4773_release_authorization_status.py", included)
        self.assertIn("tests/v4_goal4773_release_authorization_status_test.py", included)

    def test_existing_v4_wheel_candidates_do_not_package_history_or_docs(self) -> None:
        wheels = sorted((ROOT / "dist").glob("goal*_v4_release_candidate/*.whl"))

        self.assertGreaterEqual(len(wheels), 1)
        for wheel in wheels:
            with self.subTest(wheel=wheel.relative_to(ROOT).as_posix()):
                with zipfile.ZipFile(wheel) as archive:
                    names = archive.namelist()
                    bad = [
                        name
                        for name in names
                        if name.startswith(("docs/", "history/", "future/", "examples/", "tutorials/"))
                        or "docs/reviews" in name
                        or "phoenix_v3" in name.lower()
                    ]
                    metadata_name = next(name for name in names if name.endswith("METADATA"))
                    metadata = archive.read(metadata_name).decode("utf-8")

                self.assertEqual([], bad)
                self.assertIn("Name: rtdl-source-tree", metadata)
                self.assertIn("Version: 4.0.0", metadata)


if __name__ == "__main__":
    unittest.main()
