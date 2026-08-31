from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"


class Goal4981ReversedSideOrderBinaryRouteTest(unittest.TestCase):
    def test_side_order_remains_diagnostic_not_promoted_default(self) -> None:
        app = APP.read_text(encoding="utf-8")

        self.assertIn('side_order=(0, 1)', app)
        self.assertIn('default="0,1"', app)
        self.assertIn('"compiled_group_side_order"', app)
        self.assertIn('"compiled_group_side_order_scope"', app)
        self.assertIn("writer_free_binary_descriptor_route_only", app)

    def test_paper_text_order_claim_is_explicitly_not_authorized(self) -> None:
        app = APP.read_text(encoding="utf-8")

        self.assertIn('"paper_text_order_claim_authorized": False', app)
        self.assertIn("not a paper-text ordering policy", app)
        self.assertIn("side-order/locality diagnostic", app)
        self.assertNotIn("import rtdsl.rayjoin_overlay", app)
        self.assertNotIn("from rtdsl import rayjoin_overlay", app)


if __name__ == "__main__":
    unittest.main()
