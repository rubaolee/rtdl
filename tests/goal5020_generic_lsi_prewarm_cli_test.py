import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"


class Goal5020GenericLsiPrewarmCliTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = APP.read_text(encoding="utf-8")

    def test_cli_exposes_generic_lsi_prewarm(self):
        self.assertIn('"--generic-lsi-prewarm"', self.source)
        self.assertIn("Run a tiny generic planar-map LSI prewarm", self.source)
        self.assertIn("_generic_lsi_tiny_prewarm", self.source)

    def test_prewarm_uses_public_generic_lsi_front_door(self):
        chunk = self.source[
            self.source.index("def _generic_lsi_tiny_prewarm") :
            self.source.index("def _trunc_div2_array")
        ]
        self.assertIn("base.prepare_planar_map_lsi_2d_optix", chunk)
        self.assertIn("query.run_bounded_pair_id_device_columns", chunk)
        self.assertNotIn("rayjoin_overlay", chunk)
        self.assertNotIn("output_chain", chunk)

    def test_summary_keeps_prewarm_out_of_route_window(self):
        self.assertIn('summary["generic_lsi_prewarm"]', self.source)
        self.assertIn('summary["generic_lsi_prewarm_time_excluded_from_writer_free_hot"] = True', self.source)
        self.assertIn('summary["cold_cli_one_shot_speedup_claim_authorized"] = False', self.source)
        self.assertIn('"prewarm_time_excluded_from_writer_free_hot": True', self.source)
        self.assertIn('"ten_x_claim_authorized": False', self.source)


if __name__ == "__main__":
    unittest.main()
