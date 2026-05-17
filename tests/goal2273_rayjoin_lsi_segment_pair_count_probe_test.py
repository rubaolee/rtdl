import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal2273_rayjoin_lsi_segment_pair_count_probe_pod_2026-05-17.json"
REPORT = ROOT / "docs" / "reports" / "goal2273_rayjoin_lsi_segment_pair_count_probe_2026-05-17.md"


class Goal2273RayJoinLsiSegmentPairCountProbeTest(unittest.TestCase):
    def test_artifact_records_rayjoin_exported_stream(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["goal"], 2273)
        self.assertEqual(payload["commit"], "dffabc1317f382dcb19cd3ea30087692a0b69e48")
        self.assertEqual(payload["query_stream_schema"], "rtdl.rayjoin.same_query_stream.v1")
        self.assertEqual(payload["query_stream_producer"], "rayjoin_query_exec_export_patch")
        self.assertEqual(payload["workload"], "lsi")
        self.assertEqual(payload["query_count"], 100_000)

    def test_count_preserves_parity_but_not_speedup(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertTrue(payload["parity"])
        self.assertEqual(payload["raw_row_count"], 8_921)
        self.assertEqual(payload["scalar_count"], 8_921)
        self.assertGreater(payload["count_to_row_ratio"], 1.0)
        self.assertLess(payload["row_to_count_speedup"], 1.0)

    def test_claim_boundary_is_closed(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        boundary = payload["claim_boundary"]

        self.assertFalse(boundary["whole_app_speedup_claim_authorized"])
        self.assertFalse(boundary["rayjoin_paper_dataset_claim_authorized"])
        self.assertFalse(boundary["rtdl_beats_rayjoin_claim_authorized"])

    def test_report_states_diagnostic_lesson(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("not the bottleneck fix", text)
        self.assertIn("row output is already small", text)
        self.assertIn("candidate copyback and exact-refinement overhead", text)
        self.assertIn("not materially improve runtime", text)


if __name__ == "__main__":
    unittest.main()
