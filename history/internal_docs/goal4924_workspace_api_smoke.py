#!/usr/bin/env python3
"""Run Goal4924 through the Goal4914 workspace-hot smoke harness."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


THIS_DIR = Path(__file__).resolve().parent
GOAL4914 = THIS_DIR / "goal4914_workspace_api_smoke.py"
GOAL4924 = THIS_DIR / "goal4924_columnar_reprojection_sort_probe.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    runner = _load(GOAL4914, "goal4914_workspace_api_smoke_for_goal4924")
    runner.NUMBA_WRAPPER = GOAL4924

    def install_goal4924(wrapper) -> None:
        base = wrapper.base
        base.intersection_rows_from_pairs = wrapper.intersection_rows_from_pairs_no_fraction
        base.sort_xsects_for_map = wrapper.sort_xsects_for_map_goal4924
        base.midpoint_points = wrapper.midpoint_points_numba_enabled
        base.dedupe_point_pairs = wrapper.dedupe_point_pairs_numba_enabled
        base.write_output_chains_streaming = wrapper.write_output_chains_streaming_numba_skip

    runner._install_numba_app_continuation = install_goal4924
    runner.main()


if __name__ == "__main__":
    main()
