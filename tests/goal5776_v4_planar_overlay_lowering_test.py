from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
LOWERING = ROOT / "src/rtdsl/v4_planar_overlay_lowering.py"
APP = ROOT / "Paper-reproduction-apps/rayjoin-paper/v4_whole_app.py"


class Goal5776PlanarOverlayLoweringTest(unittest.TestCase):
    def test_lowering_is_app_neutral_and_consumes_verified_callback(self):
        source = LOWERING.read_text(encoding="utf-8")
        lowered = source.lower()
        for forbidden in ("rayjoin", "county", "zipcode", "paper app"):
            self.assertNotIn(forbidden, lowered)
        self.assertIn("consume_verified_bounded_relation_executable", source)
        self.assertIn("DIRECTED_POINT_LOCATION_SOS_I46", source)
        self.assertIn("SEGMENT_PAIR_GROUPED_COUNT_SOS_I46", source)
        self.assertIn("OptixTraversalAuditSession", source)

    def test_app_runs_six_batches_without_python_event_rows(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn("def run_v4_real_scale_six_batch(", source)
        self.assertIn('"python_candidate_or_event_rows_materialized": False', source)
        self.assertIn('"default_selected_between_application_algorithms": False', source)


if __name__ == "__main__":
    unittest.main()
