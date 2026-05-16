import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2120_clean_a5000_optix_hd_rerun_2026-05-16.md"
SMOKE = ROOT / "docs" / "reports" / "goal2120_new_pod_hd_smoke_512.json"
ORACLE_ROWS = [
    ROOT / "docs" / "reports" / "goal2120_new_pod_hd_oracle_radius_4096.json",
    ROOT / "docs" / "reports" / "goal2120_new_pod_hd_oracle_radius_8192.json",
    ROOT / "docs" / "reports" / "goal2120_new_pod_hd_oracle_radius_32768.json",
    ROOT / "docs" / "reports" / "goal2120_new_pod_hd_oracle_radius_65536.json",
]


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class Goal2120CleanA5000OptixHdRerunTest(unittest.TestCase):
    def test_report_records_clean_pod_boundary(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("RTDL OptiX native controls passed", text)
        self.assertIn("RT-core Hausdorff speedup: needs-more-evidence", text)
        self.assertIn("X-HD-style algorithm readiness: needs-more-evidence", text)
        self.assertIn("algorithmic formulation is the blocker", text)
        self.assertIn("id_ed25519_rtdl_codex", text)

    def test_smoke_artifact_has_correct_and_bounded_rt_paths(self):
        data = _load(SMOKE)
        results = data["results"]

        v2_user = results["rtdl_v2_user_cuda"]
        self.assertTrue(v2_user["ok"])
        self.assertTrue(v2_user["matches_exact_reference"])
        self.assertTrue(v2_user["metadata"]["uses_rtdl"])
        self.assertTrue(v2_user["metadata"]["uses_partner"])
        self.assertFalse(v2_user["metadata"]["uses_rt_cores"])

        threshold = results["rtdl_rt_threshold_search"]
        self.assertTrue(threshold["ok"])
        self.assertTrue(threshold["metadata"]["uses_rt_cores"])
        self.assertFalse(threshold["exact_value"])
        self.assertFalse(threshold["matches_exact_reference"])

        nearest = results["rtdl_rt_nearest_witness"]
        self.assertTrue(nearest["ok"])
        self.assertTrue(nearest["metadata"]["uses_rt_cores"])
        self.assertTrue(nearest["exact_value"])
        self.assertTrue(nearest["matches_exact_reference"])

        self.assertGreater(nearest["elapsed_sec"], v2_user["elapsed_sec"])

    def test_oracle_radius_artifacts_are_exact_but_not_speedup_evidence(self):
        for path in ORACLE_ROWS:
            with self.subTest(path=path.name):
                data = _load(path)
                results = data["results"]
                v2_user = results["rtdl_v2_user_cuda"]
                rt_oracle = results["rtdl_rt_nearest_witness_oracle_radius"]

                self.assertTrue(v2_user["ok"])
                self.assertTrue(v2_user["matches_exact_reference"])
                self.assertTrue(v2_user["metadata"]["uses_rtdl"])
                self.assertTrue(v2_user["metadata"]["uses_partner"])
                self.assertFalse(v2_user["metadata"]["uses_rt_cores"])

                self.assertTrue(rt_oracle["ok"])
                self.assertTrue(rt_oracle["exact_value"])
                self.assertTrue(rt_oracle["matches_exact_reference"])
                self.assertTrue(rt_oracle["metadata"]["uses_rt_cores"])
                self.assertEqual(
                    rt_oracle["metadata"]["role"],
                    "diagnostic_lower_bound",
                )
                self.assertEqual(
                    rt_oracle["oracle_radius_source"],
                    "exact_reference_plus_slack",
                )
                self.assertGreater(rt_oracle["elapsed_sec"], v2_user["elapsed_sec"])


if __name__ == "__main__":
    unittest.main()
