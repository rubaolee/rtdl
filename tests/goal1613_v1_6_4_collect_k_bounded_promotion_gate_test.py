from __future__ import annotations

import json
import tempfile
from pathlib import Path
import unittest

from scripts import goal1613_v1_6_4_collect_k_bounded_promotion_gate as goal1613


ROOT = Path(__file__).resolve().parents[1]


class Goal1613CollectKBoundedPromotionGateTest(unittest.TestCase):
    def test_gate_defers_stable_promotion_with_exact_missing_evidence(self) -> None:
        gate = goal1613.validate_gate(goal1613.build_gate())

        self.assertEqual(gate["goal"], "Goal1613")
        self.assertEqual(gate["version_slot"], "v1.6.4")
        self.assertEqual(gate["primitive"], "COLLECT_K_BOUNDED")
        self.assertEqual(gate["decision"], "defer_stable_promotion_keep_experimental")
        self.assertTrue(gate["accepted_as_gate"])
        self.assertFalse(gate["stable_promotion_ready"])
        self.assertEqual(
            tuple(gate["missing_promotion_evidence"]),
            goal1613.MISSING_PROMOTION_EVIDENCE,
        )

    def test_satisfied_evidence_files_exist(self) -> None:
        gate = goal1613.validate_gate(goal1613.build_gate())

        self.assertEqual(len(gate["satisfied_evidence"]), len(goal1613.SATISFIED_EVIDENCE))
        self.assertEqual(gate["missing_satisfied_evidence_files"], ())
        for record in gate["satisfied_evidence"]:
            with self.subTest(path=record["path"]):
                self.assertTrue(record["exists"])
                self.assertTrue((ROOT / record["path"]).exists())

    def test_semantic_fields_cover_fail_closed_and_buffer_contracts(self) -> None:
        gate = goal1613.validate_gate(goal1613.build_gate())

        for field in (
            "capacity_metadata",
            "valid_count_metadata",
            "overflow_flag",
            "fail_closed_overflow",
            "bounded_result_buffer_contract",
            "prepared_host_output_buffer_reuse",
            "typed_contiguous_host_input_measurement",
            "embree_optix_parity_where_claimed",
        ):
            with self.subTest(field=field):
                self.assertIn(field, gate["required_semantic_fields"])
                self.assertTrue(gate["semantic_field_status"][field])

    def test_authorization_flags_remain_false(self) -> None:
        gate = goal1613.validate_gate(goal1613.build_gate())

        self.assertEqual(set(gate["authorization_flags"]), set(goal1613.FALSE_AUTHORIZATION_FLAGS))
        for flag in goal1613.FALSE_AUTHORIZATION_FLAGS:
            with self.subTest(flag=flag):
                self.assertIs(gate["authorization_flags"][flag], False)

    def test_generated_artifacts_preserve_claim_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            json_path = Path(tmp) / "gate.json"
            md_path = Path(tmp) / "gate.md"
            rc = goal1613.main(["--json-out", str(json_path), "--md-out", str(md_path)])

            self.assertEqual(rc, 0)
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            markdown = md_path.read_text(encoding="utf-8")

        self.assertEqual(payload["decision"], "defer_stable_promotion_keep_experimental")
        self.assertIn("stable promotion deferred", markdown)
        self.assertIn("COLLECT_K_BOUNDED", markdown)
        self.assertIn("remains experimental", markdown)
        self.assertIn("does not authorize stable primitive promotion", markdown)
        self.assertIn("public speedup wording", markdown)
        self.assertIn("true zero-copy wording", markdown)

    def test_external_reviews_and_consensus_exist_without_promotion(self) -> None:
        review_paths = (
            ROOT
            / "docs/reviews/goal1613_v1_6_4_collect_k_bounded_promotion_gate_claude_review_2026-05-09.md",
            ROOT
            / "docs/reviews/goal1613_v1_6_4_collect_k_bounded_promotion_gate_gemini_review_2026-05-09.md",
            ROOT
            / "docs/reviews/goal1613_v1_6_4_collect_k_bounded_promotion_gate_3ai_consensus_2026-05-09.md",
        )

        for path in review_paths:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("ACCEPTED", text)
                self.assertIn("COLLECT_K_BOUNDED", text)
        consensus = review_paths[-1].read_text(encoding="utf-8")
        self.assertIn("remains experimental", consensus)
        self.assertIn("does not authorize stable primitive promotion", consensus)
        self.assertIn("public speedup", consensus)


if __name__ == "__main__":
    unittest.main()
