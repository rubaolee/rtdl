import json
import unittest
from pathlib import Path

from scripts import goal2896_raydb_same_contract_performance_decision_gate as gate


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2896_raydb_same_contract_performance_decision_gate_2026-05-31.md"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2896_pod_artifacts"
    / "goal2896_raydb_same_contract_performance_decision_gate_pod_69_30_85_171_2026-05-31.json"
)


def _case(row_count: int, mode: str, backend: str, sec: float) -> dict[str, object]:
    return {
        "row_count": row_count,
        "mode": mode,
        "backend": backend,
        "median_wall_sec": sec,
        "matches_cpu_reference": True,
        "true_zero_copy_authorized": False,
        "v2_5_selected_path": "prepared_fused_generic_grouped_reduction"
        if backend == gate.PRIMITIVE_FIRST_BACKEND
        else None,
        "partner_continuation_required": False if backend == gate.PRIMITIVE_FIRST_BACKEND else None,
        "typed_hit_stream_forced": False if backend == gate.PRIMITIVE_FIRST_BACKEND else None,
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "release_authorized": False,
        },
    }


class Goal2896RaydbSameContractPerformanceDecisionGateTest(unittest.TestCase):
    def test_analyzer_accepts_primitive_first_win_with_claims_blocked(self) -> None:
        cases = []
        for row_count in gate.REQUIRED_ROW_COUNTS:
            for mode in gate.REQUIRED_MODES:
                primitive_sec = 0.001 if mode == "count" else 0.002
                hit_sec = primitive_sec * (gate.HIT_STREAM_MIN_SLOWDOWN_BY_MODE[mode] + 1.0)
                old_sec = primitive_sec * (gate.OLD_PAPER_MIN_SPEEDUP_BY_MODE[mode] + 1.0)
                cases.extend(
                    [
                        _case(row_count, mode, gate.PRIMITIVE_FIRST_BACKEND, primitive_sec),
                        _case(row_count, mode, gate.HIT_STREAM_TRITON_BACKEND, hit_sec),
                        _case(row_count, mode, gate.OLD_PAPER_BACKEND, old_sec),
                    ]
                )
        summary = gate.analyze_payload(
            {
                "git_head": "synthetic",
                "nvidia_smi": "NVIDIA RTX A5000, synthetic",
                "all_correct": True,
                "cases": cases,
            }
        )

        self.assertEqual(summary["status"], "pass")
        self.assertFalse(summary["decision"]["triton_front_door_promoted_for_scalar_grouped_reductions"])
        self.assertFalse(summary["decision"]["auto_triton_promotion_authorized"])
        self.assertFalse(summary["claim_boundary"]["release_authorized"])
        self.assertFalse(summary["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertEqual(len(summary["comparisons"]), 4)
        self.assertEqual(len(summary["diagnostics"]), 4)

    def test_analyzer_rejects_partner_first_regression(self) -> None:
        cases = []
        for row_count in gate.REQUIRED_ROW_COUNTS:
            for mode in gate.REQUIRED_MODES:
                cases.extend(
                    [
                        _case(row_count, mode, gate.PRIMITIVE_FIRST_BACKEND, 1.0),
                        _case(row_count, mode, gate.HIT_STREAM_TRITON_BACKEND, 1.1),
                        _case(row_count, mode, gate.OLD_PAPER_BACKEND, 100.0),
                    ]
                )
        summary = gate.analyze_payload({"all_correct": True, "cases": cases})

        self.assertEqual(summary["status"], "fail")
        self.assertTrue(
            any("hit-stream Triton slowdown" in error for error in summary["errors"]),
            summary["errors"],
        )

    def test_pod_gate_artifact_records_current_decision(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["all_correct"])
        self.assertIn("NVIDIA", payload["nvidia_smi"])
        self.assertEqual(payload["row_counts"], list(gate.REQUIRED_ROW_COUNTS))
        self.assertEqual(payload["modes"], list(gate.REQUIRED_MODES))
        self.assertEqual(
            payload["decision"]["raydb_scalar_grouped_fast_path"],
            gate.PRIMITIVE_FIRST_BACKEND,
        )
        self.assertEqual(
            payload["decision"]["selected_design_rule"],
            "primitive_first_for_exact_fused_generic_grouped_reductions",
        )
        self.assertFalse(payload["decision"]["triton_front_door_promoted_for_scalar_grouped_reductions"])
        self.assertFalse(payload["claim_boundary"]["release_authorized"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["true_zero_copy_authorized"])

        for comparison in payload["comparisons"]:
            with self.subTest(row_count=comparison["row_count"], mode=comparison["mode"]):
                self.assertTrue(comparison["pass"])
                self.assertGreaterEqual(
                    comparison["prepared_hit_stream_triton_slowdown_vs_primitive_first"],
                    comparison["required_min_slowdown"],
                )
        for diagnostic in payload["diagnostics"]:
            with self.subTest(row_count=diagnostic["row_count"], mode=diagnostic["mode"]):
                self.assertTrue(diagnostic["pass"])
                self.assertEqual(
                    diagnostic["comparison_scope"],
                    "diagnostic_full_call_baseline_not_prepared_same_contract",
                )

    def test_report_documents_decision_not_release_claim(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("RayDB Same-Contract Performance Decision Gate", text)
        self.assertIn("primitive-first", text)
        self.assertIn("prepared hit-stream plus Triton", text)
        self.assertIn("internal decision gate", text)
        self.assertIn("not a release claim", text)
        self.assertIn("not a true-zero-copy claim", text)


if __name__ == "__main__":
    unittest.main()
