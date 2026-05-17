from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2188_rayjoin_rtx_pod_build_and_bounded_rtdl_evidence_2026-05-17.md"
NATIVE = ROOT / "docs" / "reports" / "goal2188_rayjoin_native_pod_summary_2026-05-17.json"
PIP = ROOT / "docs" / "reports" / "goal2188_pod_rtdl_rayjoin_pip_county512_2026-05-17.json"
LSI = ROOT / "docs" / "reports" / "goal2188_pod_rtdl_rayjoin_lsi_count512_2026-05-17.json"
OVERLAY = ROOT / "docs" / "reports" / "goal2188_pod_rtdl_rayjoin_overlay_count512_2026-05-17.json"
RAW_SAMPLE = ROOT / "docs" / "reports" / "goal2188_rayjoin_native_pod_sample_protocol_raw_2026-05-17.txt"
RAW_QUERY = ROOT / "docs" / "reports" / "goal2188_rayjoin_native_pod_query_protocol_raw_2026-05-17.txt"


class Goal2188RayjoinRtxPodBuildAndBoundedRtdlEvidenceTest(unittest.TestCase):
    def test_report_records_pod_environment_and_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("NVIDIA RTX A5000", text)
        self.assertIn("cuda_12.8", text)
        self.assertIn("02bf6220d6d20b04af77ee20364eced75cc029c9", text)
        self.assertIn("8af5f62d3062d757ede52ad4309f40ebcc6dcc6c", text)
        self.assertIn("No RTDL native engine code is customized for RayJoin", text)
        self.assertIn("does not claim full\npaper reproduction", text)
        self.assertIn("not a direct same-contract performance fight", text)
        self.assertIn("accept-with-boundary", text)

    def test_rayjoin_native_artifact_has_real_optix_launches_and_diff_passes(self) -> None:
        data = json.loads(NATIVE.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], "2188")
        self.assertIn("RTX A5000", data["pod"]["gpu"])
        self.assertEqual(data["rayjoin_commit"], "02bf6220d6d20b04af77ee20364eced75cc029c9")

        overlay = data["rayjoin_overlay_sample"]
        for mode in ("grid", "lbvh", "rt"):
            self.assertTrue(overlay[mode]["answer_diff_passed"])
        self.assertGreater(overlay["rt"]["optix_launch_count"], 0)
        self.assertLess(
            overlay["rt"]["timing_ms"]["Intersection edges"],
            overlay["grid"]["timing_ms"]["Intersection edges"],
        )

        query = data["rayjoin_query_generated_100k"]
        self.assertGreater(query["lsi"]["rt"]["optix_launch_count"], 0)
        self.assertGreater(query["pip"]["rt"]["optix_launch_count"], 0)
        self.assertLess(query["lsi"]["rt"]["timing_ms"]["Query"], query["lsi"]["grid"]["timing_ms"]["Query"])
        self.assertLess(query["pip"]["rt"]["timing_ms"]["Query"], query["pip"]["lbvh"]["timing_ms"]["Query"])
        self.assertTrue(query["pip"]["rt"]["built_in_check_passed"])

        self.assertFalse(data["claim_boundary"]["paper_scale_perf_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["v2_0_release_authorized"])

    def test_rtdl_artifacts_preserve_parity_and_goal_metadata(self) -> None:
        artifacts = [json.loads(path.read_text(encoding="utf-8")) for path in (PIP, LSI, OVERLAY)]

        for artifact in artifacts:
            self.assertEqual(artifact["goal"], "2188")
            self.assertEqual(artifact["source_runner_goal"], "2159")
            self.assertEqual(artifact["commit"], "8af5f62d3062d757ede52ad4309f40ebcc6dcc6c")
            self.assertFalse(artifact["claim_boundary"]["paper_scale_perf_claim_authorized"])
            self.assertFalse(artifact["claim_boundary"]["v2_0_release_authorized"])

        pip_case = artifacts[0]["cases"]["pip_county512"]["backends"]
        self.assertEqual(pip_case["optix"]["row_counts"], [1430, 1430, 1430])
        self.assertTrue(pip_case["optix"]["all_parity_vs_cpu_python_reference"])
        self.assertLess(pip_case["optix"]["app_elapsed_sec_median"], pip_case["cpu"]["app_elapsed_sec_median"])

        lsi_case = artifacts[1]["cases"]["lsi_county256_soil256_count512"]["backends"]
        self.assertEqual(lsi_case["optix"]["row_counts"], [269, 269, 269])
        self.assertTrue(lsi_case["cupy_lsi_bruteforce"]["all_parity_vs_cpu_python_reference"])
        self.assertLess(lsi_case["optix"]["app_elapsed_sec_median"], lsi_case["cupy_lsi_bruteforce"]["app_elapsed_sec_median"])

        overlay_case = artifacts[2]["cases"]["overlay_county512_soil512"]["backends"]
        self.assertEqual(overlay_case["optix"]["row_counts"], [233766, 233766, 233766])
        self.assertTrue(overlay_case["optix"]["all_parity_vs_cpu_python_reference"])
        self.assertLess(overlay_case["optix"]["app_elapsed_sec_median"], overlay_case["embree"]["app_elapsed_sec_median"])

    def test_raw_logs_are_retained(self) -> None:
        self.assertIn("polyover sample mode=rt", RAW_SAMPLE.read_text(encoding="utf-8"))
        self.assertIn("optixLaunch", RAW_SAMPLE.read_text(encoding="utf-8"))
        self.assertIn("query workload=pip mode=rt", RAW_QUERY.read_text(encoding="utf-8"))
        self.assertIn("Map: 0 passed check", RAW_QUERY.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
