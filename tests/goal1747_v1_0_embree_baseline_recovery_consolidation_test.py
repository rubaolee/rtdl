import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1747_v1_0_embree_baseline_recovery_consolidation_2026-05-12.md"
RUN = ROOT / "docs" / "reports" / "goal1746_v1_0_embree_baseline_adapter_run_2026-05-12.json"


class Goal1747V10EmbreeBaselineRecoveryConsolidationTest(unittest.TestCase):
    def test_recovery_summary_counts(self) -> None:
        payload = json.loads(RUN.read_text(encoding="utf-8"))
        self.assertEqual(payload["attempted"], 14)
        self.assertEqual(payload["completed"], 14)
        skipped = [row for row in payload["results"] if row.get("skipped_by_request")]
        self.assertEqual(skipped, [])

    def test_recovered_artifacts_exist(self) -> None:
        payload = json.loads(RUN.read_text(encoding="utf-8"))
        for row in payload["results"]:
            if row.get("stdout_json"):
                artifact = ROOT / row["artifact"]
                self.assertTrue(artifact.exists(), row["artifact"])
                self.assertGreater(artifact.stat().st_size, 0, row["artifact"])

    def test_report_keeps_schema_and_speedup_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("embree_baseline_recovered_with_schema_boundary", text)
        self.assertIn("tester/profiler command-shape gap", text)
        self.assertIn("not a missing v1.0 Embree implementation gap", text)
        self.assertIn("ann_candidate_search", text)
        self.assertIn("rerank_summary", text)
        self.assertIn("7.2 billion", text)
        self.assertIn("37.262", text)
        self.assertIn("direct_speedup_claim_authorized` is false", text)
        self.assertIn("phase_mapping_required` is true", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("does not authorize v1.8 release/tag action", text)


if __name__ == "__main__":
    unittest.main()
