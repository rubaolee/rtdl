from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2403_rt_dbscan_repeat_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3758_rt_dbscan_numba_repeat_probe_support_2026-06-07.md"
SUMMARY = ROOT / "docs" / "reports" / "goal3758_rt_dbscan_numba_repeat_probe_a5000" / "summary.json"


class Goal3758RtDbscanNumbaRepeatProbeSupportTest(unittest.TestCase):
    def test_repeat_probe_declares_numba_prepared_modes(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('PREPARED_NUMBA_GRID_MODE = "partner_numba_prepared_grid_components_3d"', text)
        self.assertIn(
            'PREPARED_OPTIX_NUMBA_GRID_MODE = "optix_rt_core_flags_numba_prepared_grid_components_3d"',
            text,
        )
        self.assertIn("PREPARED_NUMBA_GRID_MODE", text)
        self.assertIn("PREPARED_OPTIX_NUMBA_GRID_MODE", text)

    def test_numba_repeat_rows_are_rawkernel_free_and_claim_bounded(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"raw_cuda_kernel_required": False', text)
        self.assertIn('"numba_component_continuation_sec": outer_elapsed', text)
        self.assertIn('"numba_component_continuation_sec": continuation_elapsed', text)
        self.assertIn('"rt_core_accelerated": True', text)
        self.assertIn('"rt_core_accelerated": False', text)
        self.assertIn('"steady_state_probe_only": True', text)

    def test_report_documents_purpose_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("RT-DBSCAN Numba Repeat Probe Support", text)
        self.assertIn("no RawKernel", text)
        self.assertIn("same reuse contract", text)
        self.assertIn("A5000 Evidence", text)
        self.assertIn("1.748x", text)
        self.assertIn("does not authorize", text)

    def test_a5000_summary_records_scale_dependent_numba_result(self) -> None:
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(summary["goal"], "Goal3758")
        self.assertEqual(summary["hardware"], "A5000 pod")
        self.assertEqual(summary["dataset"], "clustered3d")
        for value in summary["claim_boundary"].values():
            self.assertFalse(value)

        rows = {row["point_count"]: row for row in summary["rows"]}
        self.assertEqual(set(rows), {4096, 65536, 131072})
        for row in rows.values():
            self.assertTrue(row["signatures_match"])
            numba_modes = [mode for mode in row["mode_results"] if "numba" in mode["mode"]]
            self.assertTrue(numba_modes)
            for mode in numba_modes:
                self.assertFalse(mode["raw_cuda_kernel_required"])

        self.assertGreater(rows[65536]["speedups"]["optix_numba_vs_cupy_prepared_grid"], 1.3)
        self.assertGreater(rows[131072]["speedups"]["optix_numba_vs_cupy_prepared_grid"], 1.7)
        self.assertGreater(rows[131072]["speedups"]["optix_numba_vs_numba_prepared_grid"], 1.5)
        self.assertLess(rows[4096]["speedups"]["optix_numba_vs_cupy_prepared_grid"], 1.0)


if __name__ == "__main__":
    unittest.main()
