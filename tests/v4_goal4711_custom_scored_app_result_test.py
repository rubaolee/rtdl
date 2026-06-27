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

import rtdsl.v4 as v4


SCRIPT = ROOT / "scripts" / "v4_goal4711_custom_scored_app_pod.py"


class V4Goal4711CustomScoredAppResultTest(unittest.TestCase):
    def _discovery(self) -> dict[str, object]:
        return {
            "completed_before_v4_timing": True,
            "quality": "strong_materialized_device_fallback_after_no_custom_repo_route_found",
            "v2_14": {"selected_baseline": "materialized_hit_id_plus_device_callback_reduce_fallback"},
            "v3_0_2": {"selected_baseline": "materialized_hit_id_plus_device_callback_reduce_fallback"},
        }

    def _rows(self, ratio: float = 1.35) -> list[dict[str, object]]:
        rows = []
        for callback in ("affine_score", "threshold_score", "minmax_score"):
            for regime in ("dense_hits", "sparse_hits"):
                for scale in (262144, 524288):
                    rows.append(
                        {
                            "protocol_callback": callback,
                            "callback_role": "primary",
                            "regime": regime,
                            "scale": scale,
                            "v4_fused_median_s": 1.0,
                            "v2_baseline_median_s": 1.6,
                            "v3_baseline_median_s": ratio,
                            "v2_baseline_over_v4_ratio": 1.6,
                            "v3_baseline_over_v4_ratio": ratio,
                            "v4_fused_correctness_passed": True,
                            "materialized_fallback_correctness_passed": True,
                            "counts_toward_primary_claim": True,
                        }
                    )
        return rows

    def test_contract_validation_passes_and_exports(self) -> None:
        validation = v4.validate_v4_goal4711_custom_scored_app_result_contract()
        self.assertEqual("passed", validation["status"])
        self.assertIn("pending_external_denominator_review", validation["passing_example"]["classification"])
        self.assertFalse(validation["passing_example"]["release_authorized"])

    def test_classifier_rejects_weighted_sum_as_primary_claim(self) -> None:
        rows = self._rows()
        rows.append(
            {
                "protocol_callback": "weighted_sum",
                "callback_role": "control",
                "regime": "dense_hits",
                "scale": 262144,
                "v4_fused_median_s": 1.0,
                "v2_baseline_median_s": 3.0,
                "v3_baseline_median_s": 3.0,
                "v2_baseline_over_v4_ratio": 3.0,
                "v3_baseline_over_v4_ratio": 3.0,
                "v4_fused_correctness_passed": True,
                "materialized_fallback_correctness_passed": True,
                "counts_toward_primary_claim": True,
            }
        )
        result = v4.classify_v4_goal4711_custom_scored_app_result(rows, self._discovery())
        self.assertEqual("fail_focused_app_gate_not_high_performance", result["classification"])
        self.assertTrue(result["weighted_sum_used_as_claim_evidence"])

    def test_classifier_fails_low_v3_gain(self) -> None:
        result = v4.classify_v4_goal4711_custom_scored_app_result(self._rows(ratio=1.02), self._discovery())
        self.assertEqual("fail_focused_app_gate_not_high_performance", result["classification"])
        self.assertLess(result["primary_geomean_v3_speedup"], 1.20)

    def test_script_dry_run_emits_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "goal4711.json"
            md_out = tmp_path / "goal4711.md"
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
        self.assertIn("Goal4711 Custom Scored App", markdown)


if __name__ == "__main__":
    unittest.main()
