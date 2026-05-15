import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2064_all_app_v2_current_pod_evidence_audit_2026-05-15.md"
MATRIX = ROOT / "docs" / "reports" / "goal2064_all_app_v2_matrix_after_goal2062.json"
ANYHIT = ROOT / "docs" / "reports" / "goal2064_segment_polygon_v2_partner_anyhit_cupy_l4_2048.json"
CLAIMS = ROOT / "docs" / "reports" / "goal2064_public_v2_claim_boundary_scan_after_current_pod.json"
READINESS = ROOT / "docs" / "reports" / "goal2064_v2_readiness_aggregator_after_current_pod.json"


class Goal2064AllAppV2CurrentPodEvidenceAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        cls.anyhit = json.loads(ANYHIT.read_text(encoding="utf-8"))
        cls.claims = json.loads(CLAIMS.read_text(encoding="utf-8"))
        cls.readiness = json.loads(READINESS.read_text(encoding="utf-8"))

    def test_anyhit_current_pod_row_is_measured_but_mixed(self):
        self.assertEqual(self.anyhit["status"], "pass")
        self.assertEqual(self.anyhit["count"], 2048)
        self.assertTrue(self.anyhit["parity"]["strict_rows_match"])
        cupy = self.anyhit["partners"]["cupy"]
        self.assertEqual(cupy["overflow_check"]["status"], "pass")
        self.assertGreater(cupy["query_median_ratio_vs_v1_8_native"], 1.0)

    def test_matrix_has_no_missing_pod_timing_rows(self):
        self.assertEqual(self.matrix["blockers"], [])
        self.assertFalse(self.matrix["final_pod_batch_needed"])
        counts = self.matrix["counts_by_comparison_status"]
        self.assertNotIn("needs-pod-timing", counts)
        self.assertNotIn("needs-current-pod-rerun", counts)
        self.assertEqual(counts["pod-evidence-collected-mixed"], 2)
        self.assertFalse(self.matrix["release_claim_boundary"]["all_apps_have_measured_v2_speedup"])
        self.assertFalse(self.matrix["release_claim_boundary"]["v2_0_release_authorized"])

    def test_claim_scan_and_readiness_still_block_release(self):
        self.assertEqual(self.claims["status"], "pass")
        self.assertEqual(self.claims["findings"], [])
        self.assertFalse(self.claims["claim_boundary"]["v2_0_release_authorized"])
        self.assertEqual(self.readiness["status"], "blocked")
        self.assertEqual(self.readiness["missing_pod_artifacts"], [])
        self.assertIn("final v2.0 release consensus missing", self.readiness["blockers"])

    def test_report_states_boundaries(self):
        required = [
            "no missing pod-timing rows",
            "It is not a speedup",
            "pod-evidence-collected-mixed",
            "final Claude v2.0 release review missing",
            "v2.0 release readiness",
            "all apps have measured v2 speedup",
            "arbitrary partner-program acceleration",
            "`accept-with-boundary`",
        ]
        for phrase in required:
            self.assertIn(phrase, self.report)


if __name__ == "__main__":
    unittest.main()
