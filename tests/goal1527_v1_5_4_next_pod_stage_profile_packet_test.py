from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1527_v1_5_4_next_pod_stage_profile_packet_2026-05-08.md"
RUNNER = ROOT / "scripts" / "goal1506_v1_5_4_run_optix_collect_k_stage_profile_pod.sh"


class Goal1527V154NextPodStageProfilePacketTest(unittest.TestCase):
    def test_packet_points_to_exact_goal1506_runner_and_artifacts(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("bash scripts/goal1506_v1_5_4_run_optix_collect_k_stage_profile_pod.sh", text)
        self.assertIn("COUNTS=\"4097 65537 131072\"", text)
        self.assertIn("REPEATS=5", text)
        self.assertIn("goal1506_v1_5_4_optix_collect_k_stage_profile_probe_2026-05-08.jsonl", text)
        self.assertIn("goal1508_v1_5_4_optix_collect_k_tiled_preflight_2026-05-08.json", text)

    def test_packet_defines_accepted_evidence_conditions(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "accepted_goal1506_evidence=true",
            "row_width2_bounded_multi_tile_sort_merge",
            "expected topology",
            "runner's unittest slice passes",
            "Do not infer performance conclusions from a failed packet",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_packet_keeps_claim_boundary_closed(self) -> None:
        text = " ".join(REPORT.read_text(encoding="utf-8").split())

        for phrase in (
            "does not authorize public speedup wording",
            "broad RTX/GPU claims",
            "true zero-copy wording",
            "whole-app claims",
            "stable `COLLECT_K_BOUNDED` promotion",
            "release action",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_packet_stays_aligned_with_existing_runner(self) -> None:
        packet = REPORT.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")

        self.assertIn("goal1508_v1_5_4_optix_collect_k_tiled_preflight.py", runner)
        self.assertIn("goal1506_v1_5_4_optix_collect_k_stage_profile_probe.py", runner)
        self.assertIn("tests.goal1508_v1_5_4_optix_collect_k_tiled_preflight_test", runner)
        self.assertIn("OPTIX_PREFIX=/root/vendor/optix-sdk", packet)


if __name__ == "__main__":
    unittest.main()
