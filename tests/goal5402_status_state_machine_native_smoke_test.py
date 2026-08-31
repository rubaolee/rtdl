from __future__ import annotations

from pathlib import Path
import ctypes
import inspect
import json
import sys
import unittest
from unittest import mock

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
POD_ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5402_status_state_machine_native_smoke_pod.json"
)


class _FakeStatusStateMachineSymbol:
    def __init__(self, *, overflow: bool = False) -> None:
        self.overflow = overflow
        self.argtypes = None
        self.restype = None

    def __call__(self, *args):
        if self.overflow:
            ctypes.cast(args[26], ctypes.POINTER(ctypes.c_uint64))[0] = 0
            ctypes.cast(args[27], ctypes.POINTER(ctypes.c_uint64))[0] = 3
            ctypes.cast(args[28], ctypes.POINTER(ctypes.c_uint64))[0] = 3
            ctypes.cast(args[29], ctypes.POINTER(ctypes.c_uint64))[0] = 1
            ctypes.cast(args[30], ctypes.POINTER(ctypes.c_uint32))[0] = 1
            return 0

        active_out = args[18]
        query_out = args[19]
        source_out = args[20]
        cell_out = args[21]
        status_out = args[22]
        phase_out = args[23]
        before_out = args[24]
        after_out = args[25]
        rows = [
            (10, 0, 100, 51, 2, 1, 5.0, 5.0),
            (12, 2, 102, 53, 2, 1, 7.0, 7.0),
        ]
        for i, row in enumerate(rows):
            active_out[i] = row[0]
            query_out[i] = row[1]
            source_out[i] = row[2]
            cell_out[i] = row[3]
            status_out[i] = row[4]
            phase_out[i] = row[5]
            before_out[i] = row[6]
            after_out[i] = row[7]
        ctypes.cast(args[26], ctypes.POINTER(ctypes.c_uint64))[0] = len(rows)
        ctypes.cast(args[27], ctypes.POINTER(ctypes.c_uint64))[0] = len(rows)
        ctypes.cast(args[28], ctypes.POINTER(ctypes.c_uint64))[0] = len(rows)
        ctypes.cast(args[29], ctypes.POINTER(ctypes.c_uint64))[0] = 1
        ctypes.cast(args[30], ctypes.POINTER(ctypes.c_uint32))[0] = 0
        return 0


class Goal5402StatusStateMachineNativeSmokeTest(unittest.TestCase):
    def test_native_symbol_is_declared_and_app_neutral(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8", errors="ignore")
        api = API.read_text(encoding="utf-8", errors="ignore")
        symbol = "rtdl_optix_active_query_status_state_machine_smoke_v1"

        self.assertIn(symbol, prelude)
        self.assertIn(f'extern "C" int {symbol}', api)
        self.assertIn("status_count_offloading_out", api)
        self.assertIn("feedback_update_count_out", api)
        self.assertIn("candidate_work_counts[i] <= heavy_threshold", api)
        self.assertIn("status_codes_out[out] = 2", api)
        self.assertIn("transition_phase_codes_out[out] = 1", api)

        window = api[api.index(symbol): api.index(symbol) + 7000].lower()
        for forbidden in ("xhd", "x-hd", "hausdorff", "paper", "hd_exec", "figure"):
            self.assertNotIn(forbidden, window)

    def test_python_frontdoor_exports_columns_and_feedback_telemetry(self) -> None:
        import rtdsl as rt
        from rtdsl import optix_runtime

        self.assertIn("active_query_status_state_machine_smoke_native", rt.__all__)
        self.assertIs(
            rt.active_query_status_state_machine_smoke_native,
            optix_runtime.active_query_status_state_machine_smoke_native,
        )

        fake = _FakeStatusStateMachineSymbol()
        with mock.patch.object(optix_runtime, "_load_optix_library", return_value=object()):
            with mock.patch.object(optix_runtime, "_find_optional_backend_symbol", return_value=fake):
                result = rt.active_query_status_state_machine_smoke_native(
                    query_row_ids=[0, 1, 2],
                    active_queue_indices=[10, 11, 12],
                    source_ids=[100, 101, 102],
                    current_best_sq=[5.0, 6.0, 7.0],
                    current_best_item_ids=[500, 501, 502],
                    candidate_query_row_ids=[0, 2],
                    candidate_cell_ids=[51, 53],
                    candidate_min_sq=[1.0, 2.0],
                    candidate_max_sq=[4.0, 5.0],
                    candidate_work_counts=[9, 10],
                    heavy_threshold=5,
                    feedback_active_queue_indices=[11],
                    feedback_best_sq=[3.0],
                    feedback_item_ids=[300],
                    row_capacity=8,
                )

        self.assertEqual(result["contract"], "generic_active_query_status_state_machine_native_spike_v1")
        self.assertEqual(result["native_generic_symbol"], "rtdl_optix_active_query_status_state_machine_smoke_v1")
        self.assertFalse(result["explicit_app_option_support_claimed"])
        self.assertFalse(result["rt_core_accelerated"])
        self.assertEqual(result["valid_count"], 2)
        self.assertEqual(result["attempted_count"], 2)
        self.assertEqual(result["columns"]["active_queue_indices"].tolist(), [10, 12])
        self.assertEqual(result["columns"]["cell_ids"].tolist(), [51, 53])
        self.assertEqual(result["columns"]["status_codes"].tolist(), [2, 2])
        self.assertEqual(result["columns"]["transition_phase_codes"].tolist(), [1, 1])
        self.assertEqual(result["columns"]["current_best_before_sq"].tolist(), [5.0, 7.0])
        self.assertEqual(result["columns"]["current_best_after_sq"].tolist(), [5.0, 7.0])
        self.assertEqual(result["telemetry"]["raw_offload_row_count"], 2)
        self.assertEqual(result["telemetry"]["status_count_offloading"], 2)
        self.assertEqual(result["telemetry"]["feedback_update_count"], 1)

    def test_python_frontdoor_fails_closed_on_overflow(self) -> None:
        import rtdsl as rt
        from rtdsl import optix_runtime

        fake = _FakeStatusStateMachineSymbol(overflow=True)
        with mock.patch.object(optix_runtime, "_load_optix_library", return_value=object()):
            with mock.patch.object(optix_runtime, "_find_optional_backend_symbol", return_value=fake):
                with self.assertRaisesRegex(RuntimeError, "fail_closed_overflow"):
                    rt.active_query_status_state_machine_smoke_native(
                        query_row_ids=[0],
                        active_queue_indices=[10],
                        source_ids=[100],
                        current_best_sq=[5.0],
                        current_best_item_ids=[500],
                        candidate_query_row_ids=[0, 0, 0],
                        candidate_cell_ids=[51, 52, 53],
                        candidate_min_sq=[1.0, 2.0, 3.0],
                        candidate_max_sq=[4.0, 5.0, 6.0],
                        candidate_work_counts=[9, 10, 11],
                        heavy_threshold=5,
                        row_capacity=2,
                    )

    def test_frontdoor_source_keeps_claim_boundary_narrow(self) -> None:
        from rtdsl import optix_runtime

        source = inspect.getsource(optix_runtime.active_query_status_state_machine_smoke_native)
        lowered = source.lower()
        self.assertIn("application option implementation", lowered)
        self.assertIn("not a row/hash parity claim", lowered)
        self.assertIn("not a paper performance claim", lowered)
        for forbidden in ("xhd", "x-hd", "hd_exec", "figure7", "figure11"):
            self.assertNotIn(forbidden, lowered)

    def test_pod_native_smoke_artifact_matches_expected_boundary(self) -> None:
        artifact = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        self.assertTrue(artifact["matched"])
        self.assertEqual(artifact["status"], "native_status_state_machine_smoke_passed")
        self.assertEqual(artifact["observed"]["valid_count"], 2)
        self.assertEqual(artifact["observed"]["attempted_count"], 2)
        self.assertEqual(artifact["observed"]["active_queue_indices"], [0, 2])
        self.assertEqual(artifact["observed"]["query_row_ids"], [10, 12])
        self.assertEqual(artifact["observed"]["status_codes"], [2, 2])
        self.assertEqual(artifact["observed"]["transition_phase_codes"], [1, 1])
        self.assertEqual(artifact["observed"]["telemetry"]["feedback_update_count"], 1)
        self.assertEqual(artifact["observed"]["telemetry"]["raw_offload_row_count"], 2)
        self.assertEqual(artifact["native_result_metadata"]["native_generic_symbol"], "rtdl_optix_active_query_status_state_machine_smoke_v1")
        self.assertEqual(artifact["native_result_metadata"]["contract"], "generic_active_query_status_state_machine_native_spike_v1")
        for key, value in artifact["claim_boundary"].items():
            if key.endswith("_claimed") and key not in {
                "generic_native_status_state_smoke_claimed",
                "synthetic_non_app_gate_claimed",
            }:
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
