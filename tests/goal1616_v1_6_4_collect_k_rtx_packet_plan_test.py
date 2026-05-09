from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal1616_v1_6_4_collect_k_rtx_packet_plan_2026-05-09.md"
GOAL1614_LINUX_JSON = (
    ROOT / "docs/reports/goal1614_v1_6_4_linux_all_backend_bounds_stress_2026-05-09.json"
)
GOAL1615_LINUX_JSON = (
    ROOT / "docs/reports/goal1615_v1_6_4_linux_all_backend_reduced_copy_benchmark_2026-05-09.json"
)


class Goal1616CollectKRtxPacketPlanTest(unittest.TestCase):
    def test_report_records_local_linux_rehearsal_as_non_rtx_performance(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("READY as a prepared RTX packet plan", text)
        self.assertIn("NVIDIA GeForce GTX 1070", text)
        self.assertIn("behavior rehearsal only", text)
        self.assertIn("not representative RTX performance evidence", text)
        self.assertIn("not public speedup evidence", text)

    def test_report_contains_required_backend_pod_commands(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("--backends fake_native embree optix", text)
        self.assertIn("--required-backends fake_native embree optix", text)
        self.assertIn("tests.goal1614_v1_6_4_collect_k_bounds_stress_test", text)
        self.assertIn("tests.goal1615_v1_6_4_collect_k_reduced_copy_benchmark_test", text)
        self.assertIn("make build-optix", text)
        self.assertIn("RTDL_OPTIX_LIB", text)
        self.assertIn("goal1618_v1_6_4_collect_k_packet_runner.py", text)
        self.assertIn("representative_rtx_required_backend_packet", text)

    def test_imported_linux_rehearsal_artifacts_are_all_backend_accepted(self) -> None:
        for path in (GOAL1614_LINUX_JSON, GOAL1615_LINUX_JSON):
            with self.subTest(path=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertTrue(payload["accepted"])
                self.assertEqual(tuple(payload["backends"]), ("fake_native", "embree", "optix"))
                self.assertEqual(tuple(payload["required_backends"]), ("fake_native", "embree", "optix"))
                self.assertEqual(payload["failed"], [])
                self.assertEqual(payload["skipped_required"], [])

    def test_claim_boundary_blocks_release_and_promotion(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("do not authorize stable", text)
        self.assertIn("public speedup wording", text)
        self.assertIn("true zero-copy wording", text)
        self.assertIn("broad RTX/GPU wording", text)
        self.assertIn("release action", text)

    def test_external_reviews_and_consensus_accept_plan_only(self) -> None:
        review_paths = (
            ROOT / "docs/reviews/goal1616_v1_6_4_collect_k_rtx_packet_plan_claude_review_2026-05-09.md",
            ROOT / "docs/reviews/goal1616_v1_6_4_collect_k_rtx_packet_plan_gemini_review_2026-05-09.md",
            ROOT / "docs/reviews/goal1616_v1_6_4_collect_k_rtx_packet_plan_3ai_consensus_2026-05-09.md",
        )

        for path in review_paths:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("ACCEPTED", text)
                self.assertIn("COLLECT_K_BOUNDED", text)
        consensus = review_paths[-1].read_text(encoding="utf-8")
        self.assertIn("GTX behavior rehearsal only", consensus)
        self.assertIn("not representative RTX performance evidence", consensus)
        self.assertIn("does not authorize public speedup", consensus)


if __name__ == "__main__":
    unittest.main()
