from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4715_custom_predicate_early_exit_timing_result import (
    classify_v4_goal4715_custom_predicate_early_exit_timing,
    validate_v4_goal4715_custom_predicate_early_exit_timing_result_contract,
)


SCRIPT = ROOT / "scripts" / "v4_goal4715_custom_predicate_early_exit_timing_pod.py"


class V4Goal4715CustomPredicateEarlyExitTimingResultTest(unittest.TestCase):
    def _discovery(self) -> dict[str, object]:
        return {
            "completed_before_v4_timing": True,
            "v2_14": {"selected_baseline": "materialized_all_hit_ids_plus_device_predicate_reduce_fallback"},
            "v3_0_2": {"selected_baseline": "materialized_all_hit_ids_plus_device_predicate_reduce_fallback"},
        }

    def _rows(self, ratio: float = 1.7) -> list[dict[str, object]]:
        rows = []
        for regime, k in (("dense_early_accept_k8", 8), ("dense_early_accept_k32", 32), ("sparse_early_accept_k32", 32)):
            for scale in (65536, 131072):
                rows.append(
                    {
                        "row_role": "primary",
                        "regime": regime,
                        "scale": scale,
                        "v4_correctness_passed": True,
                        "materialized_fallback_correctness_passed": True,
                        "early_termination_observed": True,
                        "v4_anyhit_invocations": scale,
                        "fallback_all_hit_invocations": scale * k,
                        "v2_baseline_over_v4_ratio": ratio,
                        "v3_baseline_over_v4_ratio": ratio,
                    }
                )
        rows.append(
            {
                "row_role": "control",
                "regime": "dense_reject_all_k32",
                "scale": 65536,
                "v4_correctness_passed": True,
                "materialized_fallback_correctness_passed": True,
                "v2_baseline_over_v4_ratio": 1.0,
                "v3_baseline_over_v4_ratio": 1.0,
            }
        )
        return rows

    def test_contract_validation_passes(self) -> None:
        validation = validate_v4_goal4715_custom_predicate_early_exit_timing_result_contract()
        self.assertEqual("passed", validation["status"])
        self.assertEqual("pass_focused_timing_gate_not_release", validation["passing_example"]["classification"])
        self.assertFalse(validation["passing_example"]["release_authorized"])

    def test_classifier_fails_trivial_speedup(self) -> None:
        result = classify_v4_goal4715_custom_predicate_early_exit_timing(self._rows(ratio=1.05), self._discovery())
        self.assertEqual("fail_focused_timing_gate_not_high_performance", result["classification"])
        self.assertLess(result["primary_geomean_v3_speedup"], 1.50)

    def test_classifier_invalidates_missing_early_termination(self) -> None:
        rows = [
            {**row, "early_termination_observed": False, "v4_anyhit_invocations": row.get("fallback_all_hit_invocations", 0)}
            for row in self._rows()
        ]
        result = classify_v4_goal4715_custom_predicate_early_exit_timing(rows, self._discovery())
        self.assertEqual("invalid_or_fail_timing_gate_repair_required", result["classification"])

    def test_script_dry_run_emits_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "goal4715.json"
            md_out = tmp_path / "goal4715.md"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            )
            payload = json.loads(json_out.read_text(encoding="utf-8"))
            stdout_payload = json.loads(proc.stdout)
            markdown = md_out.read_text(encoding="utf-8")
        self.assertEqual("dry_run_contract_passed", payload["status"])
        self.assertEqual("dry_run_contract_passed", stdout_payload["status"])
        self.assertIn("Goal4715 Custom Predicate Early-Exit Timing", markdown)


if __name__ == "__main__":
    unittest.main()
