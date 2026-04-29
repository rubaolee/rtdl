from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.goal1102_current_contract_baseline_intake import EXPECTED
from scripts.goal1102_current_contract_baseline_intake import build_intake
from scripts.goal1102_current_contract_baseline_intake import to_markdown


def _artifact(expected: dict, *, matches_oracle=True) -> dict:
    result = {
        "query_count": expected["query_count"],
        "matches_oracle": matches_oracle,
    }
    if expected.get("barnes_tree_depth") is not None:
        result["barnes_tree_depth"] = expected["barnes_tree_depth"]
    if expected.get("hit_threshold") is not None:
        result["hit_threshold"] = expected["hit_threshold"]
    return {
        "schema_version": "goal1101_current_contract_non_optix_baseline_v1",
        "app": expected["app"],
        "path_name": expected["path_name"],
        "backend": expected["backend"],
        "source_commit": "test-commit",
        "public_speedup_claim_authorized": False,
        "scenario": {
            "scenario": expected["scenario"],
            "result": result,
            "timings_sec": {"native_query_sec": {"median_sec": 0.123}},
        },
    }


class Goal1102CurrentContractBaselineIntakeTest(unittest.TestCase):
    def test_default_intake_waits_when_artifacts_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            payload = build_intake(Path(tmpdir))

        self.assertTrue(payload["valid"])
        self.assertFalse(payload["artifact_set_complete"])
        self.assertEqual(payload["overall_status"], "waiting_for_baseline_artifacts")
        self.assertEqual(payload["summary"]["row_count"], 4)
        self.assertEqual(payload["summary"]["public_speedup_claim_authorized_count"], 0)
        self.assertIn("structurally valid", payload["valid_meaning"])

    def test_intake_accepts_complete_synthetic_artifact_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            baseline_dir = Path(tmpdir)
            for expected in EXPECTED:
                matches = None if expected.get("requires_timing_only") else True
                (baseline_dir / expected["path"].name).write_text(
                    json.dumps(_artifact(expected, matches_oracle=matches)),
                    encoding="utf-8",
                )

            payload = build_intake(baseline_dir)

        self.assertTrue(payload["valid"])
        self.assertTrue(payload["artifact_set_complete"])
        self.assertEqual(payload["overall_status"], "ready_for_2ai_baseline_review_not_public_claim")
        self.assertEqual(payload["summary"]["ok_count"], 4)
        self.assertEqual(payload["summary"]["blocked_count"], 0)

    def test_intake_blocks_bad_claim_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            baseline_dir = Path(tmpdir)
            expected = EXPECTED[0]
            artifact = _artifact(expected)
            artifact["public_speedup_claim_authorized"] = True
            (baseline_dir / expected["path"].name).write_text(json.dumps(artifact), encoding="utf-8")

            payload = build_intake(baseline_dir)
            row = next(row for row in payload["rows"] if row["name"] == expected["name"])

        self.assertEqual(row["status"], "blocked")
        self.assertIn("public_speedup_claim_authorized is not false", row["issues"])
        self.assertEqual(payload["overall_status"], "waiting_for_baseline_artifacts")

    def test_markdown_preserves_no_claim_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            markdown = to_markdown(build_intake(Path(tmpdir)))

        self.assertIn("Goal1102 Current-Contract Baseline Intake", markdown)
        self.assertIn("Artifact set complete: `false`", markdown)
        self.assertIn("Valid meaning:", markdown)
        self.assertIn("does not authorize public RTX speedup claims", markdown)
        self.assertIn("waiting_for_baseline_artifacts", markdown)


if __name__ == "__main__":
    unittest.main()
