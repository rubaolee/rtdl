from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"


class Goal4979GroupedCarrierSideWorkMetricsTest(unittest.TestCase):
    def test_side_builder_work_metric_keys_are_reported(self) -> None:
        app = APP.read_text(encoding="utf-8")

        self.assertIn("GROUPED_CARRIER_SIDE_WORK_METRIC_KEYS", app)
        for key in (
            "chain_points_scanned",
            "edge_slots_scanned",
            "intersection_run_count",
            "intersection_row_count",
            "intersection_display_point_appends",
            "dedupe_append_calls",
            "split_flush_count",
            "chain_final_flush_count",
            "kept_group_count",
            "skipped_group_count",
            "emitted_point_row_count",
        ):
            self.assertIn(key, app)

    def test_metrics_remain_app_owned_and_do_not_promote_carrier_core(self) -> None:
        app = APP.read_text(encoding="utf-8")

        self.assertIn('"side_work_metrics": side_work_metrics', app)
        self.assertIn('"side_work_metrics_total": _sum_grouped_carrier_side_work_metrics', app)
        self.assertIn("out_metrics = np.zeros(len(GROUPED_CARRIER_SIDE_WORK_METRIC_KEYS)", app)
        self.assertIn("parse_compiled_group_side_order", app)
        self.assertIn("--compiled-group-side-order", app)
        self.assertIn('"compiled_group_side_order"', app)
        self.assertNotIn("import rtdsl.rayjoin_overlay", app)
        self.assertNotIn("from rtdsl import rayjoin_overlay", app)


if __name__ == "__main__":
    unittest.main()
