from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2948_payload_grouped_sum_scale_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal2948_payload_grouped_sum_scale_probe_2026-06-01.md"
POD_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2948_payload_grouped_sum_scale_probe_pod"
    / "goal2948_payload_grouped_sum_scale_probe.json"
)


class Goal2948PayloadGroupedSumScaleProbeTest(unittest.TestCase):
    def test_runner_uses_goal2947_front_door_and_claim_boundaries(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("prepare_generic_ray_triangle_event_ordered_payload_grouped_sum_3d", source)
        self.assertIn("partner=\"cupy\"", source)
        self.assertIn("event_ordered_partner_payload_grouped_sum_consumer_and_materialization", source)
        self.assertIn('"public_speedup_claim_authorized": False', source)
        self.assertIn('"rayjoin_paper_claim_authorized": False', source)

    def test_report_explains_scale_probe_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2948", text)
        self.assertIn("multi-block/partial-reduction", text)
        self.assertIn("262144", text)
        self.assertIn("not a v2.5 release authorization", text)
        self.assertIn("not encode RayJoin", text)

    def test_pod_artifact_when_available(self) -> None:
        if not POD_ARTIFACT.exists():
            self.skipTest("Goal2948 pod artifact has not been imported yet")
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual("pass", payload["status"])
        self.assertRegex(payload["source_commit"], r"^[0-9a-f]{40}$")
        self.assertEqual([], payload["source_dirty"])
        self.assertEqual(262144, payload["expected_row_count"])
        self.assertEqual(4096, payload["ray_count"])
        self.assertEqual(64, payload["triangle_count"])
        self.assertGreater(payload["rows_per_second_median"], 0.0)
        self.assertGreater(payload["consumer_rows_per_second_median"], 0.0)
        for result in payload["timed_results"]:
            self.assertEqual(262144, result["summary"]["row_count"])
            self.assertEqual(payload["expected_group_hit_counts"], result["group_hit_counts"])
            self.assertEqual(payload["expected_group_payload_sums"], result["group_payload_sums"])
            metadata = result["metadata"]
            self.assertEqual("hit_stream_primitive_payload_grouped_sum_f64", metadata["operation"])
            self.assertEqual("cupy_conformance", metadata["selected_partner"])
            self.assertEqual("cuda_event_cross_stream", metadata["producer_consumer_stream_ordering"])
            self.assertFalse(metadata["public_speedup_claim_authorized"])
            self.assertFalse(metadata["true_zero_copy_authorized"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["true_zero_copy_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
