from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1515_v1_5_4_embree_native_linux_validation_2026-05-08.md"


class Goal1515EmbreeNativeLinuxValidationTest(unittest.TestCase):
    def test_report_exists(self):
        self.assertTrue(REPORT.exists())

    def test_report_records_environment_and_library(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in [
            "Host: `192.168.1.20`",
            "/home/lestat/work/rtdl_codex_local_check",
            "Validated pushed commit: `6a3739b1`",
            "build/librtdl_embree.so",
            "embree_library_loaded=yes",
        ]:
            self.assertIn(phrase, text)

    def test_report_records_exact_native_embree_slice(self):
        text = REPORT.read_text(encoding="utf-8")
        for test_name in [
            "tests.goal715_embree_fixed_radius_summary_test",
            "tests.goal717_embree_prepared_fixed_radius_summary_test",
            "tests.goal720_embree_prepared_knn_rows_test",
            "tests.goal723_event_hotspot_embree_summary_test",
            "tests.goal724_service_coverage_embree_summary_test",
            "tests.goal736_robot_collision_embree_scaled_test",
        ]:
            self.assertIn(test_name, text)

    def test_report_records_result_and_claim_boundary(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in [
            "Ran 17 tests",
            "OK",
            "CPU-backend validation only",
            "does not add NVIDIA evidence",
            "does not promote `COLLECT_K_BOUNDED`",
            "NVIDIA performance claims",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
