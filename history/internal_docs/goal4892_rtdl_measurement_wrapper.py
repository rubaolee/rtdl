#!/usr/bin/env python3
from __future__ import annotations

import ctypes
import importlib.util
import json
import os
import sys
from pathlib import Path


THIS_DIR = Path("/workspace/goal4886_numba_au")
WRAPPED = THIS_DIR / "goal4886_section57_public_primitives_overlay_numba_harness.py"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


measurements: dict[str, list[dict[str, int | float | str]]] = {
    "lsi": [],
    "pip": [],
}


def _read_pip_work_counts(locator) -> tuple[int | None, int | None]:
    library = getattr(locator, "library", None)
    if library is None and hasattr(locator, "prepared"):
        library = getattr(locator.prepared, "library", None)
    if library is None:
        return None, None
    symbol = getattr(
        library,
        "rtdl_optix_directed_segment_point_location_get_last_work_counts",
        None,
    )
    if symbol is None:
        symbol = getattr(
            library,
            "rtdl_optix_rayjoin_cdb_point_location_get_last_work_counts",
            None,
        )
    if symbol is None:
        return None, None
    symbol.argtypes = (ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t))
    symbol.restype = ctypes.c_int
    candidate = ctypes.c_size_t(0)
    pruned = ctypes.c_size_t(0)
    status = symbol(ctypes.byref(candidate), ctypes.byref(pruned))
    if status != 0:
        return None, None
    return int(candidate.value), int(pruned.value)


def _summary_arg() -> Path | None:
    args = sys.argv[1:]
    for index, value in enumerate(args):
        if value == "--summary" and index + 1 < len(args):
            return Path(args[index + 1])
        if value.startswith("--summary="):
            return Path(value.split("=", 1)[1])
    return None


def main() -> None:
    os.environ["RTDL_OPTIX_POINT_LOCATION_DIAGNOSTICS"] = "1"
    wrapped = _load_module(WRAPPED, "goal4892_wrapped_goal4886")
    base = wrapped.base

    import rtdsl.optix_runtime as optix_runtime

    original_lsi_run_raw = optix_runtime.PreparedOptixPlanarMapLsi2D.run_raw

    def measured_lsi_run_raw(self, left_segments):
        result = original_lsi_run_raw(self, left_segments)
        timings = self.prepared.last_phase_timings() or {}
        measurements["lsi"].append(
            {
                "route": "PreparedOptixPlanarMapLsi2D.run_raw",
                "raw_candidate_count": int(timings.get("raw_candidate_count", -1)),
                "emitted_count": int(timings.get("emitted_count", -1)),
                "mode": str(timings.get("mode", "")),
                "candidate_count_sec": float(timings.get("candidate_count", 0.0)),
                "candidate_write_sec": float(timings.get("candidate_write", 0.0)),
                "candidate_download_sec": float(timings.get("candidate_download", 0.0)),
                "exact_refine_sec": float(timings.get("exact_refine", 0.0)),
            }
        )
        return result

    optix_runtime.PreparedOptixPlanarMapLsi2D.run_raw = measured_lsi_run_raw

    original_run_point_location = base.run_point_location

    def measured_run_point_location(locator, points, point_count: int):
        result = original_run_point_location(locator, points, point_count)
        timings = locator.last_phase_timings() or {}
        candidate_count, pruned_count = _read_pip_work_counts(locator)
        measurements["pip"].append(
            {
                "route": "PreparedOptixPlanarMapPointLocation2D.run_raw",
                "mode": str(timings.get("mode", "")),
                "point_count": int(timings.get("point_count", point_count)),
                "positive_face_count": int(timings.get("positive_face_count", -1)),
                "candidate_segment_count_after_prune": int(candidate_count or -1),
                "pruned_segment_count": int(pruned_count or -1),
                "traversal_sec": float(timings.get("traversal", 0.0)),
                "row_download_sec": float(timings.get("row_download", 0.0)),
                "point_upload_sec": float(timings.get("point_upload", 0.0)),
            }
        )
        return result

    base.run_point_location = measured_run_point_location
    wrapped.main()

    summary_path = _summary_arg()
    if summary_path is not None and summary_path.exists():
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
        payload["goal4892_work_counts"] = measurements
        summary_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True, default=str),
            encoding="utf-8",
        )
    print(json.dumps({"goal4892_work_counts": measurements}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
