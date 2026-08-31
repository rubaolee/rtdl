from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
QUICK_TUTORIAL = ROOT / "docs" / "quick_tutorial.md"
REPORT = ROOT / "docs" / "reports" / "goal3794_quick_tutorial_hiprt_autodiscovery_note_2026-06-07.md"


class Goal3794QuickTutorialHiprtAutodiscoveryNoteTest(unittest.TestCase):
    def test_quick_tutorial_documents_autodiscovery_and_override(self) -> None:
        text = QUICK_TUTORIAL.read_text(encoding="utf-8")
        self.assertIn("make build-hiprt  # auto-discovers common HIPRT SDK locations", text)
        self.assertIn("make build-hiprt HIPRT_PREFIX=/path/to/hiprtSdk", text)
        self.assertIn("If auto-discovery does not match your SDK layout", text)

    def test_quick_tutorial_keeps_amd_boundary_explicit(self) -> None:
        text = QUICK_TUTORIAL.read_text(encoding="utf-8")
        self.assertIn("HIPRT can run through Orochi on NVIDIA development hosts", text)
        self.assertIn("that is not AMD", text)
        self.assertIn("AMD HIPRT evidence requires an actual AMD host", text)

    def test_report_is_bounded(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3794 Quick Tutorial HIPRT Autodiscovery Note", text)
        self.assertIn("does not authorize AMD", text)
        self.assertIn("app-specific native-engine logic", text)


if __name__ == "__main__":
    unittest.main()
