from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "docs" / "release_reports" / "v0_9_8"


class Goal1219V098ReleasePackageTest(unittest.TestCase):
    def test_release_package_files_exist_and_are_released(self) -> None:
        for name in [
            "README.md",
            "release_statement.md",
            "support_matrix.md",
            "audit_report.md",
            "tag_preparation.md",
        ]:
            with self.subTest(name=name):
                text = (PACKAGE_DIR / name).read_text(encoding="utf-8")
                self.assertIn("Status: released as `v0.9.8`", text)
                self.assertNotIn("release-prepared as `v0.9.8`; not tagged or published", text)

    def test_package_preserves_public_claim_boundaries(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in PACKAGE_DIR.glob("*.md"))
        self.assertIn("Reviewed public RTX wording rows: `11`", combined)
        self.assertIn("road_hazard_screening / prepared_native_compact_summary_40k", combined)
        self.assertIn("database_analytics` public speedup wording: `blocked`", combined)
        self.assertIn("polygon_set_jaccard` public speedup wording: `blocked`", combined)
        self.assertIn("whole-app road-hazard speedup", combined)
        self.assertNotIn("database_analytics / public speedup", combined)
        self.assertNotIn("polygon_set_jaccard / public speedup", combined)

    def test_package_records_gate_evidence_and_no_pod_requirement(self) -> None:
        readme = (PACKAGE_DIR / "README.md").read_text(encoding="utf-8")
        audit = (PACKAGE_DIR / "audit_report.md").read_text(encoding="utf-8")
        tag_prep = (PACKAGE_DIR / "tag_preparation.md").read_text(encoding="utf-8")
        self.assertIn("Goal1214 full local discovery", readme)
        self.assertIn("`2366` tests OK", audit)
        self.assertIn("Goal1215 release-surface documentation audit: `64` tests OK", audit)
        self.assertIn("No immediate pod is required", tag_prep)
        self.assertIn("Goal1220 final authorization: accepted by Codex and Gemini", tag_prep)


if __name__ == "__main__":
    unittest.main()
