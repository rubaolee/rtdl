import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLAIN = ROOT / "docs" / "reports" / "goal2284_segment_pair_phase_telemetry_pod_2026-05-17.json"
PACKED = ROOT / "docs" / "reports" / "goal2285_segment_pair_packed_left_probe_pod_2026-05-17.json"
REPORT = ROOT / "docs" / "reports" / "goal2284_segment_pair_phase_telemetry_pod_2026-05-17.md"


class Goal2284SegmentPairPhaseTelemetryPodTest(unittest.TestCase):
    def test_artifacts_record_same_stream_and_commit(self) -> None:
        plain = json.loads(PLAIN.read_text(encoding="utf-8"))
        packed = json.loads(PACKED.read_text(encoding="utf-8"))

        self.assertEqual(plain["commit"], "ae2f56680aa122940dc4fc234be74eed644af563")
        self.assertEqual(packed["commit"], plain["commit"])
        self.assertEqual(plain["query_stream"], packed["query_stream"])
        self.assertEqual(plain["query_stream_producer"], "rayjoin_query_exec_export_patch")
        self.assertEqual(packed["query_stream_producer"], "rayjoin_query_exec_export_patch")
        self.assertEqual(plain["query_count"], 100_000)
        self.assertEqual(packed["query_count"], 100_000)

    def test_packed_left_reuse_removes_python_packing_from_repeated_calls(self) -> None:
        plain = json.loads(PLAIN.read_text(encoding="utf-8"))
        packed = json.loads(PACKED.read_text(encoding="utf-8"))

        self.assertTrue(plain["parity"])
        self.assertTrue(packed["parity"])
        self.assertEqual(plain["raw_row_count"], 8_921)
        self.assertEqual(packed["raw_row_count"], 8_921)
        raw_speedup = plain["raw_median_sec"] / packed["raw_median_sec"]
        count_speedup = plain["count_median_sec"] / packed["count_median_sec"]
        self.assertGreater(raw_speedup, 15.0)
        self.assertGreater(count_speedup, 15.0)
        self.assertGreater(packed["one_time_left_pack_sec"], packed["raw_median_sec"])

    def test_phase_telemetry_identifies_native_phases(self) -> None:
        plain = json.loads(PLAIN.read_text(encoding="utf-8"))

        for phase_set in ("raw_phase_medians_sec", "count_phase_medians_sec"):
            phases = plain[phase_set]
            for key in (
                "left_upload",
                "candidate_count_pass",
                "candidate_write_pass",
                "candidate_download",
                "exact_refine",
            ):
                self.assertIn(key, phases)
                self.assertGreaterEqual(phases[key], 0.0)
            self.assertGreater(phases["exact_refine"], phases["candidate_download"])

    def test_report_preserves_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("strong v2 programming-model lesson", text)
        self.assertIn("prepack reusable left/query geometry", text)
        self.assertIn("about `20x`", text)
        self.assertIn("Not allowed", text)
        self.assertIn("claim that all workloads get a 20x gain", text)


if __name__ == "__main__":
    unittest.main()
