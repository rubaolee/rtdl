from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2184_rayjoin_phase0_protocol_and_sample_evidence_2026-05-17.md"
RAW = ROOT / "docs" / "reports" / "goal2184_rayjoin_build_protocol_linux_raw_2026-05-17.txt"
ARTIFACT = ROOT / "docs" / "reports" / "goal2184_rtdl_same_rayjoin_sample_bounded_linux_2026-05-17.json"


class Goal2184RayjoinPhase0ProtocolAndSampleEvidenceTest(unittest.TestCase):
    def test_report_records_real_rayjoin_source_and_protocol(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("02bf6220d6d20b04af77ee20364eced75cc029c9", text)
        self.assertIn("MIT License", text)
        self.assertIn("query_exec", text)
        self.assertIn("polyover_exec", text)
        self.assertIn("`-mode=grid`, `-mode=lbvh`, `-mode=rt`", text)
        self.assertIn("`-query=lsi` and `-query=pip`", text)
        self.assertIn("br_county_clean_25_odyssey_final.txt", text)
        self.assertIn("br_soil_ascii_odyssey_final.txt", text)

    def test_report_records_build_patches_and_sample_status(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        raw = RAW.read_text(encoding="utf-8")

        self.assertIn("local Linux source/protocol/sample evidence complete", text)
        self.assertIn("diff passed", text)
        self.assertIn("OPTIX_ERROR_INTERNAL_COMPILER_ERROR", text)
        self.assertIn("ENABLED_ARCHS 61", raw)
        self.assertIn("GLOG_INCLUDE_DIRS", raw)
        self.assertIn("Goal2184Vec2Hash", raw)

    def test_rtdl_same_sample_artifact_has_pip_lsi_overlay_parity(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(artifact["goal"], "2184")
        self.assertEqual(artifact["commit"], "f54441a4475bbbf96e20ffc28127255c30aeb850")
        self.assertFalse(artifact["claim_boundary"]["full_rayjoin_reproduction"])
        self.assertFalse(artifact["claim_boundary"]["paper_scale_perf_claim_authorized"])
        self.assertFalse(artifact["claim_boundary"]["v2_0_release_authorized"])

        expected = {
            "pip_county512": ("pip", 1430),
            "lsi_county256_soil256_count128": ("lsi", 56),
            "overlay_county128_soil128": ("overlay_seed", 14036),
        }
        for label, (workload, row_count) in expected.items():
            case = artifact["cases"][label]
            self.assertEqual(case["workload"], workload)
            for backend in ("cpu", "embree"):
                backend_payload = case["backends"][backend]
                self.assertEqual(backend_payload["status"], "ok")
                self.assertEqual(backend_payload["row_counts"], [row_count])
                self.assertTrue(backend_payload["all_parity_vs_cpu_python_reference"])

    def test_report_blocks_premature_public_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("still `accept-with-boundary`", text)
        self.assertIn("paper-scale RayJoin reproduction", text)
        self.assertIn("3-AI consensus", text)
        self.assertIn("does not\nauthorize claims that RTDL reproduces RayJoin paper results", text)


if __name__ == "__main__":
    unittest.main()
