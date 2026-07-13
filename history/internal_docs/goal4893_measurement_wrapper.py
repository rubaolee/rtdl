#!/usr/bin/env python3
from __future__ import annotations

import ctypes
import importlib.util
import json
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


def _read_pip_work_count(locator) -> int | None:
    library = getattr(locator, "library", None)
    if library is None and hasattr(locator, "prepared"):
        library = getattr(locator.prepared, "library", None)
    if library is None:
        return None
    symbol = getattr(library, "rtdl_optix_rayjoin_cdb_point_location_get_last_work_count", None)
    if symbol is None:
        return None
    symbol.argtypes = (ctypes.POINTER(ctypes.c_size_t),)
    symbol.restype = ctypes.c_int
    value = ctypes.c_size_t(0)
    status = symbol(ctypes.byref(value))
    if status != 0:
        return None
    return int(value.value)


def main() -> None:
    wrapped = _load_module(WRAPPED, "goal4890_wrapped_goal4886")
    base = wrapped.base

    import rtdsl.optix_runtime as optix_runtime

    original_lsi_run_raw = optix_runtime.PreparedOptixPlanarMapLsi2D.run_raw
    original_lsi_run_pair_id_rows = getattr(
        optix_runtime.PreparedOptixPlanarMapLsi2D,
        "run_pair_id_rows",
        None,
    )

    def _record_lsi_measurement(route: str, result, prepared):
        timings = prepared.last_phase_timings() or {}
        measurements["lsi"].append(
            {
                "route": route,
                "raw_candidate_count": int(timings.get("raw_candidate_count", -1)),
                "emitted_count": int(timings.get("emitted_count", -1)),
                "mode": str(timings.get("mode", "")),
                "candidate_count_sec": float(timings.get("candidate_count_pass", 0.0)),
                "candidate_write_sec": float(timings.get("candidate_write_pass", 0.0)),
                "candidate_download_sec": float(timings.get("candidate_download", 0.0)),
                "exact_refine_sec": float(timings.get("exact_refine", 0.0)),
            }
        )
        return result

    def measured_lsi_run_raw(self, left_segments):
        result = original_lsi_run_raw(self, left_segments)
        return _record_lsi_measurement(
            "PreparedOptixPlanarMapLsi2D.run_raw",
            result,
            self.prepared,
        )

    def measured_lsi_run_pair_id_rows(self, left_segments):
        if original_lsi_run_pair_id_rows is None:
            raise RuntimeError("run_pair_id_rows is not available in this RTDL checkout")
        result = original_lsi_run_pair_id_rows(self, left_segments)
        return _record_lsi_measurement(
            "PreparedOptixPlanarMapLsi2D.run_pair_id_rows",
            result,
            self.prepared,
        )

    optix_runtime.PreparedOptixPlanarMapLsi2D.run_raw = measured_lsi_run_raw
    if original_lsi_run_pair_id_rows is not None:
        optix_runtime.PreparedOptixPlanarMapLsi2D.run_pair_id_rows = measured_lsi_run_pair_id_rows

    original_run_point_location = base.run_point_location

    def measured_run_point_location(locator, points, point_count: int):
        result = original_run_point_location(locator, points, point_count)
        timings = locator.last_phase_timings() or {}
        measurements["pip"].append(
            {
                "route": "PreparedOptixPlanarMapPointLocation2D.run_raw",
                "mode": str(timings.get("mode", "")),
                "point_count": int(timings.get("point_count", point_count)),
                "positive_face_count": int(timings.get("positive_face_count", -1)),
                "raw_candidate_count": int(_read_pip_work_count(locator) or -1),
                "traversal_sec": float(timings.get("traversal", 0.0)),
                "row_download_sec": float(timings.get("row_download", 0.0)),
                "point_upload_sec": float(timings.get("point_upload", 0.0)),
            }
        )
        return result

    base.run_point_location = measured_run_point_location
    wrapped.main()

    summary_path = None
    for index, value in enumerate(sys.argv[1:]):
        if value == "--summary" and index + 2 <= len(sys.argv[1:]):
            summary_path = Path(sys.argv[1:][index + 1])
            break
        if value.startswith("--summary="):
            summary_path = Path(value.split("=", 1)[1])
            break
    if summary_path is not None and summary_path.exists():
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
        payload["goal4890_work_counts"] = measurements
        summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps({"goal4890_work_counts": measurements}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
