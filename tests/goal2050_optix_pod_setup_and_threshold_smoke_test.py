import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2050_optix_pod_setup_and_threshold_smoke_2026-05-15.md"
BUILD_LOG = ROOT / "docs" / "reports" / "goal2050_build_optix.log"
SMOKE = ROOT / "docs" / "reports" / "goal2050_optix_hausdorff_threshold_smoke.json"


class Goal2050OptixPodSetupAndThresholdSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.build_log = BUILD_LOG.read_text(encoding="utf-8")
        cls.smoke = json.loads(SMOKE.read_text(encoding="utf-8"))

    def test_build_log_records_optix_library(self):
        self.assertIn("build/librtdl_optix.so", self.build_log)
        self.assertIn("libnvrtc.so.12", self.build_log)
        self.assertIn("libcuda.so.1", self.build_log)

    def test_smoke_matches_oracle_and_uses_threshold_path(self):
        self.assertTrue(self.smoke["matches_oracle"])
        self.assertTrue(self.smoke["oracle_decision_matches"])
        self.assertTrue(self.smoke["oracle_identity_matches"])
        self.assertTrue(self.smoke["rt_core_accelerated"])
        self.assertEqual(self.smoke["native_continuation_backend"], "optix_threshold_count")
        self.assertEqual(self.smoke["directed_a_to_b"]["generic_primitive"], "FIXED_RADIUS_COUNT_THRESHOLD_2D")
        self.assertEqual(self.smoke["directed_a_to_b"]["summary_primitive"], "REDUCE_INT(COUNT)")

    def test_report_blocks_overclaims(self):
        required = [
            "not the exact Hausdorff witness bridge",
            "OptiX zero-copy candidate rows feed the CuPy witness continuation",
            "Joining those into a same-contract OptiX candidate-row plus CuPy witness pipeline remains",
            "v2.0 release readiness",
        ]
        for phrase in required:
            self.assertIn(phrase, self.report)


if __name__ == "__main__":
    unittest.main()
