from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
PRIMITIVE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
SCRIPT = ROOT / "scripts" / "goal4487_m91_rtdbscan_direct_status_prepare_breakdown.py"


class Goal4487M91DirectStatusPrepareBreakdownTest(unittest.TestCase):
    def test_direct_status_prepare_diagnostics_are_opt_in(self) -> None:
        source = PRIMITIVE.read_text(encoding="utf-8")
        start = source.index("def _prepare_direct_status_union_runtime_columns_cupy_3d")
        end = source.index("def _run_direct_status_union_signature_from_prepared_columns_cupy_3d")
        section = source[start:end]

        self.assertIn("RTDL_DIRECT_STATUS_PREPARE_DIAGNOSTICS", section)
        self.assertIn('"prepare_phase_timing_available": timing_enabled', section)
        self.assertIn('"prepare_phase_timing_diagnostic_syncs": timing_enabled', section)
        self.assertIn('if not timing_enabled:', section)
        self.assertIn("cupy.cuda.get_current_stream().synchronize()", section)

    def test_prepare_breakdown_runner_preserves_production_vs_diagnostic_split(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        for fragment in (
            "rtdl.v3_0.rtdbscan_direct_status_prepare_breakdown.goal4487.v1",
            "RTDL_DIRECT_STATUS_PREPARE_DIAGNOSTICS",
            '"diagnostics": False',
            '"diagnostics": True',
            "production_prepare_sec",
            "diagnostic_prepare_sec",
            "diagnostic_rows_are_for_phase_accounting_not_public_timing",
            "goal4487_v3_0_m91_rtdbscan_direct_status_prepare_breakdown_2026-06-17.json",
        ):
            self.assertIn(fragment, source)


if __name__ == "__main__":
    unittest.main()
