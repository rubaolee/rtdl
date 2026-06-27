from __future__ import annotations

import ctypes
import os
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_rt_barneshut_native_route import (  # noqa: E402
    V4_RT_BARNESHUT_NATIVE_AUTHOR_REQUIRED_SYMBOLS,
    V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_HOST_FALLBACK_AVAILABLE,
    V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_RT_CORE_CANDIDATE_AVAILABLE,
    V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_SYMBOLS_PRESENT_UNVALIDATED,
    V4RtBarnesHutNativeRouteUnavailable,
    inspect_v4_rt_barneshut_native_feasibility,
    run_v4_rt_barneshut_native_author_route,
    validate_v4_rt_barneshut_native_feasibility,
)


PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"


def _optix_library_path() -> Path | None:
    env = os.environ.get("RTDL_OPTIX_LIB") or os.environ.get("RTDL_OPTIX_LIBRARY")
    if env:
        return Path(env)
    candidate = ROOT / "build" / ("librtdl_optix.dylib" if sys.platform == "darwin" else "librtdl_optix.so")
    return candidate if candidate.exists() else None


class V4Goal4763RtBarnesHutNativeAbiFirstSliceTest(unittest.TestCase):
    def test_source_tree_exposes_3d_author_abi_symbols(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")

        self.assertIn("struct RtdlRtBarnesHutAuthor3DOutput", prelude)
        self.assertIn("struct RtBarnesHutAuthorPrepared3D", api)
        for symbol in V4_RT_BARNESHUT_NATIVE_AUTHOR_REQUIRED_SYMBOLS:
            self.assertIn(symbol, prelude)
            self.assertIn(symbol, api)

    def test_feasibility_status_moves_to_symbols_present_but_unvalidated(self) -> None:
        feasibility = inspect_v4_rt_barneshut_native_feasibility(ROOT)
        validate_v4_rt_barneshut_native_feasibility(feasibility)

        self.assertIn(
            feasibility.status,
            {
                V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_SYMBOLS_PRESENT_UNVALIDATED,
                V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_HOST_FALLBACK_AVAILABLE,
                V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_RT_CORE_CANDIDATE_AVAILABLE,
            },
        )
        self.assertEqual((), feasibility.missing_native_author_symbols)
        self.assertTrue(feasibility.claim_boundary["native_v4_abi_symbols_available"])
        self.assertFalse(feasibility.claim_boundary["native_v4_operator_available"])
        self.assertFalse(feasibility.claim_boundary["public_rt_barneshut_paper_reproduction_claim_authorized"])
        self.assertFalse(feasibility.claim_boundary["v2_v3_v4_author_speed_table_authorized"])

    def test_python_route_still_fails_closed_until_traversal_is_validated(self) -> None:
        with self.assertRaises(V4RtBarnesHutNativeRouteUnavailable) as raised:
            run_v4_rt_barneshut_native_author_route()

        self.assertIn("requires explicit CUDA device column pointers", str(raised.exception))

    def test_rebuilt_native_library_exports_first_slice_symbols_when_available(self) -> None:
        library = _optix_library_path()
        if library is None or not library.exists():
            self.skipTest("rebuilt librtdl_optix is not available in this environment")

        loaded = ctypes.CDLL(str(library))
        for symbol in V4_RT_BARNESHUT_NATIVE_AUTHOR_REQUIRED_SYMBOLS:
            self.assertTrue(hasattr(loaded, symbol), f"missing exported symbol: {symbol}")


if __name__ == "__main__":
    unittest.main()
