from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"


class Goal4978GroupedCarrierDecompositionTest(unittest.TestCase):
    def test_compiled_carrier_builder_reports_subphase_keys(self) -> None:
        app = APP.read_text(encoding="utf-8")

        for fragment in (
            "_prepare_inputs_sec",
            "_numba_builder_sec",
            "_slice_copy_sec",
            "_concatenate_sec",
            "_group_offset_cumsum_sec",
            "_stats_packaging_sec",
        ):
            self.assertIn(fragment, app)

    def test_compiled_carrier_builder_accepts_phase_seconds_without_core_changes(self) -> None:
        app = APP.read_text(encoding="utf-8")

        self.assertIn("phase_seconds=None", app)
        self.assertIn('phase_prefix="grouped_compiled_carrier"', app)
        self.assertIn("phase_seconds=phase_seconds", app)
        self.assertNotIn("import rtdsl.rayjoin_overlay", app)
        self.assertNotIn("from rtdsl import rayjoin_overlay", app)


if __name__ == "__main__":
    unittest.main()
