import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal2276_cached_lookup_rayjoin_lsi_probe_pod_2026-05-17.json"
REPORT = ROOT / "docs" / "reports" / "goal2276_cached_lookup_rayjoin_lsi_probe_2026-05-17.md"


class Goal2276CachedLookupRayJoinLsiProbeTest(unittest.TestCase):
    def test_artifact_records_pushed_commit_and_stream(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["goal"], 2276)
        self.assertEqual(payload["commit"], "5c41ade112fb7ebbcdd6ed593eea96eb806db75f")
        self.assertEqual(payload["compared_baseline_goal2273_commit"], "dffabc1317f382dcb19cd3ea30087692a0b69e48")
        self.assertEqual(payload["query_stream_producer"], "rayjoin_query_exec_export_patch")
        self.assertEqual(payload["query_count"], 100_000)

    def test_cached_lookup_preserves_parity_and_improves_baseline(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertTrue(payload["parity"])
        self.assertEqual(payload["raw_row_count"], 8_921)
        self.assertEqual(payload["scalar_count"], 8_921)
        self.assertGreater(payload["improvement_vs_goal2273"]["row_raw_speedup"], 1.05)
        self.assertGreater(payload["improvement_vs_goal2273"]["count_speedup"], 1.10)

    def test_count_is_slightly_faster_after_cache(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertLess(payload["count_to_row_ratio"], 1.0)
        self.assertGreater(payload["row_to_count_speedup"], 1.0)

    def test_report_keeps_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("modest but real improvement", text)
        self.assertIn("does not fully solve the LSI performance gap", text)
        self.assertIn("not an app-specific RayJoin engine path", text)
        self.assertIn("Not allowed", text)


if __name__ == "__main__":
    unittest.main()
