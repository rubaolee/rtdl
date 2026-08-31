from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path
from unittest import mock

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
SMOKE_SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_goal5397_native_status_stream_smoke.py"
)
POD_ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5397_native_status_stream_smoke_pod.json"
)


class Goal5397NativeStatusStreamFrontdoorTest(unittest.TestCase):
    def test_native_v7_symbol_and_status_row_schema_are_declared(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8", errors="ignore")
        api = API.read_text(encoding="utf-8", errors="ignore")
        workloads = WORKLOADS.read_text(encoding="utf-8", errors="ignore")

        self.assertIn("struct RtdlActiveQueryStatusStreamRow", prelude)
        for field in (
            "active_queue_index",
            "query_row_id",
            "source_id",
            "cell_id",
            "status_code",
            "transition_phase_code",
            "current_best_before_sq",
            "current_best_after_sq",
        ):
            self.assertIn(field, prelude)
            self.assertIn(field, workloads)

        symbol = "rtdl_optix_collect_active_query_status_stream_3d_v1"
        self.assertIn(symbol, prelude)
        self.assertIn(f'extern "C" int {symbol}', api)
        self.assertIn("status_rows_out", workloads)
        self.assertIn("params.status_rows_out[row_index]", workloads)

    def test_python_frontdoor_is_exported_and_app_neutral(self) -> None:
        import rtdsl as rt
        from rtdsl import optix_runtime

        self.assertIn("collect_active_query_status_stream_3d_optix", rt.__all__)
        self.assertIs(
            rt.collect_active_query_status_stream_3d_optix,
            optix_runtime.collect_active_query_status_stream_3d_optix,
        )

        source = inspect.getsource(optix_runtime.collect_active_query_status_stream_3d_optix)
        lowered = source.lower()
        for forbidden in ("xhd", "x-hd", "hd_exec", "figure7", "figure11"):
            self.assertNotIn(forbidden, lowered)
        self.assertIn('"contract": "generic_active_query_status_stream_native_abi_v1"', source)
        self.assertIn('"explicit_app_option_support_claimed": False', source)
        self.assertIn('"native_backend_complete": False', source)

    def test_frontdoor_fails_closed_when_native_symbol_is_missing(self) -> None:
        from rtdsl import optix_runtime

        query_coords = np.asarray([[0.0, 0.0, 0.0]], dtype=np.float64)
        query_ids = np.asarray([100], dtype=np.int64)
        cell_ids = np.asarray([10], dtype=np.int64)
        begins = np.asarray([0], dtype=np.uint64)
        counts = np.asarray([1], dtype=np.uint64)
        mins = np.asarray([[-1.0, -1.0, -1.0]], dtype=np.float64)
        maxs = np.asarray([[1.0, 1.0, 1.0]], dtype=np.float64)
        best = np.asarray([np.inf], dtype=np.float64)
        best_ids = np.asarray([-1], dtype=np.int64)

        with mock.patch.object(optix_runtime, "_load_optix_library", return_value=object()):
            with mock.patch.object(optix_runtime, "_find_optional_backend_symbol", return_value=None):
                with self.assertRaisesRegex(RuntimeError, "does not export"):
                    optix_runtime.collect_active_query_status_stream_3d_optix(
                        query_coords=query_coords,
                        query_point_ids=query_ids,
                        cell_ids=cell_ids,
                        point_begin_offsets=begins,
                        point_counts=counts,
                        cell_mbr_min=mins,
                        cell_mbr_max=maxs,
                        radius=10.0,
                        current_best_distances=best,
                        current_best_item_ids=best_ids,
                        max_inline_points=0,
                        row_capacity=4,
                    )

    def test_current_source_does_not_promote_v7_to_lb_parity(self) -> None:
        from rtdsl import optix_runtime

        source = inspect.getsource(optix_runtime.collect_active_query_status_stream_3d_optix)
        lowered = source.lower()
        self.assertIn("application option implementation", lowered)
        self.assertIn("not a row/hash parity claim", lowered)
        self.assertIn("not a paper performance claim", lowered)

    def test_pod_smoke_script_keeps_claim_boundary_narrow(self) -> None:
        source = SMOKE_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("native_v7_status_stream_smoke_passed", source)
        for field in (
            '"explicit_lb_support_claimed": False',
            '"row_count_parity_claimed": False',
            '"hash_sample_parity_claimed": False',
            '"figure7_reproduction_claimed": False',
            '"figure11_reproduction_claimed": False',
            '"full_xhd_paper_reproduction_claimed": False',
        ):
            self.assertIn(field, source)

    def test_pod_smoke_artifact_records_v7_symbol_without_lb_claim(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal5397")
        self.assertEqual(payload["status"], "native_v7_status_stream_smoke_passed")
        self.assertTrue(payload["matched"])
        metadata = payload["native_result_metadata"]
        self.assertEqual(
            metadata["native_generic_symbol"],
            "rtdl_optix_collect_active_query_status_stream_3d_v1",
        )
        self.assertEqual(metadata["contract"], "generic_active_query_status_stream_native_abi_v1")
        self.assertEqual(metadata["valid_count"], 4)
        self.assertEqual(payload["observed"]["status_codes"], [2])
        boundary = payload["claim_boundary"]
        self.assertTrue(boundary["native_v7_symbol_smoke_claimed"])
        for key in (
            "explicit_lb_support_claimed",
            "row_count_parity_claimed",
            "hash_sample_parity_claimed",
            "figure7_reproduction_claimed",
            "figure11_reproduction_claimed",
            "full_xhd_paper_reproduction_claimed",
        ):
            self.assertIs(boundary[key], False, key)


if __name__ == "__main__":
    unittest.main()
