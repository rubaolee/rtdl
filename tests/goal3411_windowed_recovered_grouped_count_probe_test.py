from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3411_windowed_recovered_grouped_count_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3411_windowed_recovered_grouped_count_probe_2026-06-04.md"
SCRIPT = ROOT / "scripts" / "goal3411_windowed_recovered_grouped_count_probe.py"


class Goal3411WindowedRecoveredGroupedCountProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.script = SCRIPT.read_text(encoding="utf-8")

    def test_full_cdb_windowed_orchestration_shape(self):
        payload = self.payload

        self.assertEqual(payload["schema"], "rtdl.goal3411.windowed_recovered_grouped_count_probe.v1")
        self.assertEqual(payload["goal"], 3411)
        self.assertEqual(payload["rtdl_commit"][:8], "8b1fe308")
        self.assertEqual(payload["point_count"], 16545)
        self.assertEqual(payload["shape_count"], 15700)
        self.assertEqual(payload["window_size"], 2048)
        self.assertEqual(payload["window_count"], 9)
        self.assertEqual(payload["initial_max_rows"], 100)
        self.assertEqual(payload["overflow_window_count"], 9)
        self.assertEqual(payload["retry_window_count"], 9)

        boundary = payload["orchestration_boundary"]
        self.assertTrue(boundary["python_windowed_orchestration_bridge"])
        self.assertTrue(boundary["windows_are_caller_visible"])
        self.assertTrue(boundary["window_merge_uses_key_addition"])
        self.assertFalse(boundary["window_merge_requires_disjoint_left_ids"])
        self.assertFalse(boundary["native_paged_stream_implemented"])
        self.assertFalse(boundary["automatic_retry_authorized"])
        self.assertFalse(boundary["hidden_dispatch_authorized"])

    def test_windowed_recovered_grouped_counts_match_host(self):
        payload = self.payload

        self.assertEqual(payload["host_exact_row_count"], 47262)
        self.assertEqual(payload["device_grouped_source_row_count"], 47262)
        self.assertEqual(payload["host_group_count"], 16476)
        self.assertEqual(payload["device_group_count"], 16476)
        self.assertEqual(payload["device_grouped_row_count"], 16541)
        self.assertGreaterEqual(payload["device_grouped_row_count"], payload["device_group_count"])
        self.assertTrue(payload["group_counts_match_host"])
        self.assertEqual(payload["missing_group_key_count"], 0)
        self.assertEqual(payload["extra_group_key_count"], 0)
        self.assertEqual(payload["mismatched_group_value_count"], 0)

    def test_window_summaries_are_fail_closed_and_recovered(self):
        windows = self.payload["window_summaries"]
        self.assertEqual(len(windows), 9)
        self.assertEqual(windows[0]["first_capacity_status"]["required_capacity"], 5666)
        self.assertEqual(windows[7]["first_capacity_status"]["required_capacity"], 6016)
        self.assertEqual(windows[8]["first_capacity_status"]["required_capacity"], 352)

        for window in windows:
            first = window["first_capacity_status"]
            recovered = window["recovered_capacity_status"]
            self.assertEqual(first["capacity"], 100)
            self.assertEqual(first["row_count"], 0)
            self.assertTrue(first["overflowed"])
            self.assertEqual(first["retry_capacity_hint"], first["required_capacity"])
            self.assertFalse(first["partial_result_returned"])

            self.assertEqual(recovered["capacity"], first["required_capacity"])
            self.assertEqual(recovered["row_count"], first["required_capacity"])
            self.assertFalse(recovered["overflowed"])
            self.assertIsNone(recovered["retry_capacity_hint"])
            self.assertFalse(window["grouped_overflow"])
            self.assertEqual(window["grouped_source_row_count"], window["host_exact_rows"])

    def test_script_and_report_keep_native_paged_stream_boundary(self):
        self.assertIn("_windows(points, args.window_size)", self.script)
        self.assertIn("retry_hint = first_columns.retry_capacity_hint", self.script)
        self.assertIn("window_merge_uses_key_addition", self.script)
        self.assertIn("bounded Python orchestration bridge", self.report)
        self.assertIn("group keys are not assumed", self.report)
        self.assertIn("to be disjoint", self.report)
        self.assertIn("still not the native graduation target", self.report)
        self.assertIn("does not implement native paged streams", self.report)

        for key, value in self.payload["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
