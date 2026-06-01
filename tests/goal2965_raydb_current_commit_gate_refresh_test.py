from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2965_raydb_current_commit_gate_refresh_2026-06-01.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2965_raydb_current_gate_pod"
RAW = ARTIFACT_DIR / "goal2965_raydb_same_contract_raw_current.json"
GATE = ARTIFACT_DIR / "goal2965_raydb_same_contract_gate_current.json"
EXPECTED_COMMIT = "28bcf380b078f6e3c0cbe55d9ed4ed78a9ac61e9"


class Goal2965RaydbCurrentCommitGateRefreshTest(unittest.TestCase):
    def test_current_commit_gate_passes_existing_acceptance_rows(self) -> None:
        gate = json.loads(GATE.read_text(encoding="utf-8"))

        self.assertEqual("pass", gate["status"])
        self.assertEqual(EXPECTED_COMMIT, gate["git_head"])
        self.assertEqual([], gate["errors"])
        self.assertTrue(gate["all_correct"])
        self.assertEqual(4, len(gate["comparisons"]))
        for row in gate["comparisons"]:
            with self.subTest(row_count=row["row_count"], mode=row["mode"]):
                self.assertIn(row["row_count"], (250000, 1000000))
                self.assertIn(row["mode"], ("count", "sum"))
                self.assertTrue(row["pass"])
                self.assertGreaterEqual(
                    float(row["prepared_hit_stream_triton_slowdown_vs_primitive_first"]),
                    float(row["required_min_slowdown"]),
                )

    def test_raw_artifact_contains_2m_stress_rows_with_correctness(self) -> None:
        raw = json.loads(RAW.read_text(encoding="utf-8"))
        cases = {
            (int(case["row_count"]), str(case["mode"]), str(case["backend"])): case
            for case in raw["cases"]
        }

        self.assertEqual(EXPECTED_COMMIT, raw["git_head"])
        self.assertTrue(raw["all_correct"])
        self.assertEqual(18, len(raw["cases"]))
        for mode in ("count", "sum"):
            primitive = cases[(2000000, mode, "paper_rt_optix_v2_5_primitive_first")]
            hit_stream = cases[(2000000, mode, "paper_rt_optix_device_hit_stream_triton_prepared")]
            old = cases[(2000000, mode, "paper_rt_optix")]
            slowdown = float(hit_stream["median_wall_sec"]) / float(primitive["median_wall_sec"])
            old_speedup = float(old["median_wall_sec"]) / float(primitive["median_wall_sec"])

            self.assertTrue(primitive["matches_cpu_reference"])
            self.assertTrue(hit_stream["matches_cpu_reference"])
            self.assertTrue(old["matches_cpu_reference"])
            self.assertEqual("prepared_fused_generic_grouped_reduction", primitive["v2_5_selected_path"])
            self.assertFalse(primitive["partner_continuation_required"])
            self.assertFalse(primitive["typed_hit_stream_forced"])
            self.assertGreater(slowdown, 30.0 if mode == "count" else 100.0)
            self.assertGreater(old_speedup, 1000.0)

    def test_report_and_readiness_keep_raydb_as_internal_gate(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)

        for phrase in (
            "Goal2965",
            "`30.138x`",
            "`142.648x`",
            "`108.213x`",
            "Do not promote Triton merely to say Triton was used.",
            "does not authorize",
        ):
            self.assertIn(phrase, text)
        self.assertIn(
            "docs/reports/goal2965_raydb_current_commit_gate_refresh_2026-06-01.md",
            packet["required_reports"],
        )
        self.assertFalse(packet["claim_authorization"]["v2_5_release_authorized"])


if __name__ == "__main__":
    unittest.main()
