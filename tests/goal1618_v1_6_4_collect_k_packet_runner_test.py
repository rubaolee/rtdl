from __future__ import annotations

import json
import tempfile
from pathlib import Path
import unittest

from scripts import goal1618_v1_6_4_collect_k_packet_runner as goal1618


class Goal1618CollectKPacketRunnerTest(unittest.TestCase):
    def test_packet_runner_accepts_default_fake_native_subpackages(self) -> None:
        payload = goal1618.validate_packet(goal1618.run_packet())

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["status"], "accepted_packet_execution")
        self.assertEqual(payload["failed_subpackages"], ())
        self.assertTrue(payload["subpackages"]["goal1614_bounds_stress"]["accepted"])
        self.assertTrue(payload["subpackages"]["goal1615_reduced_copy_benchmark"]["accepted"])

    def test_packet_runner_records_backends_and_required_backends(self) -> None:
        payload = goal1618.validate_packet(
            goal1618.run_packet(backends=("fake_native",), required_backends=("fake_native",))
        )

        self.assertEqual(payload["backends"], ("fake_native",))
        self.assertEqual(payload["required_backends"], ("fake_native",))
        self.assertEqual(
            tuple(payload["manifest"]["subgoals"]),
            ("Goal1614", "Goal1615"),
        )

    def test_packet_runner_keeps_authorization_flags_false(self) -> None:
        payload = goal1618.validate_packet(goal1618.run_packet())

        for flag in (
            "representative_rtx_performance_evidence_authorized",
            "public_speedup_wording_authorized",
            "true_zero_copy_wording_authorized",
            "stable_collect_k_promotion_authorized",
            "broad_rtx_wording_authorized",
            "release_action_authorized",
        ):
            with self.subTest(flag=flag):
                self.assertIs(payload[flag], False)
        self.assertIs(payload["manifest"]["broad_rtx_wording_authorized"], False)

    def test_artifact_generation_preserves_packet_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            json_path = Path(tmp) / "packet.json"
            md_path = Path(tmp) / "packet.md"
            rc = goal1618.main(["--json-out", str(json_path), "--md-out", str(md_path)])

            self.assertEqual(rc, 0)
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            markdown = md_path.read_text(encoding="utf-8")

        self.assertTrue(payload["accepted"])
        self.assertIn("Goal1614 bounds stress", markdown)
        self.assertIn("Goal1615 reduced-copy benchmark", markdown)
        self.assertIn("packet-execution evidence", markdown)
        self.assertIn("Timing remains diagnostic only", markdown)
        self.assertIn("does not authorize public speedup wording", markdown)
        self.assertIn("stable COLLECT_K_BOUNDED promotion", markdown)

    def test_external_reviews_and_consensus_accept_runner_only(self) -> None:
        root = Path(__file__).resolve().parents[1]
        review_paths = (
            root / "docs/reviews/goal1618_v1_6_4_collect_k_packet_runner_claude_review_2026-05-09.md",
            root / "docs/reviews/goal1618_v1_6_4_collect_k_packet_runner_gemini_review_2026-05-09.md",
            root / "docs/reviews/goal1618_v1_6_4_collect_k_packet_runner_3ai_consensus_2026-05-09.md",
        )

        for path in review_paths:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("ACCEPTED", text)
                self.assertIn("COLLECT_K_BOUNDED", text)
        consensus = review_paths[-1].read_text(encoding="utf-8")
        self.assertIn("single packet-execution runner", consensus)
        self.assertIn("does\nnot authorize representative RTX performance evidence", consensus)


if __name__ == "__main__":
    unittest.main()
