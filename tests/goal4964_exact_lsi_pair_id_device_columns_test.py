from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
APP = ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"


class Goal4964ExactLsiPairIdDeviceColumnsTest(unittest.TestCase):
    def test_runtime_exposes_exact_pair_id_device_column_front_door(self) -> None:
        source = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("OPTIX_SEGMENT_PAIR_EXACT_PAIR_ID_DEVICE_COLUMNS_PREPARED_LEFT_SYMBOL", source)
        self.assertIn("exact_pair_id_device_columns_prepared_left", source)
        self.assertIn("def run_pair_id_device_columns(self) -> OptixNativeDevicePairColumnOutput", source)
        self.assertIn("predicate_mode=_PLANAR_MAP_LSI_PREDICATE_ID", source)

    def test_native_symbol_is_generic_not_rayjoin_overlay_named(self) -> None:
        symbol = (
            "rtdl_optix_run_prepared_segment_pair_exact_pair_id_device_columns_"
            "prepared_left_grouped_range_direct_intersection_with_predicate_mode"
        )
        self.assertIn(symbol, PRELUDE.read_text(encoding="utf-8"))
        self.assertIn(symbol, API.read_text(encoding="utf-8"))
        workloads = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn(
            "run_prepared_segment_pair_exact_pair_id_device_columns_prepared_left_grouped_range_direct_intersection_with_predicate_mode_optix",
            workloads,
        )

        lowered = symbol.lower()
        for forbidden in ("rayjoin", "overlay", "output_chain", "authorofficial"):
            self.assertNotIn(forbidden, lowered)

    def test_exact_device_route_reuses_device_pair_column_shape_but_not_candidate_route(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        function_block = workloads.split(
            "run_prepared_segment_pair_exact_pair_id_device_columns_prepared_left_grouped_range_direct_intersection_with_predicate_mode_optix",
            1,
        )[1].split("static void run_prepared_segment_pair_candidate_device_columns_optix", 1)[0]

        self.assertIn("pair_output", function_block)
        self.assertIn("segment_pair_split_packed_pair_ids_kernel", workloads)
        self.assertIn("columns_out->candidate_event_count = static_cast<uint64_t>(exact_count);", function_block)
        self.assertNotIn("RtdlSegmentPairIdRow", function_block)
        self.assertNotIn("std::malloc", function_block)

    def test_public_app_route_is_explicit_measurement_and_not_zero_copy_claim(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("--exact-lsi-device-columns", source)
        self.assertIn("lsi_exact_pair_id_device_columns_sec", source)
        self.assertIn("lsi_exact_pair_id_device_columns_to_numpy_sec", source)
        self.assertIn("exact_lsi_device_columns_downstream_numpy_copy_used", source)
        self.assertIn("--prepared-lsi-replay, --exact-lsi-device-columns, and ", source)
        self.assertIn("--bounded-exact-lsi-device-columns are mutually exclusive", source)

    def test_public_app_file_has_no_internal_goal_or_history_dependency(self) -> None:
        source = APP.read_text(encoding="utf-8").lower()

        self.assertNotIn("history/internal_docs", source)
        self.assertNotIn("goal4964", source)
        self.assertNotIn("goal4963", source)


if __name__ == "__main__":
    unittest.main()
