from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2502_raydb_style_benchmark_slice_closeout_2026-05-22.md"
CLAUDE_REVIEW = ROOT / "docs/reviews/goal2502_claude_review_raydb_style_closeout_2026-05-22.md"
CONSENSUS = ROOT / "docs/reviews/goal2502_codex_claude_consensus_raydb_style_closeout_2026-05-22.md"


class Goal2502RaydbStyleBenchmarkSliceCloseoutTest(unittest.TestCase):
    def test_closeout_states_local_completion_and_pod_gap(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("CPU + Embree local portion", text)
        self.assertIn("complete as\na reconstruction harness", text)
        self.assertIn("Post-pod update", text)
        self.assertIn("OptiX runtime parity evidence", text)
        self.assertIn("goal2501_raydb_style_optix_pod_validation_results_2026-05-22.md", text)
        self.assertIn("fresh OptiX runtime parity for count/sum", text)
        self.assertIn("now closed by Goal2501", text)
        self.assertIn('cases.optix.status == "ok"', text)

    def test_closeout_records_main_design_conclusion(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("direct_columnar_record_set_preparation_without_row_mapping", text)
        self.assertIn("more valuable than copying RayDB internals", text)
        self.assertIn("normalized column descriptors directly into backend preparation", text)

    def test_closeout_blocks_overclaims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "RayDB reproduction",
            "SQL engine or DBMS support",
            "authors-code performance comparison",
            "public speedup claim",
            "true zero-copy claim",
            "whole-app acceleration claim",
            "new app-specific native ABI",
        ):
            self.assertIn(phrase, text)

    def test_closeout_status_table_includes_key_capabilities(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "CPU oracle count/sum/min/max/avg_as_sum_count",
            "Embree count/sum parity",
            "OptiX count/sum app path",
            "Direct `ColumnarRecordSet` native preparation",
        ):
            self.assertIn(phrase, text)

    def test_external_review_and_consensus_exist(self) -> None:
        review = CLAUDE_REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")
        self.assertIn("APPROVE_WITH_NON_BLOCKING_NOTES", review)
        self.assertIn("Approve Goals2497-2502", consensus)
        self.assertIn("OptiX runtime parity remains pending", consensus)


if __name__ == "__main__":
    unittest.main()
