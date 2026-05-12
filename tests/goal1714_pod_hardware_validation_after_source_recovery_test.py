import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal1714_pod_hardware_validation_after_source_recovery_2026-05-12.md"
)


class Goal1714PodHardwareValidationAfterSourceRecoveryTest(unittest.TestCase):
    def test_report_records_pod_identity_and_working_key_boundary(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "root@157.157.221.29 -p 22464",
            "C:\\Users\\Lestat\\.ssh\\id_ed25519_rtdl_codex_current_pod",
            "default key path did not authenticate",
            "NVIDIA RTX 4000 Ada Generation",
            "driver: 550.163.01",
            "CUDA version: 12.8",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_records_dependency_setup_and_build_outputs(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "libgeos-dev libembree-dev",
            "OptiX SDK v8.0.0",
            "make build-embree",
            "make build-optix OPTIX_PREFIX=/opt/optix",
            "build/librtdl_embree.so 393264 bytes",
            "build/librtdl_optix.so 843984 bytes",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_records_gates_and_results(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Ran 83 tests in 3.555s",
            "OK (skipped=1)",
            "Ran 34 tests in 7.160s",
            "OK (skipped=5)",
            "Ran 117 tests in 5.250s",
            "OK (skipped=6)",
            "Ran 4 tests in 0.006s",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_keeps_tarball_and_release_boundaries(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "goal1204_rtdl_source_2026-05-01.tar.gz",
            "extracted_no_goal1204_tarball",
            "Goal1660 requires local v1.0 tag",
            "aee364d677442994958d87dacf3f814360c20ffa",
            "Ran 13 tests in 8.654s",
            "validates the v1.6.11/v1.0 manifest preparation",
            "not the full v1.6.11 release performance matrix",
            "needs-more-evidence",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
