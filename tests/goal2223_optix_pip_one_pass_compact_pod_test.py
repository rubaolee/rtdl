import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "docs" / "reports" / "goal2223_optix_pip_one_pass_compact_pod_2026-05-17.json"
REPORT = ROOT / "docs" / "reports" / "goal2223_optix_pip_one_pass_compact_pod_2026-05-17.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2223_optix_pip_one_pass_compact_pod"


class Goal2223OptixPipOnePassCompactPodTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_pod_evidence_metadata_matches_one_pass_run(self) -> None:
        self.assertEqual(self.data["goal"], "2223")
        self.assertEqual(self.data["status"], "parsed")
        self.assertEqual(self.data["workload"], "pip")
        self.assertEqual(self.data["query_count"], 100000)
        self.assertEqual(self.data["reference_backend"], "cpu")
        self.assertEqual(self.data["reference_row_count"], 8686)
        self.assertEqual(self.data["long_repeat_count"], 10)
        self.assertTrue(self.data["rtdl_commit"].startswith("7426c257"))

    def test_long_run_backends_preserve_same_stream_parity(self) -> None:
        for backend in ("embree", "optix"):
            item = self.data["backends_long"][backend]
            self.assertEqual(item["status"], "ok")
            self.assertTrue(item["all_parity_vs_reference"], backend)
            self.assertEqual(item["parity_reference_backend"], "cpu")
            self.assertTrue(item["row_count_consistent"])
            self.assertEqual(item["row_counts"], [8686] * 10)

    def test_one_pass_removes_count_pass_and_improves_timing(self) -> None:
        profile = self.data["profile_repeat_medians"]
        derived = self.data["derived"]
        self.assertEqual(profile["one_pass"], 1)
        self.assertEqual(profile["fallback_chunks"], 0)
        self.assertEqual(profile["candidates"], 8793)
        self.assertEqual(profile["emitted"], 8686)
        self.assertEqual(profile["count_pass_s"], 0.0)
        self.assertGreater(derived["optix_speedup_over_goal2209"], 40.0)
        self.assertGreater(derived["optix_speedup_over_goal2213_compact"], 6.0)
        self.assertGreater(derived["optix_speedup_over_goal2219_two_pass_default"], 1.3)
        self.assertLess(derived["optix_vs_embree_ratio_long"], 1.0)

    def test_claim_boundaries_remain_locked(self) -> None:
        boundary = self.data["claim_boundary"]
        self.assertTrue(boundary["same_contract_with_rayjoin_query_exec"])
        for key in (
            "rtdl_beats_rayjoin_claim_authorized",
            "broad_rt_core_speedup_claim_authorized",
            "v2_0_release_authorized",
        ):
            self.assertFalse(boundary[key])

    def test_report_and_artifacts_are_present(self) -> None:
        for name in (
            "progress.log",
            "build_optix.log",
            "rtdl_pip_one_pass.log",
            "rtdl_pip_one_pass_same_rayjoin_stream.json",
            "rtdl_pip_one_pass_long.log",
            "rtdl_pip_one_pass_long_same_rayjoin_stream.json",
        ):
            self.assertTrue((ARTIFACT_DIR / name).exists(), name)
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2223", text)
        self.assertIn("45.52x", text)
        self.assertIn("faster than Embree", text)
        self.assertIn("RTDL beats RayJoin", text)
        self.assertIn("does not authorize", text)


if __name__ == "__main__":
    unittest.main()
