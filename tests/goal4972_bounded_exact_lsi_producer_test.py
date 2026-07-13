from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
APP = ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"


class Goal4972BoundedExactLsiProducerTest(unittest.TestCase):
    def test_native_symbol_is_generic_and_bounded(self) -> None:
        symbol = (
            "rtdl_optix_run_prepared_segment_pair_bounded_exact_pair_id_device_columns_"
            "prepared_left_grouped_range_direct_intersection_with_predicate_mode"
        )
        self.assertIn(symbol, PRELUDE.read_text(encoding="utf-8"))
        self.assertIn(symbol, API.read_text(encoding="utf-8"))

        workloads = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn(
            "run_prepared_segment_pair_bounded_exact_pair_id_device_columns_prepared_left_grouped_range_direct_intersection_with_predicate_mode_optix",
            workloads,
        )
        self.assertIn("pair_output_capacity = static_cast<unsigned long long>(max_rows)", workloads)
        self.assertIn("if (emitted_count > static_cast<unsigned long long>(max_rows))", workloads)
        self.assertIn("columns_out->overflow = 1u", workloads)

        lowered = symbol.lower()
        for forbidden in ("rayjoin", "overlay", "output_chain", "authorofficial"):
            self.assertNotIn(forbidden, lowered)

    def test_python_front_door_and_app_route_are_bounded_measurement(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")

        self.assertIn("OPTIX_SEGMENT_PAIR_BOUNDED_EXACT_PAIR_ID_DEVICE_COLUMNS_PREPARED_LEFT_SYMBOL", runtime)
        self.assertIn("def bounded_exact_pair_id_device_columns_prepared_left", runtime)
        self.assertIn("def run_bounded_pair_id_device_columns", runtime)
        self.assertIn("predicate_mode=_PLANAR_MAP_LSI_PREDICATE_ID", runtime)

        self.assertIn("--bounded-exact-lsi-device-columns", app)
        self.assertIn("--bounded-exact-lsi-capacity", app)
        self.assertIn("lsi_bounded_exact_pair_id_device_columns_sec", app)
        self.assertIn("bounded_exact_lsi_downstream_numpy_copy_used", app)
        self.assertIn("device_columns.overflow", app)
        self.assertIn("not an ", app)
        self.assertIn("end-to-end zero-copy claim", app)


if __name__ == "__main__":
    unittest.main()
