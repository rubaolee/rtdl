from __future__ import annotations

import sys
import unittest
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


if __name__ == "__main__":
    unittest.main()
