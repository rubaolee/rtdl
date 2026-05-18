from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2329_rayjoin_local_linux_multihead_progress_2026-05-18.md"
SMOKE = ROOT / "docs" / "reports" / "goal2327_rayjoin_local_linux_smoke"
STREAMS = ROOT / "docs" / "reports" / "goal2327_rayjoin_local_linux_streams"


class Goal2329RayJoinLocalLinuxMultiheadProgressTest(unittest.TestCase):
    def test_report_records_local_linux_boundary_and_next_pod_command(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("local-linux-smoke-complete-pod-still-needed", text)
        self.assertIn("NVIDIA GeForce GTX 1070", text)
        self.assertIn("RayJoin-exported same-query stream replay", text)
        self.assertIn("does not authorize", text)
        self.assertIn("goal2327_rayjoin_pod_perf_runner.sh", text)

    def test_smoke_artifacts_keep_claim_boundary_locked(self) -> None:
        boundary = json.loads((SMOKE / "claim_boundary.json").read_text(encoding="utf-8"))
        self.assertFalse(boundary["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(boundary["paper_scale_perf_claim_authorized"])
        self.assertFalse(boundary["v2_0_release_authorized"])
        self.assertTrue((SMOKE / "summary.md").exists())

    def test_demo_stream_prepared_outputs_are_consistent(self) -> None:
        comparison = json.loads((STREAMS / "prepared_comparison_65536.json").read_text(encoding="utf-8"))
        self.assertEqual(comparison["commit"][:8], "a83f0ff4")
        self.assertTrue(comparison["lsi"]["raw_rows"]["value_consistent"])
        self.assertTrue(comparison["lsi"]["scalar_count"]["value_consistent"])
        self.assertTrue(comparison["pip"]["positive_rows"]["value_consistent"])
        self.assertTrue(comparison["pip"]["scalar_count"]["value_consistent"])
        self.assertFalse(comparison["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"])

    def test_all_backend_demo_stream_parity_is_true(self) -> None:
        for name in [
            "lsi_demo_stream_4096_all_backend.json",
            "pip_demo_stream_4096_all_backend.json",
        ]:
            payload = json.loads((STREAMS / name).read_text(encoding="utf-8"))
            for backend in ["cpu_python_reference", "cpu", "embree", "optix"]:
                self.assertIn(backend, payload["backends"])
                self.assertTrue(payload["backends"][backend]["all_parity_vs_reference"])


if __name__ == "__main__":
    unittest.main()
