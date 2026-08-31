from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
LOWERING = ROOT / "src/rtdsl/v4_aabb_relation_count_lowering.py"
APP = ROOT / "Paper-reproduction-apps/librts-paper/v4_whole_app.py"


class Goal5776AabbRelationCountLoweringTest(unittest.TestCase):
    def test_lowering_is_closed_app_neutral_and_true_optix(self):
        source = LOWERING.read_text(encoding="utf-8")
        lowered = source.lower()
        for forbidden in ("librts", "parks", "paper app"):
            self.assertNotIn(forbidden, lowered)
        self.assertIn("compile_callback()", source)
        self.assertIn("verify_typed_physical_schema", source)
        self.assertIn("AabbCountAlgebra", source)
        self.assertIn("prepare_aabb_index_2d_columns", source)
        self.assertIn("OptixTraversalAuditSession", source)
        self.assertIn("arbitrary_user_reducer_allowed\": False", source)

    def test_app_has_no_cartesian_capacity_for_real_scale_count(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn("prepare_v4_real_scale_count", source)
        body = source[source.index("def prepare_v4_real_scale_count"):]
        self.assertNotIn("len(indexed_columns) *", body)


if __name__ == "__main__":
    unittest.main()
