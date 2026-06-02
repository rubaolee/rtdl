from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3056_v2_6_pre_release_public_doc_cleanup_audit_2026-06-02.md"
TOTAL_AUDIT = ROOT / "docs" / "reports" / "goal3058_v2_6_release_candidate_doc_total_audit_2026-06-02.md"

CURRENT_FACING_DOCS = [
    "README.md",
    "docs/README.md",
    "docs/current_architecture.md",
    "docs/backend_maturity.md",
    "docs/current_main_support_matrix.md",
    "docs/partner_acceleration_boundaries.md",
    "docs/app_example_quickstart.md",
    "docs/tutorials/README.md",
    "docs/tutorials/v2_app_building.md",
    "docs/tutorials/partner_optix_column_anyhit.md",
    "docs/rtdl_feature_guide.md",
    "docs/application_catalog.md",
    "examples/README.md",
    "examples/v2_0/README.md",
]


class Goal3056V26PreReleasePublicDocCleanupAuditTest(unittest.TestCase):
    def _read(self, rel: str) -> str:
        return (ROOT / rel).read_text(encoding="utf-8")

    def test_report_records_file_by_file_operations(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        total = TOTAL_AUDIT.read_text(encoding="utf-8")

        self.assertIn("Goal3056", text)
        self.assertIn("File-by-File Findings And Operations", text)
        self.assertIn("v2.3 remains the latest released", text)
        self.assertIn("v2.6 is the active internal pre-release", text)
        self.assertIn("v2.6 release-candidate", total)
        self.assertIn("Triton is paused", text)
        for rel in CURRENT_FACING_DOCS:
            self.assertTrue(rel in text or rel in total)

    def test_current_docs_use_clean_v26_boundary(self) -> None:
        front = self._read("README.md")
        docs_index = self._read("docs/README.md")
        architecture = self._read("docs/current_architecture.md")
        boundary = self._read("docs/partner_acceleration_boundaries.md")
        support = self._read("docs/current_main_support_matrix.md")

        self.assertIn("v2.6 release-candidate RTDL surface", front)
        self.assertIn("docs/learn/partner_choice_for_custom_logic.md", front)
        self.assertIn("RTDL v2.6 is the release-candidate", docs_index)
        self.assertIn("v2.6 partner design is protocol first", architecture)
        self.assertIn("Full residency-first", architecture)
        self.assertIn("roadmap work", architecture)
        self.assertIn("## v2.6 Partner Choice Rule", boundary)
        self.assertIn("Numba is the v2.6 custom CUDA-style continuation lane", boundary)
        self.assertIn("Triton remains paused", boundary)
        self.assertIn("Current docs target: v2.6", support)

    def test_stale_current_facing_phrases_are_removed(self) -> None:
        forbidden = [
            "partner_optix_zero_copy_anyhit",
            "Triton-first",
            "Triton first",
            "default Triton",
            "auto-select Triton",
            "zero-cost",
            "compile-time zero-copy",
            "current v2.3 release",
            "v2.3 users first",
        ]

        offenders: list[str] = []
        for rel in CURRENT_FACING_DOCS:
            text = self._read(rel)
            for phrase in forbidden:
                if phrase in text:
                    offenders.append(f"{rel}: {phrase}")

        self.assertEqual([], offenders)

    def test_optix_partner_tutorial_uses_clean_filename_and_boundary(self) -> None:
        old_path = ROOT / "docs" / "tutorials" / "partner_optix_zero_copy_anyhit.md"
        new_path = ROOT / "docs" / "tutorials" / "partner_optix_column_anyhit.md"

        self.assertFalse(old_path.exists())
        self.assertTrue(new_path.exists())

        tutorials = self._read("docs/tutorials/README.md")
        quickstart = self._read("docs/app_example_quickstart.md")
        tutorial = new_path.read_text(encoding="utf-8")

        self.assertIn("partner_optix_column_anyhit.md", tutorials)
        self.assertIn("partner_optix_column_anyhit.md", quickstart)
        self.assertIn("general zero-copy product guarantee", tutorial)
        self.assertIn("Choosing A Partner For Custom Logic", tutorial)


if __name__ == "__main__":
    unittest.main()
