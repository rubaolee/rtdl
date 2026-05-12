import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1759_v1_8_release_prep_after_legacy_native_cleanup_2026-05-12.md"


class Goal1759V18ReleasePrepAfterLegacyNativeCleanupTest(unittest.TestCase):
    def test_report_declares_review_ready_not_release_authorized(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("v1_8_release_prep_ready_for_fresh_external_review", text)
        self.assertIn("does not authorize a tag", text)
        self.assertIn("version bump", text)
        self.assertIn("public release", text)

    def test_report_records_goal1758_as_source_abi_blocker_resolution(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal1758 removed the older Apple RT / HIPRT / Oracle / Vulkan", text)
        self.assertIn("`lsi`, `overlay`, and `triangle_probe` native support symbols", text)
        self.assertIn("app-agnostic native", text)
        self.assertIn("source/ABI boundary", text)

    def test_report_preserves_public_claim_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "package-install",
            "broad speedup",
            "whole-application acceleration",
            "universal backend",
            "Python+partner+RTDL",
            "PyTorch/CuPy",
            "true zero-copy",
        ):
            self.assertIn(phrase, text)

    def test_report_requires_external_reviews_gate_and_user_authorization(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Fresh Claude review", text)
        self.assertIn("Fresh Gemini review", text)
        self.assertIn("Focused v1.8 gate re-run", text)
        self.assertIn("Final v1.8 consensus/decision note", text)
        self.assertIn("Explicit user authorization", text)

    def test_report_protects_local_files(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz", text)
        self.assertIn("id_ed25519_rtdl_codex", text)
        self.assertIn("rtdl_v0_4.tar.gz", text)
        self.assertIn("scratch/", text)


if __name__ == "__main__":
    unittest.main()
