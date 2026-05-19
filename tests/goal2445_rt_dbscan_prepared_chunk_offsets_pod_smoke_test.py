from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal2445_rt_dbscan_prepared_chunk_offsets_pod_smoke" / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal2445_rt_dbscan_prepared_chunk_offsets_pod_smoke_2026-05-19.md"


class Goal2445RtDbscanPreparedChunkOffsetsPodSmokeTest(unittest.TestCase):
    def test_pod_artifact_proves_prepared_offset_reuse(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        rows = payload["rows"]

        self.assertEqual(payload["commit"], "2d938df526ff4b68e6831a926fb2d8262e574ffb")
        self.assertEqual(payload["point_count"], 32768)
        self.assertTrue(payload["signatures_match"])
        self.assertEqual(len(rows), 2)
        self.assertFalse(rows[0]["prepared_chunk_edge_offsets_reused"])
        self.assertTrue(rows[1]["prepared_chunk_edge_offsets_reused"])
        self.assertEqual(rows[0]["prepared_chunk_edge_offset_count"], 18)
        self.assertEqual(rows[1]["prepared_chunk_edge_offset_count"], 18)
        self.assertEqual(rows[1]["prepared_chunk_edge_offsets_policy"], "degree_prefix_offsets_prepared_once_per_chunk")
        self.assertEqual(rows[1]["neighbor_index_workspace_policy"], "allocated_per_chunk_to_avoid_cross_stream_reuse_race")
        self.assertLessEqual(rows[1]["max_chunk_directed_edge_count"], rows[1]["max_directed_edges_per_chunk"])
        self.assertEqual(rows[1]["adjacency_write_pass_count"], 1)
        self.assertLess(rows[1]["elapsed_sec"], rows[0]["elapsed_sec"])

        self.assertFalse(payload["claim_boundary"]["release_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["paper_reproduction_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["broad_rt_core_speedup_claim_authorized"])

    def test_report_keeps_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("pod-smoked, with boundary", report)
        self.assertIn("prepared-handle evidence for offset reuse", report)
        self.assertIn("not a whole-app speedup claim", report)
        self.assertIn("cross-stream reuse race", report)
        self.assertIn("accept-with-boundary", report)


if __name__ == "__main__":
    unittest.main()
