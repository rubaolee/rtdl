from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1513_v1_5_4_non_pod_docs_linux_validation_2026-05-08.md"


class Goal1513NonPodDocsLinuxValidationTest(unittest.TestCase):
    def test_report_exists(self):
        self.assertTrue(REPORT.exists())

    def test_report_records_linux_environment_and_result(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in [
            "Host: `192.168.1.20`",
            "Hostname: `lx1`",
            "/home/lestat/work/rtdl_codex_local_check",
            "Validated commit: `ffd8858e`",
            "Ran 37 tests",
            "OK",
        ]:
            self.assertIn(phrase, text)

    def test_report_records_exact_test_slice(self):
        text = REPORT.read_text(encoding="utf-8")
        for test_name in [
            "tests.goal1512_v1_5_4_collect_k_pod_intake_failure_taxonomy_test",
            "tests.goal1511_v1_5_4_app_group_deep_dives_test",
            "tests.goal1510_v1_5_4_non_pod_app_classification_test",
            "tests.goal1509_v1_5_4_app_technical_docs_test",
            "tests.goal1506_v1_5_4_optix_collect_k_stage_profile_plan_test",
        ]:
            self.assertIn(test_name, text)

    def test_report_keeps_gpu_claim_boundary(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in [
            "does not add GPU performance evidence",
            "does not authorize public",
            "true zero-copy wording",
            "does not promote `COLLECT_K_BOUNDED`",
            "not a substitute for accepted Goal1506 GPU evidence",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
