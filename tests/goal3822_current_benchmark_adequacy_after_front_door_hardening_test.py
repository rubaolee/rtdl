from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3822_current_benchmark_adequacy_after_front_door_hardening_2026-06-07.md"
MATRIX = ROOT / "docs" / "learn" / "benchmark_partner_reference_matrix.md"
PARTNER = ROOT / "docs" / "learn" / "partner_choice_for_custom_logic.md"


class Goal3822CurrentBenchmarkAdequacyAfterFrontDoorHardeningTest(unittest.TestCase):
    def test_current_version_and_summary_remain_fail_closed(self) -> None:
        self.assertEqual(
            rt.CURRENT_BENCHMARK_ADEQUACY_VERSION,
            "rtdl.v2_10.benchmark_adequacy_after_goal3842.v1",
        )
        validation = rt.validate_current_benchmark_adequacy()
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())
        summary = rt.summarize_current_benchmark_adequacy()
        self.assertEqual(summary["app_count"], 10)
        self.assertEqual(summary["row_count"], 10)
        self.assertEqual(summary["adequacy_counts"]["needs_major_followup"], 0)
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        self.assertFalse(summary["broad_rt_core_claim_authorized"])

    def test_rtnn_and_triangle_rows_carry_front_door_evidence(self) -> None:
        rows = {row["app"]: row for row in rt.current_benchmark_adequacy()}

        rtnn = rows["rtnn"]
        self.assertIn("prepared_optix_ranked_summary", rtnn["current_recommended_path"])
        self.assertIn("Goal3820", rtnn["evidence_refs"])
        self.assertIn("65536", rtnn["current_performance_reading"])
        self.assertIn("not an RTNN paper-reproduction claim", rtnn["current_performance_reading"])
        self.assertFalse(rtnn["paper_reproduction_claim_authorized"])
        self.assertFalse(rtnn["automatic_partner_selection_authorized"])

        triangle = rows["triangle_counting"]
        self.assertIn("--optix-graph-mode native", triangle["current_recommended_path"])
        self.assertIn("Goal3819", triangle["evidence_refs"])
        self.assertIn("0.9871935369446874", triangle["current_performance_reading"])
        self.assertIn("6.018893013708293", triangle["current_performance_reading"])
        self.assertIn("no RT-core triangle-count claim", triangle["current_performance_reading"])
        self.assertFalse(triangle["broad_rt_core_claim_authorized"])

    def test_docs_reference_current_front_doors_without_claim_authorization(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        matrix = MATRIX.read_text(encoding="utf-8")
        partner = PARTNER.read_text(encoding="utf-8")

        for text in (report, matrix, partner):
            self.assertIn("prepared_optix_ranked_summary", text)
            self.assertIn("--optix-graph-mode native", text)

        self.assertIn("does not authorize release action", report)
        self.assertIn("no RT-core triangle-count claim", matrix)
        self.assertIn("front-door evidence only", report)
        self.assertNotIn("RTNN paper reproduction", matrix)


if __name__ == "__main__":
    unittest.main()
