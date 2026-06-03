from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3149_v2_8_front_door_completion_packet_2026-06-03.md"
ARTIFACTS = (
    ROOT / "docs" / "reports" / "goal3143_pod_artifacts" / "hausdorff_partner_exact_numba_pod_probe_2026-06-03.json",
    ROOT / "docs" / "reports" / "goal3145_pod_artifacts" / "segmented_minmax_front_door_pod_probe_2026-06-03.json",
    ROOT / "docs" / "reports" / "goal3147_pod_artifacts" / "compact_mask_front_door_pod_probe_2026-06-03.json",
)
REVIEWS = (
    ROOT / "docs" / "reviews" / "goal3144_claude_review_goal3143_hausdorff_partner_exact_numba_front_door_2026-06-03.md",
    ROOT / "docs" / "reviews" / "goal3146_claude_review_goal3145_segmented_minmax_front_door_2026-06-03.md",
    ROOT / "docs" / "reviews" / "goal3148_claude_review_goal3147_compact_mask_front_door_2026-06-03.md",
)


class Goal3149V28FrontDoorCompletionPacketTest(unittest.TestCase):
    def test_supported_operations_cover_current_typed_result_continuations(self) -> None:
        summary = rt.v2_8_segmented_typed_stream_adapter_summary()

        supported = set(summary["partner_consumer_supported_operations"])
        allowed = set(rt.V2_8_TYPED_RESULT_STREAM_ALLOWED_CONTINUATIONS)
        self.assertEqual(supported, allowed)
        self.assertEqual(summary["partner_consumer_deferred_operations"], {})
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        self.assertFalse(summary["rt_core_speedup_claim_authorized"])
        self.assertFalse(summary["true_zero_copy_claim_authorized"])
        self.assertFalse(summary["automatic_partner_selection_allowed"])

    def test_report_lists_operations_evidence_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for operation in rt.V2_8_TYPED_RESULT_STREAM_ALLOWED_CONTINUATIONS:
            self.assertIn(f"`{operation}`", text)
        for phrase in (
            "`V2_8_SEGMENTED_TYPED_STREAM_PARTNER_CONSUMER_DEFERRED_OPERATIONS` is now empty",
            "Ran 46 tests in 0.885s",
            "719cfc34",
            "NVIDIA RTX 4000 Ada",
            "does not authorize",
            "The user still chooses the partner explicitly",
            "device-resident result streams instead of host-side canonical output shaping",
        ):
            self.assertIn(phrase, text)

    def test_artifacts_and_reviews_are_present_and_non_authorizing(self) -> None:
        for artifact_path in ARTIFACTS:
            with self.subTest(artifact=artifact_path.name):
                artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
                self.assertTrue(artifact["all_match"])
                for value in artifact["claim_boundary"].values():
                    self.assertFalse(value)

        verdict_text = "\n".join(path.read_text(encoding="utf-8") for path in REVIEWS)
        self.assertIn("accept-with-boundary", verdict_text)
        self.assertIn("Verdict:** `accept`", verdict_text)
        self.assertIn("not authorize", verdict_text.lower())


if __name__ == "__main__":
    unittest.main()
