import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3989_rt_dbscan_grouped_union_telemetry_2026-06-08.md"
TELEMETRY = ROOT / "docs" / "reports" / "goal3989_rt_dbscan_grouped_union_atomic_telemetry_2026-06-08.json"
TELEMETRY_STDERR = ROOT / "docs" / "reports" / "goal3989_rt_dbscan_grouped_union_atomic_telemetry_2026-06-08.stderr.log"
SAME_ROOT = ROOT / "docs" / "reports" / "goal3989_rt_dbscan_same_root_ab_2026-06-08"


class Goal3989RtDbscanGroupedUnionTelemetryTest(unittest.TestCase):
    def test_atomic_telemetry_is_positive_but_not_huge(self) -> None:
        payload = json.loads(TELEMETRY.read_text(encoding="utf-8"))
        self.assertEqual(TELEMETRY_STDERR.read_text(encoding="utf-8"), "")
        row = payload["summaries"][0]
        self.assertEqual(row["point_count"], 65536)
        self.assertGreater(row["tail_median_parent_atomic_attempts"], 0)
        self.assertGreater(row["tail_median_parent_atomic_successes"], 0)
        self.assertLess(row["tail_median_parent_attempts_per_point"], 2.0)
        self.assertGreater(row["tail_median_parent_success_rate"], 0.5)
        self.assertFalse(payload["claim_boundary"]["performance_claim_authorized"])

    def test_same_root_culling_is_still_the_faster_default(self) -> None:
        enabled = json.loads((SAME_ROOT / "same_root_on.stdout.json").read_text(encoding="utf-8"))
        disabled = json.loads((SAME_ROOT / "same_root_off.stdout.json").read_text(encoding="utf-8"))
        self.assertEqual(enabled["signature"], disabled["signature"])
        enabled_median = enabled["metadata"]["prepared_query_repeat_protocol"]["elapsed_sec_median"]
        disabled_median = disabled["metadata"]["prepared_query_repeat_protocol"]["elapsed_sec_median"]
        self.assertLess(enabled_median, disabled_median)
        self.assertTrue(
            enabled["metadata"]["native_grouped_stream_metadata"][
                "grouped_union_same_root_culling_enabled"
            ]
        )
        self.assertFalse(
            disabled["metadata"]["native_grouped_stream_metadata"][
                "grouped_union_same_root_culling_enabled"
            ]
        )

    def test_report_names_next_generic_design_target_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "atomics are not the sole bottleneck",
            "RT candidate traversal plus same-root root-read culling",
            "dense fixed-radius grouped-union continuation",
            "does not authorize release",
        ]:
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
