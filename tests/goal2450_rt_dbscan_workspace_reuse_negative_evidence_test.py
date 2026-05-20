from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2450_rt_dbscan_workspace_reuse_negative_evidence_2026-05-19.md"
SINGLE = ROOT / "docs" / "reports" / "goal2447_rt_dbscan_neighbor_workspace_reuse_pod_smoke" / "summary.json"
POOL = ROOT / "docs" / "reports" / "goal2449_rt_dbscan_neighbor_workspace_pool_pod_smoke" / "summary.json"


class Goal2450RtDbscanWorkspaceReuseNegativeEvidenceTest(unittest.TestCase):
    def test_report_records_negative_workspace_reuse_verdict(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("negative for performance", report)
        self.assertIn("Default per-chunk allocation", report)
        self.assertIn("Pool size 18", report)
        self.assertIn("lower-overhead generic grouped stream continuation", report)
        self.assertIn("accept-with-boundary", report)

    def test_artifacts_show_workspace_variants_do_not_beat_default(self) -> None:
        single = json.loads(SINGLE.read_text(encoding="utf-8"))
        pool = json.loads(POOL.read_text(encoding="utf-8"))

        self.assertGreater(single["reuse_over_default_time_ratio"], 1.0)
        for name in ("pool4", "pool8", "pool18"):
            self.assertGreaterEqual(pool["summary"][name]["time_ratio_vs_default"], 1.0)
        self.assertTrue(pool["summary"]["default_per_chunk_allocation"]["signatures_match"])
        self.assertTrue(single["default_per_chunk_allocation"]["signatures_match"])
        self.assertTrue(single["reused_neighbor_workspace"]["signatures_match"])


if __name__ == "__main__":
    unittest.main()
