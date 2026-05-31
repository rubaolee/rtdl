from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2754_pod_artifacts"
    / "goal2754_current_v25_hit_stream_partner_perf_probe_69_30_85_171_2026-05-30.json"
)
REPORT = ROOT / "docs" / "reports" / "goal2754_current_v25_hit_stream_partner_perf_probe_2026-05-30.md"


class Goal2754CurrentV25HitStreamPerfProbeTest(unittest.TestCase):
    def test_pod_artifact_preserves_correctness_and_claim_boundaries(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["all_correct"])
        self.assertTrue(payload["no_public_speedup_claim"])
        self.assertEqual(payload["git_head"], "02c049fd809c2d8e1cad5c2a1de8d9b7024697da")

        device_cases = [
            case
            for case in payload["cases"]
            if case["backend"] == "paper_rt_optix_device_hit_stream_triton_prepared"
        ]
        self.assertEqual(len(device_cases), 10)
        for case in device_cases:
            with self.subTest(row_count=case["row_count"], mode=case["mode"]):
                self.assertTrue(case["matches_cpu_reference"])
                self.assertTrue(case["native_device_column_path_used"])
                self.assertTrue(case["host_row_bridge_bypassed"])
                self.assertTrue(case["torch_carrier_same_pointer_evidence_observed"])
                self.assertFalse(case["true_zero_copy_authorized"])

    def test_probe_report_states_primitive_first_interpretation(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("primitive-first planner behavior", text)
        self.assertIn("not a generic hit-stream failure", text)
        self.assertIn("true_zero_copy_authorized=false", text)
        self.assertIn("fused gather+continuation", text)


if __name__ == "__main__":
    unittest.main()
