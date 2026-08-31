from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"


class Goal4988LsiDeviceColumnsDirectNumbaHandoffTest(unittest.TestCase):
    def test_app_has_direct_lsi_device_columns_to_numba_projection_route(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("device_column_row_buffer_from_native_pair_columns", source)
        self.assertIn("def numeric_xsect_columns_from_pair_device_columns_numba_device", source)
        self.assertIn('cuda.as_cuda_array(row_buffer.columns["left_id"])', source)
        self.assertIn('cuda.as_cuda_array(row_buffer.columns["right_id"])', source)
        self.assertIn('row_buffer_metadata = row_buffer.to_metadata()', source)
        self.assertIn('result["_pair_input_device_resident"] = bool(row_buffer.device_resident_candidate)', source)
        self.assertIn(
            'result["_pair_host_to_device_copy_used"] = bool(row_buffer.materializes_host_rows_for_bridge)',
            source,
        )

    def test_exact_lsi_device_route_keeps_old_numpy_fallback_but_uses_direct_handoff_when_device_columnar(self) -> None:
        source = APP.read_text(encoding="utf-8")
        route_block = source.split("if prepared_lsi_replay_enabled:", 1)[1].split("sorted0 = timed(", 1)[0]

        self.assertIn("produce_lsi_exact_device_columns", route_block)
        self.assertIn("produce_lsi_bounded_exact_device_columns", route_block)
        self.assertIn("if device_columnar_enabled:", route_block)
        self.assertIn("numeric_xsect_columns_from_pair_device_columns_numba_device", route_block)
        self.assertIn("lsi_device_columns.close()", route_block)
        self.assertIn("exact_lsi_pair_numpy_copy_used = True", route_block)
        self.assertIn("bounded_exact_lsi_pair_numpy_copy_used = True", route_block)

    def test_summary_distinguishes_direct_handoff_from_numpy_pair_copy(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn('"lsi_pair_input_device_resident"', source)
        self.assertIn('"lsi_pair_host_to_device_copy_used"', source)
        self.assertIn('"lsi_pair_row_buffer_contract"', source)
        self.assertIn('"exact_lsi_device_columns_numba_direct_handoff_used"', source)
        self.assertIn('"bounded_exact_lsi_numba_direct_handoff_used"', source)
        self.assertIn('"exact_lsi_device_columns_downstream_numpy_copy_used": exact_lsi_pair_numpy_copy_used', source)
        self.assertIn('"bounded_exact_lsi_downstream_numpy_copy_used": bounded_exact_lsi_pair_numpy_copy_used', source)

    def test_no_new_core_or_rayjoin_overlay_dependency_is_introduced(self) -> None:
        source = APP.read_text(encoding="utf-8")
        direct_route = source.split("def numeric_xsect_columns_from_pair_device_columns_numba_device", 1)[1].split(
            "def _next_power_of_two",
            1,
        )[0]

        self.assertNotIn("rtdsl.rayjoin_overlay", direct_route)
        self.assertNotIn("output_chain", direct_route.lower())
        self.assertNotIn("authorofficial", direct_route.lower())


if __name__ == "__main__":
    unittest.main()
