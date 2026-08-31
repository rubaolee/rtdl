from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal4171_rtdbscan_road3d_2m_oneshot_probe_pod.json"
REPORT = ROOT / "docs" / "reports" / "goal4171_rtdbscan_road3d_2m_oneshot_probe_2026-06-09.md"


class Goal4171RtDbscanRoad3d2MOneShotProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.rows = {row["label"]: row for row in cls.payload["rows"]}

    def test_artifact_records_one_shot_pod_context(self) -> None:
        self.assertEqual(self.payload["schema"], "rtdl.goal4171.rtdbscan_2m_oneshot_probe.v1")
        self.assertEqual(self.payload["commit"], "72a4aedc6425646e00cf903c395c6b007cbd3dcc")
        self.assertIn("NVIDIA RTX 4000 Ada", self.payload["gpu"])
        self.assertEqual(self.payload["dataset"], "road3d")
        self.assertEqual(self.payload["point_count"], 2_097_152)
        self.assertEqual(self.payload["repeat"], 1)
        self.assertEqual(self.payload["warmup"], 0)
        for key, value in self.payload["claim_boundary"].items():
            self.assertFalse(value, key)

    def test_all_predicate_wrapper_is_one_shot_faster_and_signature_exact(self) -> None:
        current = self.rows["current_grouped_stream_numba"]
        candidate = self.rows["predicate_all_true_until_stable"]
        self.assertEqual(current["status"], "ok")
        self.assertEqual(candidate["status"], "ok")
        self.assertEqual(candidate["signature"], current["signature"])
        ratio = current["reported_elapsed_sec"] / candidate["reported_elapsed_sec"]
        self.assertGreater(ratio, 1.35)
        metadata = candidate["metadata"]
        self.assertTrue(metadata["all_predicate_fast_path"])
        self.assertEqual(metadata["border_candidate_updates"], 0)
        self.assertTrue(metadata["direct_status_convergence_proven"])

    def test_one_shot_overhead_is_visible_beyond_signature_phase(self) -> None:
        candidate = self.rows["predicate_all_true_until_stable"]
        metadata = candidate["metadata"]
        reported = float(candidate["reported_elapsed_sec"])
        signature = float(metadata["predicate_direct_status_signature_sec"])
        prepare = float(metadata["prepared_predicate_direct_status_sec"])
        self.assertGreater(reported, signature)
        self.assertGreater(reported - signature, 3.0)
        self.assertLess(prepare, 2.0)

    def test_plain_component_route_is_fast_but_not_app_signature_shape(self) -> None:
        current = self.rows["current_grouped_stream_numba"]
        generic = self.rows["prepared_direct_status_until_stable"]
        self.assertEqual(generic["status"], "ok")
        self.assertGreater(current["reported_elapsed_sec"] / generic["reported_elapsed_sec"], 1.7)
        self.assertNotEqual(generic["signature"], current["signature"])
        self.assertEqual(generic["signature"]["component_sizes"], [2_097_152])

    def test_report_keeps_next_target_and_boundary_precise(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "accepted bounded one-shot evidence; no route promotion",
            "repeat=1",
            "1.356x faster",
            "first-run/count-threshold/wrapper overhead",
            "does not solve mixed-predicate rows",
            "does not authorize automatic route selection",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
