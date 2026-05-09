from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1605_v1_6_windows_linux_optix_validation_2026-05-09.md"
WINDOWS_TRANSCRIPT = ROOT / "docs" / "reports" / "goal1605_windows_release_slice_cmd_2026-05-09.txt"
LINUX_TRANSCRIPT = ROOT / "docs" / "reports" / "goal1605_linux_release_slice_clean_2026-05-09.txt"
OPTIX_TRANSCRIPT = ROOT / "docs" / "reports" / "goal1605_linux_nvidia_optix_slice_clean_2026-05-09.txt"


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8", errors="replace").split())


class Goal1605V16WindowsLinuxOptixValidationTest(unittest.TestCase):
    def test_windows_release_slice_is_green(self):
        text = _flat(WINDOWS_TRANSCRIPT)
        self.assertIn("ae92aa8eabc969da856ea730c7b82e19345ca3a3", text)
        self.assertIn("Ran 38 tests", text)
        self.assertIn("OK", text)
        self.assertNotIn("FAILED", text)
        self.assertNotIn("ERROR:", text)

    def test_linux_release_slice_is_green(self):
        text = _flat(LINUX_TRANSCRIPT)
        self.assertIn("ae92aa8eabc969da856ea730c7b82e19345ca3a3", text)
        self.assertIn("Ran 38 tests", text)
        self.assertIn("OK", text)
        self.assertNotIn("FAILED", text)
        self.assertNotIn("ERROR:", text)

    def test_linux_optix_slice_records_real_nvidia_gpu_and_is_green(self):
        text = _flat(OPTIX_TRANSCRIPT)
        self.assertIn("ae92aa8eabc969da856ea730c7b82e19345ca3a3", text)
        self.assertIn("NVIDIA GeForce GTX 1070", text)
        self.assertIn("580.126.09", text)
        self.assertIn("Ran 33 tests", text)
        self.assertIn("OK", text)
        self.assertNotIn("FAILED", text)
        self.assertNotIn("ERROR:", text)

    def test_report_preserves_claim_boundaries(self):
        text = _flat(REPORT)
        for phrase in [
            "does not publish `v1.6`",
            "does not authorize release/tag action",
            "does not add public speedup wording",
            "does not promote `COLLECT_K_BOUNDED`",
            "not a speedup claim",
            "not a broad claim that every OptiX path uses NVIDIA RT cores",
            "package-install support",
            "true zero-copy wording",
            "partner tensor handoff claims",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
