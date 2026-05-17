import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "docs" / "reports" / "goal2213_optix_pip_compact_positive_hits_pod_2026-05-17.json"
REPORT = ROOT / "docs" / "reports" / "goal2213_optix_pip_compact_positive_hits_pod_2026-05-17.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2213_optix_pip_compact_positive_hits_pod"


class Goal2213OptixPipCompactPositiveHitsPodTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_pod_evidence_metadata_matches_compact_pip_run(self) -> None:
        self.assertEqual(self.data["goal"], "2213")
        self.assertEqual(self.data["status"], "parsed")
        self.assertEqual(self.data["workload"], "pip")
        self.assertEqual(self.data["query_count"], 100000)
        self.assertEqual(self.data["reference_backend"], "cpu")
        self.assertEqual(self.data["reference_row_count"], 8686)
        self.assertTrue(self.data["rtdl_commit"].startswith("09b1b412"))
        self.assertIn("69.30.85.202", self.data["pod"])

    def test_all_backends_preserve_same_stream_parity(self) -> None:
        for backend in ("cpu", "embree", "optix"):
            item = self.data["backends"][backend]
            self.assertEqual(item["status"], "ok")
            self.assertTrue(item["all_parity_vs_reference"], backend)
            self.assertEqual(item["parity_reference_backend"], "cpu")
            self.assertTrue(item["row_count_consistent"])
            self.assertEqual(item["row_counts"], [8686, 8686, 8686])

    def test_compact_path_improves_optix_but_still_records_weakness(self) -> None:
        derived = self.data["derived"]
        self.assertGreater(derived["optix_speedup_over_previous_goal2209"], 6.0)
        self.assertLess(derived["optix_vs_previous_goal2209_ratio"], 0.16)
        self.assertLess(derived["optix_vs_cpu_ratio"], 0.25)
        self.assertGreater(derived["optix_vs_embree_ratio"], 5.0)

    def test_claim_boundaries_remain_locked(self) -> None:
        boundary = self.data["claim_boundary"]
        self.assertTrue(boundary["same_contract_with_rayjoin_query_exec"])
        for key in (
            "rtdl_beats_rayjoin_claim_authorized",
            "broad_rt_core_speedup_claim_authorized",
            "v2_0_release_authorized",
        ):
            self.assertFalse(boundary[key])

    def test_report_and_small_artifacts_are_present(self) -> None:
        for name in (
            "progress.log",
            "build_optix.log",
            "rtdl_pip_same_stream.log",
            "rtdl_pip_same_rayjoin_stream.json",
        ):
            self.assertTrue((ARTIFACT_DIR / name).exists(), name)

        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2213", text)
        self.assertIn("6.64x", text)
        self.assertIn("still slower than RTDL Embree", text)
        self.assertIn("does not authorize", text)


if __name__ == "__main__":
    unittest.main()
