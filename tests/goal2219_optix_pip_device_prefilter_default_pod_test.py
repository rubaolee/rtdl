import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "docs" / "reports" / "goal2219_optix_pip_device_prefilter_default_pod_2026-05-17.json"
REPORT = ROOT / "docs" / "reports" / "goal2219_optix_pip_device_prefilter_default_pod_2026-05-17.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2219_optix_pip_device_prefilter_default_pod"


class Goal2219OptixPipDevicePrefilterDefaultPodTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_pod_evidence_metadata_matches_default_prefilter_run(self) -> None:
        self.assertEqual(self.data["goal"], "2219")
        self.assertEqual(self.data["status"], "parsed")
        self.assertEqual(self.data["workload"], "pip")
        self.assertEqual(self.data["query_count"], 100000)
        self.assertEqual(self.data["reference_backend"], "cpu")
        self.assertEqual(self.data["reference_row_count"], 8686)
        self.assertTrue(self.data["rtdl_commit"].startswith("4c839305"))
        self.assertIn("69.30.85.202", self.data["pod"])

    def test_all_backends_preserve_same_stream_parity(self) -> None:
        for backend in ("cpu", "embree", "optix"):
            item = self.data["backends"][backend]
            self.assertEqual(item["status"], "ok")
            self.assertTrue(item["all_parity_vs_reference"], backend)
            self.assertEqual(item["parity_reference_backend"], "cpu")
            self.assertTrue(item["row_count_consistent"])
            self.assertEqual(item["row_counts"], [8686, 8686, 8686])

    def test_default_prefilter_collapses_candidate_explosion(self) -> None:
        profile = self.data["profile_repeat_medians"]
        derived = self.data["derived"]
        self.assertEqual(profile["candidates"], 8793)
        self.assertEqual(profile["emitted"], 8686)
        self.assertGreater(derived["candidate_reduction_vs_goal2213"], 300.0)
        self.assertGreater(derived["optix_speedup_over_goal2213_compact"], 5.0)
        self.assertGreater(derived["optix_speedup_over_goal2209"], 30.0)
        self.assertLess(derived["optix_vs_cpu_ratio"], 0.05)
        self.assertGreater(derived["optix_vs_embree_ratio"], 1.0)

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
            "rtdl_pip_default.log",
            "rtdl_pip_default_same_rayjoin_stream.json",
        ):
            self.assertTrue((ARTIFACT_DIR / name).exists(), name)
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2219", text)
        self.assertIn("No `RTDL_OPTIX_POINT_PRIMITIVE_ANYHIT_DEVICE_PREFILTER` environment variable was set", text)
        self.assertIn("33.75x", text)
        self.assertIn("RTDL beats RayJoin", text)
        self.assertIn("does not authorize", text)


if __name__ == "__main__":
    unittest.main()
