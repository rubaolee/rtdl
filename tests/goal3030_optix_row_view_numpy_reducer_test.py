from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
HAUSDORFF_APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "hausdorff_xhd" / "rtdl_hausdorff_v2_function.py"
PROBE_SCRIPT = ROOT / "scripts" / "goal3026_hausdorff_raw_row_view_probe.py"


class Goal3030OptixRowViewNumpyReducerTest(unittest.TestCase):
    def test_optix_row_view_exposes_borrowed_numpy_structured_view(self) -> None:
        from rtdsl.optix_runtime import _RtdlFixedRadiusNeighborRow
        from rtdsl.optix_runtime import _make_owned_row_view

        view = _make_owned_row_view(
            _RtdlFixedRadiusNeighborRow,
            (
                _RtdlFixedRadiusNeighborRow(0, 10, 1.25),
                _RtdlFixedRadiusNeighborRow(1, 11, 2.5),
            ),
            ("query_id", "neighbor_id", "distance"),
        )
        rows = view.to_numpy(copy=False)

        self.assertEqual(rows.dtype.names, ("query_id", "neighbor_id", "distance"))
        np.testing.assert_array_equal(rows["query_id"], np.asarray([0, 1], dtype=np.uint32))
        np.testing.assert_array_equal(rows["neighbor_id"], np.asarray([10, 11], dtype=np.uint32))
        np.testing.assert_allclose(rows["distance"], np.asarray([1.25, 2.5], dtype=np.float64))

    def test_optix_row_view_numpy_copy_survives_close(self) -> None:
        from rtdsl.optix_runtime import _RtdlFixedRadiusNeighborRow
        from rtdsl.optix_runtime import _make_owned_row_view

        view = _make_owned_row_view(
            _RtdlFixedRadiusNeighborRow,
            (_RtdlFixedRadiusNeighborRow(2, 20, 3.75),),
            ("query_id", "neighbor_id", "distance"),
        )
        rows = view.to_numpy(copy=True)
        view.close()

        self.assertEqual(float(rows["distance"][0]), 3.75)
        with self.assertRaisesRegex(RuntimeError, "after OptixRowView is closed"):
            view.to_numpy(copy=False)

    def test_row_view_contract_marks_host_buffer_not_device_zero_copy(self) -> None:
        source = OPTIX_RUNTIME.read_text(encoding="utf-8")
        block = source[source.index("def to_numpy("):source.index("def to_numpy_columns(")]

        self.assertIn("borrowed host-memory view", block)
        self.assertIn("not a", block)
        self.assertIn("zero-copy partner handoff claim", block)

    def test_hausdorff_raw_path_uses_vectorized_row_view_reduction(self) -> None:
        source = HAUSDORFF_APP.read_text(encoding="utf-8")
        block = source[
            source.index("def _directed_rt_grouped_adaptive_raw_nearest_witness"):
            source.index("def _directed_rt_grouped_adaptive_reduced_nearest_witness")
        ]

        self.assertIn("rows = raw_rows.to_numpy(copy=False)", block)
        self.assertIn('rows["neighbor_id"]', block)
        self.assertIn("np.hypot", block)
        self.assertIn("np.argmax", block)
        self.assertNotIn("for local_index in range(raw_rows.row_count)", block)
        self.assertNotIn("to_dict_rows", block)

    def test_probe_script_supports_even_repeat_exploratory_runs(self) -> None:
        source = PROBE_SCRIPT.read_text(encoding="utf-8")

        self.assertIn("median_sample = statistics.median(samples)", source)
        self.assertIn("selected_index = min(range(len(samples))", source)
        self.assertNotIn("samples.index(statistics.median(samples))", source)


if __name__ == "__main__":
    unittest.main()
